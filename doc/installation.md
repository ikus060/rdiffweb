# Rdiffweb Installation

You may install rdiffweb in various ways. It's recommended to install rdiffweb
from Pypi repository. It's the official supported way to install rdiffweb.

To install rdiffweb from pypi, you need to install `pip` and other dependencies:

    sudo apt-get install python-dev python-pysqlite2 libldap2-dev libsasl2-dev rdiff-backup build-essential
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
