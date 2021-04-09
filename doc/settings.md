# Runtime Settings

This section describes the settings available from the web interface.

## Setup users’ repositories

A repository represents a directory where rdiff-backup has created a
structure to store your data. Basically, a repository is a directory
containing the `rdiff-backup-data` folder.

As an example, look at the following folder structure.

    + / (root)
      |
      + backups
        |
        + my-laptop
        | |
        | + rdiff-backup-data
        | |
        | + home
        |
        + server1
          |
          + rdiff-backup-data
          |
          + home
          |
          + etc
          |
          + var

It contains two (2) repositories: `/backups/my-laptop/` and `/backups/server1/`.

Once your installation of rdiffweb is completed, go to the admin area to configure
your users root directory.

For each user, you must assign a "root directory". **The user can access every
repositorie placed underneath the "root directory".** Consider the
following assignment:

 * admin: /backups/
 * patrik: /backups/my-laptop/

![Admin area - users list](rdiffweb-users.png)

Assignment of a "root directory" is the only way to control access to
repositories.

 * The "admin" user will have access to "my-laptop" and "server1" repositories.
 * The user "patrik" only has access to "my-laptop" repository.
 