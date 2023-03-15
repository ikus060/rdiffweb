# Quick Start

What to do to get started using Rdiffweb ?

1. [Install Rdiffweb](installation.md)

   * Rdiffweb can be installed on a Linux-based operating system.

2. [Configure the database](configuration.md#configure-database)

   * Rdiffweb can use either SQLite or PostgreSQL as the backend database.
   * To use SQLite, no additional configuration is needed. To use PostgreSQL, update the `database-uri` setting in the `/etc/rdiffweb/rdw.conf` file with the appropriate database connection details.

3. [Change the administrator password](configuration.md#configure-administrator-username-and-password)

   * You can change the administrator password either through the admin-password configuration option in the `/etc/rdiffweb/rdw.conf` file or through the web interface.
   * To change the password via the configuration file, update the `admin-password` setting with a new, secure password.
   * To change the password via the web interface, log in as the administrator (username: **admin** password: **admin123**) click on the "admin" in top-right corner, and select "Edit profile".

4. [Create a user account and adjust the user root location](settings.md#users-repositories)

   * To create a new user, log in as the administrator (username: **admin** password: **admin123**) click on the "Admin area" tab, and select "Users".
   * Click "Add user" and follow the prompts to create a new user account with a username and password.
   * After creating the user account, you can adjust the user's root location by going to the "Users" tab in the web interface, selecting the user, and clicking on "Edit". From there, you can specify the user's root location defining the location of the backup for that particular user..
