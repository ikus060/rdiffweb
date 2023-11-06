# Introduction

## What is Rdiffweb?

Rdiffweb is a web interface that can be used to display and browse Rdiff-backup repositories. It's specially optimized to manage access to your backup in a centralized deployment. If you have a centralized backup server containing multiple repositories for various users, you can use it to control user access to those repositories. 

Once a user has access to a repository, they may browse its content and restore previous revisions directly from the web interface without using a command line.

## Architecture

Rdiffweb is a standalone application that can be used to display and restore data from Rdiff-backup repositories. Backup data will be accessible from the application, either with files being accessible locally on the same physical server or using mount points like NFS.

This architecture provides deployment flexibility giving you a choice regarding the storage and the backup procedure.

While it can be run on a centralized backup server, Rdiff-backup cannot be used to manage the backup procedure itself. If you are looking for a completely managed backup solution, please look further into [Minarca](https://minarca.org/).

## Main features

* Web interface: browse and restore Rdiff-backup repositories without command lines.
* User management: provides user access control list for repositories.
* User authentication: username and password validation are done using a database or your LDAP server.
* User permission: allows you to control which users can run deletion operations.
* Email notification: emails can be sent to keep you informed when backup fails
* Statistics visualization: web interface to view backup statistics provided by Rdiff-backup.
* Open source: no secrets. Rdiffweb is a free open-source software. The source code is licensed under GPL v3.
* Support: business support will be available through [Ikus Software](https://ikus-soft.com).
* Rdiff-backup: used as the main backup software you benefit from its stability, cross-platform. And you can still use it the way you are used to with the command line.

## Software stack

Rdiffweb software consists of a single component: the web server, which provides a RESTful API and a user interface.

Aside from the web interface, which uses HTML and JavaScript everything else is written in Python programming language.

The Rdiffweb application relies on rdiff-backup and must be installed on the same server.

## Getting help

### Mailing list

Rdiffweb is open-source, and contributions are welcome. Here is the main communication channel to get help from other users.

[Rdiffweb Google Group](https://groups.google.com/forum/#!forum/rdiffweb)

### Bug tracker

If you encounter a problem, you should start by asking to be added to the mailing list. Next, you may open a ticket in our issue tracking system.

[Gitlab Issues](https://gitlab.com/ikus-soft/rdiffweb/-/issues)

### Professional support

If you need professional support or custom development, you should contact Ikus Software directly.

[Support Form](https://rdiffweb.org/contactus)
