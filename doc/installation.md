# Rdiffweb Installation

You may install rdiffweb in various ways. It's recommended to install rdiffweb
from Pypi repository. It's the official supported way to install rdiffweb.

## Install from Pypi (Recommended)

To install rdiffweb from pypi, you need to install `pip` and other dependencies:

    sudo apt-get install python-pysqlite2 libldap2-dev libsasl2-dev rdiff-backup
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    sudo python get-pip.py

Then you may install rdiffweb using `pip`:

    sudo pip install rdiffweb

Install default configuration file.

    sudo mkdir -p /etc/rdiffweb 
    wget -O /etc/rdiffweb/rdw.conf https://github.com/ikus060/rdiffweb/raw/master/rdw.conf
    
If needed, create a service unit to manage rdiffweb as a service:

    sudo wget -O /etc/systemd/system/rdiffweb.service https://raw.githubusercontent.com/ikus060/rdiffweb/master/extras/systemd/rdiffweb.service
    sudo systemctl daemon-reload
    sudo service rdiffweb start

By default, the web server is listening on port 8080 and is accessible via the following URL.

    http://127.0.0.1:8080

On first start, you should access rdiffweb using default credentials:
 * username : admin
 * password : admin123

## Install from source

To install rdiffweb, you need to install the prerequisites. On Debian distribution you may proceed as follow:

    sudo apt-get install python python-pysqlite2 libldap2-dev libsasl2-dev rdiff-backup

Then you may download a snapshot of the repository and proceed with the installation on your system.

    wget --no-check-certificate -O rdiffweb.tar.gz https://github.com/ikus060/rdiffweb/archive/master.tar.gz
    tar zxf rdiffweb.tar.gz
    cd rdiffweb-*
    sudo python setup.py install

If it's the first time you are installing rdiffweb on the system, you will need to manually copy `rdw.conf` to `/etc/rdiffweb`:

    sudo mkdir -p /etc/rdiffweb
    sudo cp rdw.conf /etc/rdiffweb/

You may also need to create an init script to startup rdiffweb on reboot. One is provided for Debian 7 (Wheezy):

    sudo cp extras/init/rdiffweb /etc/init.d/
    sudo chmod +x  /etc/init.d/rdiffweb
    sudo update-rc.d rdiffweb defaults
    sudo /etc/init.d/rdiffweb start

On Debian >8 (Jessie, Stretch, Buster) you need to create systemd file. The following was provided by contributors:

    sudo cp extras/systemd/rdiffweb.service /etc/systemd/system/
    sudo service rdiffweb start

By default, the web server is listening on port 8080 and is accessible via the following URL.

    http://127.0.0.1:8080

On first start, you should access rdiffweb using default credentials:
 * username : admin
 * password : admin123