# Configuration

There are several entry points available for administrator to manage the configuration of Rdiffweb. This section aims to outline those configurations and explain each option available and what it does.

Since version 2.2, rdiffweb configuration is more flexible. You may configure every option using the configuration file, command line argument or environment variable.

Take note that configuration options are distinct from the runtime setting, available from the web interface. The configuration options here usually meant to be static and set before starting the server. You may get the list of configuration options by calling `rdiffweb --help`.

Note: If an option is specified in more than one place, the command line arguments override the environment variable, environment variables override config files, and config files override default value.

## Configuration file

To use configuration files, you may call rdiffweb with `-f` or `--config` to define the configuration file location. When not defined, Rdiffweb loads all configuration files from these locations by default:

* /etc/rdiffweb/rdw.conf
* /etc/rdiffweb/rdw.conf.d/*.conf

Configuration file syntax must define a key and a value. The key is case-sensitive, and you may use underscore (_) or dash (-) seemlessly. All lines beginning with '#' are comments and are intended for you to read. All other lines are configuration for rdiffweb.

E.g.:

    # This is a comment
    server_port=8081
    log_level=DEBUG

## Environment variables

In addition to configuration files, you may pass environment variables. The options name must be uppercase and prefixed with `RDIFFWEB_`. As an example, if you want to change the port used to listen for HTTP request for 8081, you must define `server-port` option as follow.

    RDIFFWEB_SERVER_PORT=8081

## Command line arguments

When launching `rdiffweb` executable, you may pass as many arguments as you want on the command line. The options must be prefixed with double dash (`--`) and you must single dash (-) to separate words.

E.g. `--server-port 8081` or `--server-port=8081` are valid


## Configure listening port and interface

For security reasons, Rdiffweb listen on port `8080` for HTTP request on loopback interface (127.0.0.1) by default. Consider configuring a reverse proxy like Nginx or Apache2 if you want to make Rdiffweb listen on port 80 for HTTP and port 443 for HTTPS request.

| Option | Description | Example |
| --- | --- | --- |
| server-host | Define the IP address to listen to. Use `0.0.0.0` to listen on all interfaces. Use `127.0.0.1` to listen on loopback interface. | 0.0.0.0 |
| server-port | Define the port to listen for HTTP request. Default to `8080` | 9090 |

## Configure administrator username & password

Using configuration file, you may setup a special administrator which cannot be
deleted or renamed from the web interface. You may also configure a specific
password for this user that cannot be updated from the web interface either.

In addition, you may also create other administrator users to manage Rdiffweb.

| Parameter | Description | Example |
| --- | --- | --- | 
| admin-user | Define the name of the default admin user to be created | admin |
| admin-password | administrator encrypted password as SSHA. Read online documentation to know more about how to encrypt your password into SSHA or use http://projects.marsching.org/weave4j/util/genpassword.php When defined, administrator password cannot be updated using the web interface. When undefined, default administrator password is `admin123` and it can be updated using the web interface. | modification |


## Configure logging

Rdiffweb can be configured to send logs to specific location. By default, logs are sent to the console (stdout or stderr). If you have installed Rdiffweb on a server, you should consider enabling the logging to help you keep track of the activities or to help you debug problem.

| Option | Description | Example |
| --- | --- | --- |
| log-level | Define the log level. ERROR, WARN, INFO, DEBUG | DEBUG |
| log-file | Define the location of the log file. | /var/log/rdiffweb/server.log |
| log-access-file | Define the location of the access log file. | /var/log/rdiffweb/access.log |

### Enable Debugging

A specific option is also available if you want to enable the debugging log. We do not recommend to enable this option in production as it may leak information to the user whenever an exception is raised.

| Option | Description | Example |
| --- | --- | --- |
| debug | enable rdiffweb debug mode - change the log level to DEBUG, print exception stack trace to the web interface and show SQL query in logs. | |
| environment | Define the type of environment: `development` or `production`. This is used to limit the information shown to the user when an error occurs. Default: production | development |

## Configure database

Rdiffweb use SQL database to store user preferences. The embedded SQLite database is well suited for small deployment (1-100 users). If you intended to have a large deployment, you must consider using a PostgreSQL database instead.

| Option | Description | Example |
| --- | --- | --- |
| database-uri | Location of the database used for persistence. SQLite and PostgreSQL database are supported officially. To use a SQLite database, you may define the location using a file path or a URI. e.g.: `/srv/rdiffweb/file.db` or `sqlite:///srv/rdiffweb/file.db`. To use PostgreSQL server, you must provide a URI similar to `postgresql://user:pass@10.255.1.34/dbname` and you must install required dependencies. By default, Rdiffweb uses a SQLite embedded database located at `/etc/rdiffweb/rdw.db`. | postgresql://user:pass@10.255.1.34/dbname | 


### SQLite

To use embedded SQLite database, pass the option `database-uri` with a URI similar to `sqlite:///etc/rdiffweb/rdw.db` or `/etc/rdiffweb/rdw.db`.

### PostgreSQL

To use an external PostgreSQL database, pass the option `database-uri` with a URI similar to `postgresql://user:pass@10.255.1.34/dbname`.

You may need to install additional dependencies to connect to PostgreSQL. Step to install dependencies might differ according to the way you installed Rdiffweb.

**Using Debian repository:**

    apt install python3-psycopg2

**Using Pypi repository:**

    pip install psycopg2-binary

## Configure LDAP Authentication

Rdiffweb may integrates with LDAP server to support user authentication.

This integration works with most LDAP-compliant servers, including:

* Microsoft Active Directory
* Apple Open Directory
* Open LDAP
* 389 Server

### LDAP options

| Option | Description | Example |
| --- | --- | --- |
| ldap-add-missing-user | `True` to create users from LDAP when the credential is valid. | True |
| ldap-add-user-default-role | Role to be used when creating a new user from LDAP. Default: user | maintainer |
| ldap-add-user-default-userroot | Userroot to be used when creating a new user from LDAP. Default: empty | /backups/{cn[0]} |
| ldap-base-dn | The DN of the branch of the directory where all searches should start from. | dc=my,dc=domain | 
| ldap-bind-dn | An optional DN used to bind to the server when searching for entries. If not provided, will use an anonymous bind. | cn=manager,dc=my,dc=domain |
| ldap-bind-password | A bind password to use in conjunction with `LdapBindDn`. Note that the bind password is probably sensitive data,and should be properly protected. You should only use the LdapBindDn and LdapBindPassword if you absolutely need them to search the directory. | mypassword |
| ldap-encoding | encoding used by your LDAP server. Default to utf-8 | cp1252 |
| ldap-filter | A valid LDAP search filter. If not provided, defaults to `(objectClass=*)`, which will search for all objects in the tree. | (objectClass=*) | 
| ldap-group-attribute-is-dn | True if the content of the attribute ldap-group-attribute is a DN. | true |
| ldap-group-attribute | name of the attribute defining the groups of which the user is a member. Should be used with ldap-required-group and ldap-group-attribute-is-dn. | member |
| ldap-network-timeout | Optional timeout value. Default to 10 sec. | 10 |
| ldap-protocol-version | Version of LDAP in use either 2 or 3. Default to 3. | 3 |
| ldap-required-group | name of the group of which the user must be a member to access rdiffweb. Should be used with ldap-group-attribute and ldap-group-attribute-is-dn. | rdiffweb |
| ldap-scope | The scope of the search. Can be either `base`, `onelevel` or `subtree`. Default to `subtree`. | onelevel |
| ldap-timeout | Optional timeout value. Default to 300 sec. | 300 |
| ldap-tls | `true` to enable TLS. Default to `false` | false |
| ldap-uri | URIs containing only the schema, the host, and the port. | ldap://localhost:389 | 
| ldap-username-attribute | The attribute to search username. If no attributes are provided, the default is to use `uid`. It's a good idea to choose an attribute that will be unique across all entries in the subtree you will be using. | cn | 
| ldap-version | version of LDAP in use either 2 or 3. Default to 3.| 3 |

### Automatically create user in Rdiffweb

If you have a large number of users in your LDAP, you may want to configure Rdiffweb to automatically create user in database that has valid LDAP credentials. The user will get created on first valid login.

You may optionally pass other options like `ldap-add-user-default-role` and `ldap-add-user-default-userroot` to automatically define the default user role and default user root for any new user created from LDAP.

Here a working configuration:

    ldap-add-missing-user=true
    ldap-add-user-default-role=user
    ldap-add-user-default-userroot=/backups/{cn[0]}

### Restrict access to a specific LDAP group

If you are making use of LDAP credentials validation, you will usually want to limit the access to member of a specific LDAP group. Rdiffweb support such scenario with the use of `ldap-required-group`, `ldap-group-attribute` and `ldap-group-attribute-is-dn`.

Here is an example of how you may limit Rdiffweb access to members of *Admin_Backup* group. This configuration is known to work with LDAP PosixAccount and PosixGroup.

    ldap-required-group=cn=Admin_Backup,ou=Groups,dc=nodomain
    ldap-group-attribute=memberUid
    ldap-group-attribute-is-dn=false

## Configure email notifications

Since Rdiffweb v0.9, you may configure Rdiffweb to send an email notification to the users when their backups did not complete successfully for a period of time.
When enabled, Rdiffweb will also send email notification for security reason when user's password is changed.

| Option | Description | Example |
| --- | --- | --- |
| email-encryption | Type of encryption to be used when establishing communication with SMTP server. Available values: `none`, `ssl` and `starttls` | starttls |
| email-host | SMTP server used to send email in the form `host`:`port`. If the port is not provided, default to standard port 25 or 465 is used. | smtp.gmail.com:587 | 
| email-sender | email addres used for the `From:` field when sending email. | Rdiffweb <example@gmail.com> |
| email-notification-time | time when the email notification should be sent for inactive backups. | 22:00 |
| email-username | username used for authentication with the SMTP server. | example@gmail.com |
| email-password | password used for authentication with the SMTP server. | CHANGEME |
| email-send-changed-notification | True to send notification when sensitive information get change in user profile. Default: false | True |

To configure the notification, you need a valid SMTP server. In this example, you are making use of a Gmail account to send emails.

    email-host=smtp.gmail.com:587
    email-encryption=starttls
    email-sender=example@gmail.com
    email-username=example@gmail.com
    email-password=CHANGEME
    email-send-changed-notification=true

Note: notifications are not sent if the user doesn't have an email configured in his profile.

## Configure user quota

Since v2.1, it's now possible to customize how user quota is controller for
your system without a custom plugin. By defining `quota-set-cmd`, `quota-get-cmd`
and `QuotaUsedCmd` configuration options, you have all the flexibility to
manage the quota the way you want by providing custom command line to be executed to respectively set the quota, get the quota and get quota usage.

| Option | Description | Example | 
| --- | --- | --- |
| quota-set-cmd | Command line to set the user's quota. | Yes. If you want to allow administrators to set quota from the web interface. |
| quota-get-cmd | Command line to get the user's quota. Should print the size in bytes to console. | No. Default behaviour gets quota using operating system statvfs that should be good if you are using setquota, getquota, etc. For ZFS and other more exotic file system, you may need to define this command. |
| quota-used-cmd | Command line to get the quota usage. Should print the size in bytes to console. | No. |

When Rdiffweb calls the scripts, special environment variables are available. You should make use of this variables in a custom script to get and set the disk quota.

* `RDIFFWEB_USERID`: rdiffweb user id. e.g.: `34`
* `RDIFFWEB_USERNAME`: rdiffweb username. e.g.: `patrik`
* `RDIFFWEB_USERROOT`: user's root directory. e.g.: `/backups/patrik/`
* `RDIFFWEB_ROLE`: user's role e.g.: `10` 1:Admin, 5:Maintainer, 10:User
* `RDIFFWEB_QUOTA`: only available for `quota-set-cmd`. Define the new quota value in bytes. e.g.: 549755813888  (0.5 TiB)

Continue reading about how to configure quotas for EXT4. We generally
recommend making use of project quotas with Rdiffweb to simplify the management of permission and avoid running Rdiffweb with root privileges.  The next section
presents how to configure project quota. Keep in mind it's also possible to
configure quota using either user's quota or project quota.

### Configure user quota for EXT4

This section is not a full documentation about how to configure ext4 project quota, 
but provide enough guidance to help you.

1. Enabled project quota feature  
   You must enable project quota feature for the EXT4 partition where your backup resides using:  
   `tune2fs -O project -Q prjquota /dev/sdaX`  
   The file system must be unmounted to change this setting and may require you
   to boot your system with a live-cd if your backups reside on root file system (`/`).  
   Also, add `prjquota` options to your mount point configuration `/etc/fstab`.
   Something like `/dev/sdaX   /   ext4    errors=remount-ro,prjquota     0    1`
2. Turn on the project quota after reboot  
   `quotaon -Pv -F vfsv1 /`
3. Check if the quota is working  
   `repquota -Ps /`
4. Add `+P` attribute on directories to enabled project quotas  
   `chattr -R +P /backups/admin`
5. Then set the project id on directories  
   `chattr -R -p 1 /backups/admin` where `1` is the rdiffweb user's id

Next, you may configure Rdiffweb quota command line for your need. For EXT4
project quotas, you only need to define `quota-set-cmd` with something similar
to the following. `quota-get-cmd` and `quota-used-cmd` should not be required
with EXT4 quota management.

    quota-set-cmd=setquota -P $RDIFFWEB_USERID $((RDIFFWEB_QUOTA / 1024)) $((RDIFFWEB_QUOTA / 1024)) 0 0 /

This effectively, makes use of Rdiffweb user's id as project id.

### Configure user quota for ZFS

This section is not a full documentation about how to configure ZFS project quotas,
but provide enough guidance to help you. This documentation uses `tank/backups`
as the dataset to store rdiffweb backups.

1. Quota feature is a relatively new feature for ZFS On Linux. Check your
   operating system to verify if your ZFS version support it. You may need
   to upgrade your pool and dataset using:  

   `zpool upgrade tank`
   `zfs upgrade tank/backups`

2. Add `+P` attribute on directories to enabled project quotas  
   `chattr -R +P /backups/admin`
   `chattr -R -p 1 /backups/admin`
   OR
   `zfs project -p 1 -rs /backups/admin`
   Where `1` is the rdiffweb user's id
   
Take note, it's better to enable project quota attributes when the repositories are empty.

## Configure Rate-Limit

Rdiffweb could be configured to rate-limit access to anonymous to avoid bruteforce
attacks and authenticated users to avoid Denial Of Service attack.

| Option | Description | Example |
| --- | --- | --- |
| rate-limit | maximum number of requests per hour that can be made on sensitive endpoints. When this limit is reached, an HTTP 429 message is returned to the user or the user is logged out. This security measure is used to limit brute force attacks on the login page and the RESTful API. | 20 |
| rate-limit-dir | location where to store rate-limit information. When undefined, data is kept in memory. | /var/lib/rdiffweb/session |

## Custom user's password length limits

By default, Rdiffweb supports passwords with the following lengths:

* Minimum: 8 characters
* Maximum: 128 characters

Changing the minimum or maximum length does not affect existing users' passwords. Existing users are not prompted to reset their passwords to meet the new limits. The new limit only applies when an existing user changes their password.

| Option | Description | Example |
| --- | --- | --- |
| password-min-length | Minimum length of the user's password | 8 |
| password-max-length | Maximum length of the user's password | 128 |
| password-score      | Minimum zxcvbn's score for password. Value from 0 to 4. Default value 1. | 4 |

You may want to read more about [zxcvbn](https://github.com/dropbox/zxcvbn) score value.

## Configure Rdiffweb appearance

A number of options are available to customize the appearance of Rdiffweb to your
need. Most likely, you will want to make it closer to your business brand.

| Option | Description | Example | 
| --- | --- | --- |
| header-name | Define the application name displayed in the title bar and header menu. | My Backup |
| default-theme | Define the theme. Either: `default`, `blue` or `orange`. Define the css file to be loaded in the web interface. You may manually edit a CSS file to customize it. The location is similar to `/usr/lib/python3/dist-packages/rdiffweb/static/`. | orange |
| welcome-msg | Replace the headline displayed in the login page. It may contains HTML. | Custom message displayed on login page.|
| favicon | Define the FavIcon to be displayed in the browser title | /etc/rdiffweb/my-fav.ico |

## Configure SSH Key management

Rdiffweb allows users to manage their SSH Keys by adding and removing them using the web interface. This feature may be disabled with `disable-ssh-keys`.

When this feature is enabled, adding or removing an SSH Key from the web interface.
Updates, the `${user_root}/.ssh/authorized_keys` file if the file already exists.

## Configure repositories clean-up job

Using the web interface, users may configure a retention period on individual repository to keep only a fixed number of days in backup. This is useful to control the growth of a repository disk usage.

To support this feature, Rdiffweb schedule a job to clean-up the repositories in backup. This job is ran once a day. You may change the default time when this schedule job is running by defining another value for option `remove-older-time`.

| Parameter | Description | Example |
| --- | --- | --- |
| remove-older-time | Time when to execute the remove older task | 22:00 | 

## Configure temporary folder location

To restore file or folder, Rdiffweb needs a temporary directory to create the file to be downloaded. By default, Rdiffweb will use your default temporary folder defined using environment variable `TMPDIR`, `TEMP` or `TMP`. If none of these environment variables are defined, Rdiffweb fallback to use `/tmp`.

If you want to enforce a different location for the temporary directory, you may define the option `tempdir` with a different value. Take note, this directory must be created with the right ownership and permissions to allow Rdiffweb to use it. Also make sure enough disk space is available. Usually, a 32GiB is enough.

| Parameter | Description | Example |
| --- | --- | --- |
| tempdir | alternate temporary folder to be used when restoring files. Might be useful if the default location has limited disk space| /tmp/rdiffweb/ |


## Configure repository lookup depthness.

When defining the UserRoot value for a user, Rdiffweb will scan the content of this directory recursively to lookups for rdiff-backup repositories. For performance reason, Rdiffweb limits the recursiveness to 3 subdirectories. This default value should suit most use cases. If you have a particular use case, it's possible to allow Rdiffweb to scan for more subdirectories by defining a greater value for the option `max-depth`. Make sure to pick a reasonable value for your use case as it may impact the performance.

| Parameter | Description | Example |
| --- | --- | --- |
| --max-depth | Define the maximum folder depthness to search into the user's root directory to find repositories. This is commonly used if your repositories are organised with multiple sub-folders. Default: 3 | No | 10 |
