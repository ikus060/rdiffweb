# Networking

## Configure Rdiffweb behind Apache Reverse Proxy

You may need an Apache server in case:

* you need to serve multiple web services from the same IP;
* you need more security (like HTTP + SSL).

This section doesn't explain how to install and configure your Apache server.
This is out-of-scope. The following is only provided as a suggestion and is in
no way a complete reference.

**Install Apache and required modules**

    sudo apt-get install apache2
    sudo a2enmod rewrite
    sudo a2enmod proxy
    sudo a2enmod ssl
    sudo a2enmod proxy_http

**Basic configuration**

Add the following to your Apache configuration. It's recommended to create a
file in `/etc/apache2/sites-available/rdiffweb`.

    <VirtualHost *:80>
        ServerName rdiffweb.mydomain.com
        ProxyPass / http://localhost:8080/ retry=5
        ProxyPassReverse / http://localhost:8080/
        RemoteIPHeader X-Real-IP
    </VirtualHost>

**SSL configuration**

Here is an example with SSL configuration.

    <VirtualHost *:80>
        ServerName rdiffweb.mydomain.com
        ServerAdmin me@mydomain.com
        # Redirect HTTP to HTTPS
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

        ProxyPass / http://localhost:8080/ retry=5
        ProxyPassReverse / http://localhost:8080/
        RequestHeader set X-Forwarded-Proto https
        RemoteIPHeader X-Real-IP

        # SSL Configuration
        SSLEngine on
        SSLCertificateFile    /etc/apache2/ssl/my_certificate.crt
        SSLCertificateKeyFile /etc/apache2/ssl/my_certificate.key
        <Location />
            Order Allow,deny
            Allow from all
        </Location>
    </VirtualHost>

Make sure you set `X-Real-IP` so that Rdiffweb knows the real IP address of the client. This is used in the rate limit to identify the client.

Make sure you set `X-Forwarded-Proto` correctly so that Rdiffweb knows that access is being made using the `https` scheme. This is used to correctly create the URL on the page.

## Configure Rdiffweb behind nginx reverse proxy

You may need a nginx server in case:

* you need to serve multiple web services from the same IP;
* you need more security (like HTTP + SSL).

This section doesn't explain how to install and configure your nginx server.
This is out-of-scope. The following is only provided as a suggestion and is in
no way a complete reference.

**Basic configuration**

        location / {
                # Define proxy header for cherrypy logging.
                proxy_set_header Host $host;
                proxy_set_header X-Real-IP $remote_addr;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header X-Forwarded-Host $server_name;
                proxy_set_header X-Forwarded-Proto $scheme;
                # Proxy
                proxy_pass http://127.0.0.1:8080/;
        }

Make sure you set `X-Real-IP` so that Rdiffweb knows the real IP address of the client. This is used in the rate limit to identify the client.

Make sure you set `X-Forwarded-Proto` correctly so that Rdiffweb knows that access is being made using the `https` scheme. This is used to correctly create the URL on the page.
