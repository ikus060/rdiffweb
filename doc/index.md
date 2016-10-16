# Installation

You may install rdiffweb in various way. We recommend you to install it from
source as we have more experience doing it this way. Since v0.9.1, you may also
install rdiffweb from pypi.

## Install from source (Recommended)

To install rdiffweb, you need to install the prerequisites. On Debian distribution you may proceed as follow:

    sudo apt-get install python-cherrypy3 python python-pysqlite2 libsqlite3-dev python-jinja2 python-setuptools python-babel rdiff-backup

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

On Debian 8 (Jessie) you need to create systemd file. The following was provided by contributors:

    sudo cp extras/systemd/rdiffweb.service /etc/systemd/system/
    sudo service rdiffweb start

By default, the web server is listening on port 8080 and is accessible via the following URL.

    http://server_name:8080

On first start, you should access rdiffweb using default credentials:
 * username : admin
 * password : admin123

## Install from pypi

You may install rdiffweb from pypi. First you need to install `pip` and other dependencies:

    sudo apt-get install python-pip python-pysqlite2 rdiff-backup
    sudo pip install -U pip

Then you may install rdiffweb using `pip`:
    
    sudo pip install rdiffweb

Install default configuration file.
    
    wget https://github.com/ikus060/rdiffweb/raw/master/rdw.conf
    sudo mkdir -p /etc/rdiffweb
    sudo cp rdw.conf /etc/rdiffweb/

# Configure Apache - Reverse Proxy (optional)

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

Enable the `proxy`module as follow:

    sudo a2enmod proxy
    sudo a2enmod proxy_http

Add the following to your Apache configuration. It's recommended to create a 
file in `/etc/apache2/sites-available/rdiffweb`.

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

# Configure nginx (optional)

You may need an nginx server in case:
 
 * you need to serve multiple web services from the same IP;
 * you need more security (like HTTP + SSL).
 
This section doesn't explain how to install and configure your Nginx server.
This is out-of-scope. The following is only provided as a suggestion and is in
no way a complete reference.

See `/extras/nginx` folder for more examples.

**Reverse proxy configuration**
    
    location /rdiffweb {
        rewrite ^([^\?#]*/)([^\?#\./]+)([\?#].*)?$ $1$2/$3 permanent;
        # substitute with rdiffweb url
        proxy_pass http://127.0.0.1:18080/;
        # for https
        #proxy_redirect      http://example.com https://example.com/rdiffweb;
        proxy_set_header        Host $host;
        proxy_set_header        X-Real-IP $remote_addr;
        proxy_set_header        X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header        X-Forwarded-Proto $scheme;
        proxy_set_header Accept-Encoding "";
        # rewrite internal links
        sub_filter 'href="/' 'href="/rdiffweb/';
        sub_filter 'src="/' 'src="/rdiffweb/';
        sub_filter 'action="/' 'action="/rdiffweb/';
        sub_filter "url(\'/static" "url(\'/rdiffweb/static";
        sub_filter_types "*";
        sub_filter_once off;
    }


# Configuration

## Authentication

Rdiffweb is currently provided with a limited set of plugins for authentication and authorization:
 * SQLite : Embedded database used for authentication, authorization and data storage;
 * LDAP (optional) : Allow users to authenticate with their LDAP password.

### SQLite

To use the embeded database for authentication, make sure you have a section similare to the following in your configuration file `/etc/rdiffweb/rdw.conf`:

    #----- Enable Sqlite DB Authentication.
    SQLiteEnabled=True
    SQLiteDBFile=/etc/rdiffweb/rdw.db

### LDAP

The LDAP plugin can only be used for authentication. To make everything work, you will need to enabled SQLite plugin and LDAP plugin at the same time. LDAP will be used for authentication and SQLite will be used for autorization and data storage.

You may need to install `python-ldap` as follow:

    sudo apt-get install python-ldap

To make LDAP authentication work, you need to enable the plugin and provide information about your environment.

    #----- Enable LDAP Authentication
    LdapEnabled=true

Plugin parameters:

| Parameter | Description | Required | Example |
| --- | --- | --- | --- |
| LdapUri | URIs containing only the schema, the host, and the port fields. | Yes | ldap://localhost:389 | 
| LdapTls | `true` to enable TLS. Default to `false` | No | false |
| LdapProtocolVersion | Version of LDAP in use either 2 or 3. Default to 3. | No | 3 |
| LdapBaseDn | The DN of the branch of the directory where all searches should start from. | Yes | dc=my,dc=domain | 
| LdapBindDn | An optional DN used to bind to the server when searching for entries. If not provided, will use an anonymous bind. | No | cn=manager,dc=my,dc=domain |
| LdapBindPassword |  A bind password to use in conjunction with `LdapBindDn`. Note that the bind password is probably sensitive data, and should be properly protected. You should only use the LdapBindDn and LdapBindPassword if you absolutely need them to search the directory. | No | mypassword |
| LdapAttribute | The attribute to search username. If no attributes are provided, the default is to use `uid`. It's a good idea to choose an attribute that will be unique across all entries in the subtree you will be using. | No | cn | 
| LdapScope | The scope of the search. Can be either `base`, `onelevel` or `subtree`. Default to `subtree`. | No | onelevel |
| LdapFilter | A valid LDAP search filter. If not provided, defaults to `(objectClass=*)`, which will search for all objects in the tree. | No | (objectClass=*) | 
| LdapNetworkTimeout | Optional timeout value. Default to 10 sec. | No | 10 |
| LdapTimeout | Optional timeout value. Default to 300 sec. | No | 300 |
| LdapAllowPasswordChange | `true` to allow LDAP users to  update their password using rdiffweb. This option should only be enabled if the LDAP if confiugred to allow the user to change their own password. Default to  `false`. | No | true |

## Configure email notifications

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

This section provide some details for those who want to contributes to the development.
  
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
    

## Less & CSS(s)

For deployment reason, we need to pre-compile less file into css file.

    python setup.py build_less
    
## Javascript

Any changes to javascript file need to be manually compiled into .min.js.

    python setup.py minify_js
 
    