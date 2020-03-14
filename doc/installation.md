# Rdiffweb Installation

# Install rdiffweb on Linux

You may install rdiffweb in various ways. It's recommended to install rdiffweb
from pypi repository. It's the official supported way to install rdiffweb as of
now until a PPA is provided.

To install rdiffweb from pypi, you need to install `pip`, `rdiff-backup` other dependencies:

**Ubuntu/Debian:**

    sudo apt update
    sudo apt install python-dev libldap2-dev libsasl2-dev rdiff-backup build-essential curl
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    sudo python get-pip.py
    
**RedHat7/CentOS7:**

    sudo yum install epel-release
    sudo yum install python3-devel openldap-devel rdiff-backup gcc
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    sudo python3 get-pip.py
    
**RedHat8/CentOS8:**
*Note: rdiff-backup is not provided by RedHat or CentOS repo. You must install a beta release from pypi*

    sudo yum install epel-release
    sudo yum install python3-devel openldap-devel gcc
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    sudo python3 get-pip.py
    sudo pip install --pre rdiff-backup

Then you may install rdiffweb using `pip`:

    sudo pip3 install rdiffweb

Install default configuration file.

    sudo mkdir -p /etc/rdiffweb 
    sudo curl https://github.com/ikus060/rdiffweb/raw/master/rdw.conf -o /etc/rdiffweb/rdw.conf
    
If needed, create a service unit to manage rdiffweb as a service:

    sudo curl https://raw.githubusercontent.com/ikus060/rdiffweb/master/extras/systemd/rdiffweb.service -o /etc/systemd/system/rdiffweb.service
    sudo systemctl daemon-reload
    sudo service rdiffweb start

By default, the web server is listening on port 8080 and is accessible via the following URL.

    http://127.0.0.1:8080

On first start, you should access rdiffweb using default credentials:
 * username : admin
 * password : admin123
