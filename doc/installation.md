
# Installation

Three different solutions are available to install Rdiffweb.
You should pick the right solution depending on your operating system and your
deployment environment.

## System requirements

We recommend using high quality server hardware when running Rdiffweb in production, mainly for storage.

### Minimum server requirement for evaluation

These minimum requirements are solely for evaluation and shall not be used in a production environment :

* Cpu 64bit x86-64 or amd64, 2 core
* Memory : 2 GiB RAM
* Hard drive/storage more than 8 GiB

### Recommended server requirement

* Cpu: 64bit x86-64 or amd64, 4 core
* Memory: minimum 4 GiB
* Storage: consider the storage according to your backup needs. A couple of terabytes should be considered for the long term. Ideally, you should consider hardware or ZFS raid for your storage. If you plan to support user quota, make sure that your file system supports it. E.g. ext4 and ZFS. Other file systems might not be well supported.
* Temporary storage: Rdiffweb requires a temporary storage location that is used during the restoration process. This location should be greater than 8gb. This temporary storage will be closer to the web application. Ideally, it should be in ram using tmpfs.

## Option 1. Debian/Ubuntu repository

If you are running a Debian-based system, you should use `apt` to install Rdiffweb.

The following Debian Release as supported: Bullseye (11), Bookworm (12)

The following Ubuntu Release are supported: Jammy (22.04 LTS), Noble (24.04 LTS) and Oracular (24.10)

    apt install lsb-release
    curl -L https://www.ikus-soft.com/archive/rdiffweb/public.key | gpg --dearmor > /usr/share/keyrings/rdiffweb-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/rdiffweb-keyring.gpg] https://nexus.ikus-soft.com/repository/apt-release-$(lsb_release -sc)/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/rdiffweb.list
    apt update
    apt install rdiffweb

> **_NOTE:_**  Access the web interface `http://<ip-or-dns-name>:8080` with username  **admin** and password **admin123**. Then browse to the **Admin Area** to add users and assign backup locations to these users.

## Option 2. PyPi repository

If you are not running a Debian-based system, use `pip` to install Rdiffweb.
Using pip to install Rdiffweb has its disadvantages. Extra steps are required: creating a service unit, a directory structure, and a default config file.

**RedHat/CentOS/Rocky Linux/AlmaLinux 8 (or newer):**

```
sudo dnf update
sudo dnf install epel-release
sudo /usr/bin/crb enable
sudo dnf install rdiff-backup openssh-server python312
sudo bash -c 'cd /opt && python3.12 -m venv rdiffweb && source /opt/rdiffweb/bin/activate && pip install -U rdiffweb'
sudo mkdir -p /var/lib/rdiffweb/session
```
By default Rdiffweb is looking for a configuration file located at `/etc/rdiffweb/rdw.conf`.

Create a default configuration file:

    sudo mkdir /etc/rdiffweb 
    sudo curl -L https://gitlab.com/ikus-soft/rdiffweb/-/raw/master/rdw.conf -o /etc/rdiffweb/rdw.conf

If needed, create a service unit to start Rdiffweb on reboot:

    sudo curl -L https://gitlab.com/ikus-soft/rdiffweb/-/raw/master/extras/systemd/rdiffweb.service -o /etc/systemd/system/rdiffweb.service
    sudo ln -s /opt/rdiffweb/bin/rdiffweb /usr/local/bin/rdiffweb
    
    sudo systemctl enable --now sshd
    sudo systemctl enable --now rdiffweb



> **_NOTE:_**  Access the web interface `http://<ip-or-dns-name>:8080` with username  **admin** and password **admin123**. Then browse to the **Admin Area** to add users and assign backup locations to these users.

## Option 3. Docker

If you are already familiar with Docker, we recommend you to deploy Rdiffweb using our official Docker image.

Official container image: `ikus060/rdiffweb` ![Docker Pull Count](https://img.shields.io/docker/pulls/ikus060/rdiffweb.svg)

> **_NOTE:_**  Rdiffweb Docker image doesn't start an SSH daemon. You may use the SSH Server from the physical host or start another container with SSH and Rdiff-backup.

**Using Docker command line interface:**

Starting Rdiffweb in Docker is simple:

    docker run -d \
     --publish 8080:8080 \
     --name rdiffweb \
     -e RDIFFWEB_TEMPDIR=/restores \
     -e RDIFFWEB_DISABLE_SSH_KEYS=1 \
     --volume /path/to/rdiffweb/backups:/backups \
     --volume /path/to/rdiffweb/config:/etc/rdiffweb \
     --volume /path/to/rdiffweb/session:/var/lib/rdiffweb/session \
     --volume /path/to/rdiffweb/restores:/restores \
     --restart=unless-stopped \
     ikus060/rdiffweb

You may configure Rdiffweb settings using environment variables `RDIFFWEB_*`. Read more about all the configuration options in the [configuration section](configuration).

**Using Docker Compose:**

Create a `docker-compose.yml` file with the following contents:

    version: "3.5"
    services:
      rdiffweb:
        image: ikus060/rdiffweb
        container_name: rdiffweb
        ports:
          - 8080:8080
        volumes:
          - /path/to/rdiffweb/backups:/backups
          - /path/to/rdiffweb/config:/etc/rdiffweb
          - /path/to/rdiffweb/restores:/restores
        restart: "unless-stopped"
        environment:
          - RDIFFWEB_TEMPDIR=/restores
          - RDIFFWEB_DISABLE_SSH_KEYS=1

Then while in the same folder as the `docker-compose.yml` run:

    docker-compose up

To run the container in background add `-d` to the above command.

> **_NOTE:_**  Access the web interface `http://<ip-or-dns-name>:8080` with username  **admin** and password **admin123**. Then browse to the **Admin Area** to add users and assign backup locations to these users.
