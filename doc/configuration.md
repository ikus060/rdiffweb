# Rdiffweb configuration

## LDAP Authentication

Rdiffweb integrates with LDAP to support user authentication. 

This integration works with most LDAP-compliant directory servers, including:

* Microsoft Active Directory
* Apple Open Directory
* Open LDAP
* 389 Server.

**Requirements**

Make sure you have `python-ldap` installed either from your Linux distribution repository or from pypi using `pip`.

    sudo apt-get install python-ldap
    OR
    sudo pip install python-ldap

Plugin parameters:

| Parameter | Description | Required | Example |
| --- | --- | --- | --- |
| LdapUri | URIs containing only the schema, the host, and the port. | Yes | ldap://localhost:389 | 
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

## Email notifications

Since Rdiffweb v0.9, you may setup notification when your backup did not
run for a given period of time. This is useful to know when your backup
setup is not working. This section describes how to configure rdiffweb to notify you.

**Edit config file**

Edit rdiffweb config file `/etc/rdiffweb/rdw.conf` and edit the `Email*`
configuration parameters to suit your environment. The following is an example
using a gmail account to sent notification.

    #----- Enable Email Notification
    # The server can be configured to email user when their repositories have not
    # been backed up for a user-specified period of time. To enable this feature,
    # set below settings to correct values.
    EmailNotificationTime=6:30
    EmailHost=smtp.gmail.com:587
    EmailEncryption=starttls
    EmailSender=example@gmail.com
    EmailUsername=example@gmail.com
    EmailPassword=CHANGEME

**Restart rdiffweb**

To apply the modification, restart rdiffweb as follow:

    sudo service rdiffweb restart

**Edit your preferences**

Login to rdiffweb using your username & password. Browse to your user settings.
A new tab named "Notification" you be displayed. Click on it to change the
notification settings for each repository.

## User's quota management

Since 2.1.0, it's now possible to customize how user quota is controller for
your system without a custom plugin. By defining `QuotaSetCmd`, `QuotaGetCmd`
and `QuotaUsedCmd` configuration options, you have all the flexibility to
manage the quota the way you want by providing custom command line to be
executed to respectively set the quota, get the quota and get quota usage.

When calling the script, special environment variables are available:

* RDIFFWEB_USERID: rdiffweb user id. e.g.: `34`
* RDIFFWEB_USERNAME: rdiffweb user name. e.g.: `patrik`
* RDIFFWEB_USERROOT: user's root directory. e.g.: `/backups/patrik/`
* RDIFFWEB_ROLE: user's role e.g.: `10` 1:Admin, 5:Maintainer, 10:User
* RDIFFWEB_QUOTA: only available for `QuotaSetCmd`. Define the new quota value in bytes. e.g.: 549755813888  (0.5 TiB)


| Parameter | Description | Required | 
| --- | --- | --- |
| QuotaSetCmd | Command line to set the user's quota. | Yes. If you want to allow administrators to set quota from the web interface. |
| QuotaGetCmd | Command line to get the user's quota. Should print the size in bytes to console. | No. Default behaviour gets quota using operating system statvfs that should be good if you are using setquota, getquota, etc. For ZFS and other more exotic file system, you may need to define this command. |
| QuotaUsedCmd | Command line to get the quota usage. Should print the size in bytes to console. | No. |

Continue reading about how to configure quotas for EXT4. We generally
recommend making use of project quotas with rdiffweb to simplify the management
of permission and avoid running rdiffweb with root privileges.  The next section
present how to configure project quota. Keep in mind it's also possible to
configure quota using either user's quota or project quota.

### Configure user quota for ext4

This section is not a full documentation about how to configure ext4 project quota
but provide enough guidance to help you.

1. Enabled project quota feature  
   You must enable project quota feature for the ext4 partition where your backup resides using:  
   `tune2fs -O project -Q prjquota /dev/sdaX`  
   The file system must be unmounted to change this setting and may require you
   to boot you system with a live-cd if your backups reside on root file system (`/`).  
   Also, add `prjquota` options to your mount point configuration `/etc/fstab`.
   Something like `/dev/sdaX   /   ext4    errors=remount-ro,prjquota     0    1`
2. Turn on the project quota after reboot  
   `quotaon -Pv -F vfsv1 /`
3. Check if the quota is working  
   `repquota -Ps /`
4. Add `+P` attribute on directory you which to control quota  
   `chattr -R +P /backups/admin`
5. Then set the project id on directories  
   `chattr -R -p 1 /backups/admin` where `1` is the rdiffweb user's id

Next you may configure rdiffweb quota command line for your need. For ext4
project quotas, you only need to define `QuotaSetCmd` with something similar to:

    QuotaSetCmd=setquota -P $RDIFFWEB_USERID $((RDIFFWEB_QUOTA / 1024)) $((RDIFFWEB_QUOTA / 1024)) 0 0 /

This effectively, makes use of rdiffweb user's id as project id.

### Configure user quota for zfs

This section is not a full documentation about how to configure ZFS project quotas
but provide enough guidance to help you. This documentation uses `tank/backups`
as the dataset to store rdiffweb backups.

1. Quota feature is a relatively new feature for ZFS On Linux. Check your
   operating system to verify if your ZFS version support it. You may need
   to upgrade your pool and dataset using:  
   
   `zpool upgrade tank`
   `zfs upgrade tank/backups`
   
2. Add `+P` attribute on directory you which to control quota  
   `chattr -R +P /backups/admin`
   `chattr -R -p 1 /backups/admin`
   OR
   `zfs project -p 1 -rs /backups/admin`
   Where `1` is the rdiffweb user's id
   
Take note, it's better to enable project quota attributes when the repositories are empty.

## Other Rdiffweb settings

| Parameter | Description | Required | Example |
| --- | --- | --- | --- |
| ServerHost | Define the IP address to listen to. Use 0.0.0.0 to listen on all interfaces. | No | 127.0.0.1 |
| ServerPort | Define the host to listen to. Default to 8080 | No | 80 |
| LogLevel | Define the log level. ERROR, WARN, INFO, DEBUG | No | DEBUG |
| Environment | Define the type of environment: development, production. This is used to limit the information shown to the user when an error occur. | No | production |
| HeaderName | Define the application name displayed in the title bar and header menu. | No | My Backup |
| DefaultTheme | Define the default theme. Either: default or orange. Define the css file to be loaded in the web interface. You may manually edit a css file to customize it. the location is similar to `/usr/local/lib/python2.7/dist-packages/rdiffweb/static/`. It's preferable to contact the developer if you want a specific color scheme to be added. | No | orange |
| WelcomeMsg | Replace the headling displayed in the login page | No | - |
| LogFile | Define the location of the log file | No | /var/log/rdiffweb.log |
| LogAccessFile | Define the location of the access log file | No | /var/log/rdiffweb-access.log |
| RemoveOlderTime | Time when to execute the remove older task | No | 22:00 | 
| SQLiteDBFile | Location of the SQLite database | No | /etc/rdiffweb/rdw.db | 
| AddMissingUser | True to create users from LDAP when the credential are valid. | No | True |
| AdminUser | Define the name of the default admin user to be created | No | admin |
| FavIcon | Define the FavIcon to be displayed in the browser title | No | /etc/rdiffweb/my-fav.ico |
| TempDir | Define an alternate temp directory to be used when restoring files. | No | /retore/ |
| MaxDepth | Define the maximum folder depthness to search into the user's root directory to find repositories. This is commonly used if you repositories are organised with multiple sub-folder. Default: 5 | No | 10 |


## Configure Apache - Reverse Proxy (optional)

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
    </VirtualHost>

**SSL configuration**
Here an example with SSL configuration.

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

## Configure nginx (optional)

You may need an nginx server in case:

 * you need to serve multiple web services from the same IP;
 * you need more security (like HTTP + SSL).

This section doesn't explain how to install and configure your nginx server.
This is out-of-scope. The following is only provided as a suggestion and is in
no way a complete reference.

See [/extras/nginx](../extras/nginx) folder for example of nginx configuration
to be used with rdiffweb.
