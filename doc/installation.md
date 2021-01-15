# Rdiffweb Installation

## Install Rdiffweb on Linux

You may install Rdiffweb from Pypi repository:

**RedHat/CentOS 7 & 8:**

    sudo yum install epel-release
    sudo yum install python3-devel openldap-devel rdiff-backup gcc python3-pip
    sudo pip install -U rdiffweb

**Ubuntu/Debian (from Pypi):**

    sudo apt update
    sudo apt install python-dev libldap2-dev libsasl2-dev rdiff-backup build-essential curl python3-pip
    sudo pip install -U rdiffweb

Since v2.0.0, you may install Rdiffweb from APT Repository

**Debian Bullseye (from APT experimental):**

    curl -L https://www.ikus-soft.com/archive/rdiffweb/public.key | apt-key add - 
    echo "deb https://nexus.ikus-soft.com/repository/apt-release-bullseye/ bullseye main" > /etc/apt/sources.list.d/rdiffweb.list
    apt update
    apt install rdiffweb

## Configure rdiffweb

By default rdiffweb is looking for a configuration at `/etc/rdiffweb/rdw.conf`.
If this file doesn’t exist, rdiffweb refused to start. So let create a default
configuration file.

Install default configuration file.

    sudo mkdir -p /etc/rdiffweb 
    sudo curl -L https://gitlab.com/ikus-soft/rdiffweb/-/raw/master/rdw.conf -o /etc/rdiffweb/rdw.conf
    
If needed, create a service unit to manage rdiffweb as a service:

    sudo curl -L https://gitlab.com/ikus-soft/rdiffweb/-/raw/master/extras/systemd/rdiffweb.service -o /etc/systemd/system/rdiffweb.service
    sudo systemctl daemon-reload
    sudo service rdiffweb start

By default, the web server is listening on port 8080 and is accessible via the following URL.

    http://127.0.0.1:8080

On first start, you should access rdiffweb using default credentials:
 * username : admin
 * password : admin123
