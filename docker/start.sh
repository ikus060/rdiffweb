#!/bin/bash
set -e

KEY_DIR="/etc/minarca"
LOG_DIR="/var/log/minarca"
BACKUP_DIR="/backups"
export MINARCA_MINARCA_REMOTE_HOST_IDENTITY="$KEY_DIR"


echo "Verifying unprivileged user namespace support..."
su nobody -s /bin/sh -c "unshare --user --net" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "=================================================================="
    echo "Error: Unprivileged user namespaces are blocked for non-root users."
    echo "Your system might be running inside an LXC container or another restricted environment."
    echo "Read Minarca Server documentation to learn more about how to enabled this feature."
    echo "=================================================================="
    exit 1
fi


#change ownership of log dir
echo "Set correct permissions for log, conf and backup dir..."
chown -R minarca: $LOG_DIR $KEY_DIR $BACKUP_DIR

# RSA key
if [ ! -f "$KEY_DIR/ssh_host_rsa_key" ]; then
    echo "Generating RSA key..."
    ssh-keygen -t rsa -b 4096 -f "$KEY_DIR/ssh_host_rsa_key" -N ""
fi

# ECDSA key
if [ ! -f "$KEY_DIR/ssh_host_ecdsa_key" ]; then
    echo "Generating ECDSA key..."
    ssh-keygen -t ecdsa -b 521 -f "$KEY_DIR/ssh_host_ecdsa_key" -N ""
fi

# ED25519 key
if [ ! -f "$KEY_DIR/ssh_host_ed25519_key" ]; then
    echo "Generating ED25519 key..."
    ssh-keygen -t ed25519 -f "$KEY_DIR/ssh_host_ed25519_key" -N ""
fi

SHELL_LOG_FILE="/var/log/minarca/shell.log"
# Create shell.log file if not exists
if [ ! -f "$SHELL_LOG_FILE" ]; then
    echo "Creating shell.log file..."
    touch $SHELL_LOG_FILE
    chown minarca $SHELL_LOG_FILE
fi

# Start the OpenSSH server
echo "Starting OpenSSH service..."
/usr/sbin/sshd \
    -E /var/log/minarca/sshd.log \
    -o HostKey=$KEY_DIR/ssh_host_rsa_key \
    -o HostKey=$KEY_DIR/ssh_host_ecdsa_key \
    -o HostKey=$KEY_DIR/ssh_host_ed25519_key \
    -o AcceptEnv=TERM \
    -o AllowAgentForwarding=no \
    -o DebianBanner=no \
    -o LoginGraceTime=1m \
    -o MaxAuthTries=3 \
    -o PermitRootLogin=no \
    -o PasswordAuthentication=no \
    -o AllowUsers=minarca

# Start the Minarca service
echo "Starting Minarca service..."
su -c - minarca /opt/minarca-server/minarca-server "$@" &

# Get the PID of the Python service
PYTHON_PID=$!

# Function to stop both services
stop_services() {
    echo "Stopping services..."
    kill $PYTHON_PID
    pkill sshd
    exit 0
}

# Trap SIGTERM and SIGINT to gracefully stop services
trap 'stop_services' SIGTERM SIGINT

# Wait for the Python service to exit
wait $PYTHON_PID

# Stop SSHD if Python service exits
stop_services
