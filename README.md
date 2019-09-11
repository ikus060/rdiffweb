# Rdiffweb

Rdiffweb is a web application that allows you to view repositories generated
by [rdiff-backup](http://www.nongnu.org/rdiff-backup/). The purpose of this
application is to ease the management of backups and quickly restore your data
with a rich and powerful web interface.

Rdiffweb is written in Python and is released as open source project under the 
GNU GENERAL PUBLIC LICENSE (GPL). All source code and documentation are
Copyright Rdiffweb contributors.

Rdiffweb is actively developed by [Patrik Dufresne](http://patrikdufresne.com)
since November 2014.

The Rdiffweb source code is hosted on [self-hosted Gitlab](https://git.patrikdufresne.com/pdsl/rdiffweb)
and mirrored to [Github](https://github.com/ikus060/rdiffweb).

The Rdiffweb website is https://github.com/ikus060/rdiffweb.

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

If you quickly want to check how rdiffweb is behaving, you may try our demo server hosted on:

[http://demo.patrikdufresne.com/](http://demo.patrikdufresne.com/)

Use the following credential to login:

 * Username: admin
 * Password: admin123

## Installation

For detailed installation steps, take a look at the [Documentation](https://github.com/ikus060/rdiffweb/blob/master/doc/installation.md).

## Current Build Status

[![Build Status](https://git.patrikdufresne.com/pdsl/rdiffweb/badges/master/pipeline.svg)](https://git.patrikdufresne.com/pdsl/rdiffweb/pipelines)

# Download

![PyPI](https://img.shields.io/pypi/v/rdiffweb)

You may download rdiffweb from [pypi](https://pypi.org/project/rdiffweb/).

You should read the [Documentation](https://github.com/ikus060/rdiffweb/blob/master/doc/index.md) to properly install rdiffweb in your environment.

# Support

## Mailing list

Rdiffweb users should use the Rdiffweb mailing list. To subscribe, go to https://groups.google.com/forum/#!forum/rdiffweb

## Bug Reports

Bug reports should be reported on the Rdiffweb development web site at https://github.com/ikus060/rdiffweb/issues

## Professional support

Professional support for Rdiffweb is available by contacting [Patrik Dufresne Service Logiciel](http://www.patrikdufresne.com/en/support/#form).

# Changelog

## 1.0.0 
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

## 0.10.9
 * Better error handling when error.log file are not valid gzip file

