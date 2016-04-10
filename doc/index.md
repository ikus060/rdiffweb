# Installation

## Instructions

To install rdiffweb, you need to install the the prerequisites. On Debian distribution you may proceed as follow:

    sudo apt-get install python-cherrypy3 python2 python-pysqlite2 libsqlite3-dev python-jinja2 python-setuptools python-babel rdiff-backup 

Then you may download a snapshot of the repository and proceed with the installation on your system.

    wget --no-check-certificate -O rdiffweb.tar.gz https://github.com/ikus060/rdiffweb/archive/master.tar.gz
    tar zxf rdiffweb.tar.gz
    cd rdiffweb-*
    sudo python setup.py install
    
If it's the first time you are installing rdiffweb on the system, you will need to manually copy `rdw.conf` to `/etc/rdiffweb`:

    sudo cp rdw.conf /etc/rdiffweb
   
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

On first start, you should access rdiffweb using default credentials:
 * username : admin
 * password : admin123

## Configure Apache (optional)

You may need an Apache server in case:
 
 * you need to serve multiple web services from the same IP;
 * you need more security (like HTTP + SSL).
 
This section doesn't explain how to install and configure your Apache server.
This is out-of-scope. The following is only provided as a suggestion and is in
no way a complete reference.
 
** Install Apache and required modules**

    sudo apt-get install apache2
    sudo a2enmod rewrite
    sudo a2enmod proxy
    sudo a2enmod ssl
    sudo a2enmod proxy_http
    
**Basic configuration**

Add the following to your Apache configuration. It's recommended to create a 
file in /etc/apache2/sites-available/rdiffweb.

    <VirtualHost *:80>
        ServerName rdiffweb.mydomain.com
        ProxyPass / http://localhost:8080/ retry=5
        ProxyPassReverse / http://localhost:8080/
    </VirtualHost>

**SSL configuration**

    <VirtualHost *:80>
        ServerName rdiffweb.mydomain.com
        ServerAdmin me@mydomain.com
        # TODO Redirect HTTP to HTTPS
        RewriteEngine on
        RewriteRule ^(.*)$ https://rdiffweb.mydomain.com$1 [L,R=301]
        <Location />
            Order Allow,deny
            Allow from all
        </Location>
    </VirtualHost>
    
    <VirtualHost *:443>
        ServerName rdiffweb.mydomain.com
        ServerAdmin me@mydomain.com
    
        # Hostaname resolution in /etc/hosts
        ProxyPass / http://localhost:8080/ retry=5
        ProxyPassReverse / http://localhost:8080/
    
        # SSL Configuration
        SSLEngine on
        SSLCertificateFile    /etc/apache2/ssl/my_certificate.crt
        SSLCertificateKeyFile /etc/apache2/ssl/my_certificate.key
        <Location />
            Order Allow,deny
            Allow from all
        </Location>
    </VirtualHost>
    
# Configuration

# Configure email notifications

Since rdiffweb v0.9, you may setup rdiffweb to notify you when you backup did
not complete for some period of time. This is useful to know when you backup
setup is broken. This section describes how to configure rdiffweb to notify you.

**Edit config file**
Edit rdiffweb config file `/etc/rdiffweb/rdw.conf` and edit the `Email*`
configuration parameters to suit your environment. The following is an example
using a gmail account to sent notification.

    #----- Enable Email Notification
    # The server can be configured to email user when their repositories have not
    # been backed up for a user-specified period of time. To enable this feature,
    # set below settings to correct values.
    EmailNotificationEnabled=true
    EmailNotificationTime=6:30
    EmailHost=smtp.gmail.com:587
    EmailEncryption=starttls
    EmailSender=example@gmail.com
    EmailUsername=example@gmail.com
    EmailPassword=CHANGEME

**Restart rdiffweb**

To take the modification in consideration, restart rdiffweb as follow:

    sudo service rdiffweb restart
    
**Edit your preferences**

Login to rdiffweb using your username & password. Browse to your user settings.
A new tab named "Notification" you be displayed. Click on it to change the
notification settings for each repository.

# Development

This section provide some details for those who want to contributes. 
  
## Translation
Reference http://babel.edgewall.org/wiki/Documentation/setup.html

rdiffweb may be translated. This section describe briefly how to translate
rdiffweb. It's not a complete instruction set, it's merely a reminder.

Extract the strings to be translated.

    ./setup.py extract_messages --output-file rdiffweb/locales/messages.pot

    ./setup.py compile_catalog --directory rdiffweb/locales --locale fr

## Tests

Rdiffweb is provided with unit tests and integration test. To run the tests,
you may run it as follow for your current python version:

    python setup.py. nosetests

## Profiling

Since v0.9, you may profile rdiffweb by calling it with `--profile`.

    rdiffweb --debug --profile
    
Profiling file will be generated into `/tmp` unless you call rdiffweb
with `--profile-path`. You may visualize the data with:

    snakeviz rdiffweb_0001.prof
    
