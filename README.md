# Rdiffweb

Rdiffweb is a web application that allows you to view repositories generated
by [rdiff-backup](https://rdiff-backup.net/). The purpose of this
application is to ease the management of backups and quickly restore your data
with a rich and powerful web interface.

Rdiffweb is written in Python and is released as open source project under the 
GNU GENERAL PUBLIC LICENSE (GPL). All source code and documentation are
Copyright Rdiffweb contributors.

Rdiffweb is actively developed by [IKUS Soft](https://www.ikus-soft.com/)
since November 2014.

The Rdiffweb source code is hosted on [Gitlab](https://gitlab.com/ikus-soft/rdiffweb)
and mirrored to [Github](https://github.com/ikus060/rdiffweb).

The Rdiffweb website is https://rdiffweb.org/.

## Features

With its rich web interface Rdiffweb provide a notable list of features:

 * Browse your backup
 * Restore single file or multiple files as an archived
 * Users authentication via local database and LDAP
 * Users authorization
 * Email notification when backup is not successful
 * Configurable repository encoding
 * Configurable retention period
 * Backup statistics visualization using graphs
 * SSH Keys management
 * Disk quota visualization

## Demo

If you quickly want to check how Rdiffweb is behaving, you may try our demo server hosted on:

[https://rdiffweb-demo.ikus-soft.com/](https://rdiffweb-demo.ikus-soft.com/)

Use the following credential to login:

 * Username: admin
 * Password: admin123

## Installation

For detailed installation steps, take a look at the [Documentation](https://gitlab.com/ikus-soft/rdiffweb/-/blob/master/doc/installation.md).

## Current Build Status

[![Build Status](https://gitlab.com/ikus-soft/rdiffweb/badges/master/pipeline.svg)](https://gitlab.com/ikus-soft/rdiffweb/pipelines)

# Download

![PyPI](https://img.shields.io/pypi/v/rdiffweb)

You may download Rdiffweb from [PyPI](https://pypi.org/project/rdiffweb/).

You should read the [Documentation](https://gitlab.com/ikus-soft/rdiffweb/-/blob/master/doc/index.md) to properly install Rdiffweb in your environment.

# Support

## Mailing list

Rdiffweb users should use the [Rdiffweb mailing list](https://groups.google.com/forum/#!forum/rdiffweb).

## Bug Reports

Bug reports should be reported on the Rdiffweb Gitlab at https://gitlab.com/ikus-soft/rdiffweb/-/issues

## Professional support

Professional support for Rdiffweb is available by contacting [IKUS Soft](https://www.ikus-soft.com/en/support/#form).

# Changelog

# 2.1.0 (2021-01-15)

* Debian package: Remove dh-systemd from Debian build dependencies (https://bugs.debian.org/871312we)
* Improve Quota management:
  * `QuotaSetCmd`, `QuotaGetCmd` and `QuotaUsedCmd` options could be used to customize how to set the quota for your environment.
  * Display user's quota in User View
  * Display user's quota in Admin View
  * Allow admin to update user quota from Admin View when `QuotaSetCmd` is defined.
  * Allow admin to define user quota using human readable value (e.g.: GiB, TiB, etc.)
  * Improve logging around quota management
* Improve robustness when service is starting
* Improve robustness when repository has wrong permission defined (e.g.: when some files not readable)
* Add user id in Admin view
* Replace `UserObject(1)` by the actual username in log file to improve debugging

# 2.0.0 (2020-12-04)

* Re-implement logic to update repositories views to remove duplicates and avoid nesting repo. #107
* Handle elapsed time of days in the graph. Thanks [Nathaniel van Diepen](https://github.com/Eeems) contributions.
* Rebrand all link to ikus-soft.com
* Update documentation to install rdiffweb
* Remove obsolete minify dependency
* Drop support for python2
* Provide null translation if translation catalogues are not found
* Pass a LANG environment variable to rdiff-backup restore process to fix encoding issue #112
* Remove obsolete python shebang
* Remove execution bit (+x) on python modules
* Provide `--help` and `--version` on `rdiffweb` executable
* Improve cherrypy version detection
* Do not update translation files (.mo) during build

## 1.5.0 (2020-06-24)

This minor release introduce official support of rdiffweb on Debian Bullseye. It also includes some usability improvements.

 * Change formatting of Last Backup date for "Updated 3 weeks ago" to ease the readability
 * Add support for Debian Bullseye
 * Add support for Python 3.8 (#104)
 * Add warning in the users list view when a root directory is invalid (#30)
 * Add options to control search depthness (#1)
 * Print a warning in the log when the "DefaultTheme" value is not valid (#90)

## 1.4.0 (2020-05-20)

Thanks to our sponsor, this release introduce a feature to have better control over the user's permission by defining 3 different levels of privilege: Admin, Maintainer and User. This addition allows you to have better control on what your users can or can't do.

 * Fix single repository discovery when a user's home is a rdiff-backup repository
 * [SPONSORED] Add a new setting at the user level to define the user's role. Admin,
   Maintainer and User. Admin are allowed to do everything. Maintainer are
   allow to browse and delete repo. Users are only allowed to browse. #94
 * Add "Powered by" in the web interface footer #91
 * Display a nice error message when trying to delete admin user #93
 * Introduce usage of wtforms and flash in admin users for better form validation. #96 #97
 * Update French translation

## 1.3.2 (2020-04-23)

This minor releases fixed issues found while testing release 1.3.0.

 * Fix lookup of executable rdiff-backup and rdiffweb-restore to search in current virtualenv first
 * Fix repository view when multiple repo path are conflicting
 * Fix logging of rdiffweb-restore subprocess

## 1.3.1 (2020-04-10)

This minor release enforces security of the password stored in rdiffweb database to make use of a better encryption using SSHA.
Only new passwords will make use of the SSHA scheme.

 * Enforce password encryption by using SSHA scheme #88

## 1.3.0 (2020-04-07)

This release focuses on improving the restore of big archives. The download should be much faster to start. Major enhancement was made to offload the processing outside the web server. And all of this is still compatible with rdiff-backup v1.2.8 and the latest v2.0.0.

 * Restore file and folder in a subprocess to make the download start faster
 * Fix encoding of archive on Python3.6 (CentOS 7) by using PAX format
 * Add support to restore files and folders using rdiff-backup2
 * Remove obsolete dependencies `pysqlite2`
 * Fix issue creating duplicate entries of repository in the database

## 1.2.2 (2020-03-05)

This release provides little improvement to the v1.2.x including official support of rdiff-backup v2.0.0.

 * Enhance the repository to invite users to refresh the repository when the view is empty.
 * Support rdiff-backup v2.0.0
 * Deprecate support for cherrypy 4, 5, 6 and 7
 * Improve loading of repository data (cache status and entries)
 * Restore compatibility with SQLite 3.7 (CentOS7)

Known issues:

 * Filename encoding in tar.gz and zip file might not be accurate if you are running Python 3.6 (CentOS7)


## 1.2.1 (2020-02-08)

Little bug fix following the previous release

 * Fix 404 error when trying to access other users repo as admin
 * Fix logging format for cherrypy logs to matches rdiffweb format
 * Add log rotation by default

## 1.2.0 (2020-01-30)

This release focus on improving the database layers for better extendability to add more type of data and to support more databases backend like postgresql in the near future.

 * Add explicit testing for Debian Stretch & Buster
 * Change the persistence layers
   * Minimize number of SQL queries
   * Add object lazy loading
   * Add object data caching
 * Fix bugs with SQLite <= 3.16 (Debian Stretch)

## 1.1.0 (2019-10-31)

This release focus on improving the admin area and building the fundation for repository access control list (ACL).

 * Update documentation from PDSL web site
 * Improve the navigation bar layout
 * Update the login page headline
 * Update jinja2 version to allow 2.10.x
 * Show server log in admin area
 * Reduce code smell
 * Add System information in admin area
 * Validate credential using local database before LDAP
 * Reffactoring templates macros
 * Enhance user's view search bar
 * Change repository URL to username/repopath
 * Add System information in admin area
 * Improve testcases
 * Clean-up obsolete code
 * Fix issue with captital case encoding name
 * Fix compilation of less files
 * Fix google font import

## 1.0.3 (2019-10-04)
 * Removing the auto update repos

## 1.0.2 (2019-10-01)
 * Create "admin" user if missing
 * Update french translation

## 1.0.1 (2019-09-22)
 * Update installation documentation 
 * Fix removal of SSH Key
 * Return meaningful error to the user trying to add an existing SSH key

## 1.0.0 (2019-09-11)
 * Make repository removal more robust
 * Improve performance of librdiff
 * Add new RESTful api
 * Return the right HTTP 401 or 402 error code for authentication
 * Fix bug introduce by upgrade to Jinja2 + python3
 * Store ssh keys in database and disk
 * Add support for theme (default, orange)
 * Remove deprecated profiling code
 * Add disk usage support / quota
 * Add support of cherrypy v18
 * Drop support of cherrypy v3.2.2
 * Add wsgi entry point
 * Replace the plugins architecture to ease implementation
 * Numerous bug fixes

## 0.10.9 (2019-05-22)
 * Better error handling when error.log file are not valid gzip file

