rdiffweb
========
Release under GPLv3

# Installation

To install rdiffweb, you need to install the the prerequisites. On Debian distribution you may proceed as follow:

    sudo apt-get install python-cherrypy3 python python-pysqlite2 libsqlite3-dev python-jinja2 python-setuptools python-babel rdiff-backup 

Then you may download a snapshot of the repository and proceed with the installation on your system.

    wget --no-check-certificate -O rdiffweb.tar.gz https://github.com/ikus060/rdiffweb/archive/master.tar.gz
    tar zxf rdiffweb.tar.gz
    cd rdiffweb-*
    sudo python setup.py install
    
If it's the frist time you are installing rdiffweb on the system, you will need to manually copy `rdw.conf` to `/etc/rdiffweb`:

    sudo mkdir -p /etc/rdiffweb
    sudo cp rdw.conf /etc/rdiffweb/
   
You may also need to create an init script to startup rdiffweb on reboot. One is provided for Debian 7 (Wheezy):

    sudo cp extras/init/rdiffweb /etc/init.d/
    sudo chmod +x  /etc/init.d/rdiffweb
    sudo update-rc.d rdiffweb defaults
    sudo /etc/init.d/rdiffweb start

On Debian 8 (Jessie) you need to create systemd file. The following was provided by contributors:

    sudo cp extras/systemd/rdiffweb.service /etc/systemd/system/
    sudo service rdiffweb start

By default, the web server is listening on port 8080 and is accessible via the following URL.

    http://server_name:8080

On First start, you should access rdiffweb using default crendentials:
 * username : admin
 * password : admin123

Translation
===========
Reference http://babel.edgewall.org/wiki/Documentation/setup.html

rdiffweb may be translated. This section describe briefly how to translate
rdiffweb. It's not a complete instruction set, it's merely a reminder.

Extract the strings to be translated.

	./setup.py extract_messages --output-file rdiffweb/locales/messages.pot

	./setup.py compile_catalog --directory rdiffweb/locales --locale fr

