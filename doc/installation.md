# Installation

## System requirements

We recommend using high quality server hardware when running Rdiffweb in production, mainly for storage.

### minimum server requirement for evaluation

These minimum requirements are solely for evaluation and shall not be used in a production environment :

* Cpu 64bit x86-64 or amd64, 2 core
* Memory : 2 GiB RAM
* Hard drive/storage more than 8 GiB

### recommended server requirement

* Cpu: 64bit x86-64 or amd64, 4 core
* Memory: minimum 4 GiB
* Storage: consider the storage according to your backup needs. A couple of terabytes should be considered for the long term. Ideally, you should consider hardware or ZFS raid for your storage. If you plan to support user quota, make sure that your file system supports it. E.g. ext4 and ZFS. Other file systems might not be well supported.
* Temporary storage: Rdiffweb requires a temporary storage location that is used during the restoration process. This location should be greater than 8gb. This temporary storage will be closer to the web application. Ideally, it should be in ram using tmpfs.

## Rdiffweb installation

Two different solutions are available to install Rdiffweb. You should pick the right solution depending on your operating system.

### Debian package repositories

If you are running a Debian-based system, you should use `apt` to install Rdiffweb.

    curl -L https://www.ikus-soft.com/archive/rdiffweb/public.key | apt-key add - 
    echo "deb https://nexus.ikus-soft.com/repository/apt-release-bullseye/ bullseye main" > /etc/apt/sources.list.d/rdiffweb.list
    apt update
    apt install rdiffweb

Note: You can access the web interface with your web browser using HTTP on port 8080. For example go to `http://<ip-or-dns-name>:8080`

### PyPi package repositories

If you are not running a Debian-based system, use `pip` to install Rdiffweb.
Using pip to install Rdiffweb has its disadvantages. Extra steps are required: creating a service unit, a directory structure, and a default config file.

**RedHat/CentOS 7 & 8:**

    sudo yum install epel-release
    sudo yum install python3-devel openldap-devel rdiff-backup gcc python3-pip
    sudo pip install -U rdiffweb

If needed, create a service unit to start Rdiffweb on reboot:

    sudo curl -L https://gitlab.com/ikus-soft/rdiffweb/-/raw/master/extras/systemd/rdiffweb.service -o /etc/systemd/system/rdiffweb.service
    sudo systemctl daemon-reload
    sudo service rdiffweb start

By default Rdiffweb is looking for a configuration file located at `/etc/rdiffweb/rdw.conf`.

Create a default configuration file:

    sudo mkdir -p /etc/rdiffweb 
    sudo curl -L https://gitlab.com/ikus-soft/rdiffweb/-/raw/master/rdw.conf -o /etc/rdiffweb/rdw.conf

Note: You can access the web interface with your web browser,using HTTP on port 8080. For example go to `http://<ip-or-dns-name>:8080`
