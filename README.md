rdiffweb
========
Release under GPLv3

# Installation
ref.: http://www.rdiffweb.org/wiki/index.php?title=Installation

To install rdifWeb, you need to install the the prerequisites. On Debian distribution you may proceed as follow.

    sudo apt-get install python-cherrypy3 python-pysqlite2 libsqlite3-dev python-jinja2 python-setuptools

Then you may download a snapshot of the repository and proceed with the installation on your system.

    wget --no-check-certificate -O rdiffweb.tar.gz https://github.com/ikus060/rdiffweb/archive/develop.tar.gz
    tar zxf rdiffweb.tar.gz
    cd rdiffweb-*
    python setup.py build
    sudo python setup.py install
  
Start rdiffweb server using this command line.

    sudo /etc/init.d/rdiffweb start
    
Proceeding with the setup will initialise your database by creating a default admin user with the following username and password:
 * username : admin
 * password : admin123
  
Configure rdiffweb using web interface.

	http://localhost:8080/setup

By default, the web server is listening on port 8080 and is accessible via the following URL.

    http://server_name:8080
    
