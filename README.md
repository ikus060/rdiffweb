rdiffweb
========
Release under GPLv3

# Installation
ref.: http://www.rdiffweb.org/wiki/index.php?title=Installation

To install rdifWeb, you need to install the the prerequisites. On Debian distribution you may proceed as follow.

    sudo apt-get install python-cherrypy3 python-pysqlite2 libsqlite3-dev python-jinja2

Then you may download a snapshot of the repository and proceed with the installation on your system.

    wget --no-check-certificate -O ikus060-rdiffweb.tar.gz https://github.com/ikus060/rdiffweb/archive/v0.6.5.tar.gz
    tar zxf ikus060-rdiffweb.tar.gz
    cd rdiffweb-*
    python setup.py build
    sudo python setup.py install
  
Configure rdiffweb using the command line tool. Then follow the instruction.

    sudo rdiffweb-config
    
Then stat rdiffweb server using this command line.

    sudo /etc/init.d/rdiffweb start

By default, the web server is listening on port 8080 and is accessible via the following URL.

    http://server_name:8080
    

## Installing Grunt
To install Grunt, you must first download and install node.js (which includes npm).
npm stands for node packaged modules and is a way to manage development dependencies
through node.js.

Then, from the command line:
1. Install grunt-cli globally with npm install -g grunt-cli.
2. Navigate to the root /bootstrap/ directory, then run npm install. npm will look at
   the package.json file and automatically install the necessary local dependencies listed there.
When completed, you'll be able to run the various Grunt commands provided from the command line.

## Available Grunt commands
### grunt dist (Just compile CSS and JavaScript)
Regenerates the /dist/ directory with compiled and minified CSS and JavaScript files. As a Bootstrap user, this is normally the command you want.

### grunt watch (Watch)
Watches the Less source files and automatically recompiles them to CSS whenever you save a change.

### grunt (Build absolutely everything and run tests)
Compiles and minifies CSS and JavaScript, builds the documentation website, runs the HTML5 validator against the docs, regenerates the Customizer assets, and more. Usually only necessary if you're hacking on Bootstrap itself.
