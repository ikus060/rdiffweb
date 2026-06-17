![Rdiffweb Banner](https://gitlab.com/ikus-soft/rdiffweb/-/raw/master/doc/_static/banner.png)

<p align="center">
<strong>
<a href="https://www.rdiffweb.org">website</a>
• <a href="https://www.ikus-soft.com/archive/rdiffweb/doc/latest/html/">docs</a>
• <a href="https://groups.google.com/d/forum/rdiffweb">community</a>
• <a href="https://rdiffweb-demo.ikus-soft.com/">demo</a>
</strong>
</p>

<p align="center">
<a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/ikus060/rdiffweb"></a>
<a href="https://gitlab.com/ikus-soft/rdiffweb/pipelines"><img alt="Build" src="https://gitlab.com/ikus-soft/rdiffweb/badges/master/pipeline.svg"></a>
<a href="https://sonar.ikus-soft.com/dashboard?id=rdiffweb"><img alt="Quality Gate Minarca Client" src="https://sonar.ikus-soft.com/api/project_badges/measure?project=rdiffweb&metric=alert_status"></a>
<a href="https://sonar.ikus-soft.com/dashboard?id=rdiffweb"><img alt="Coverage" src="https://sonar.ikus-soft.com/api/project_badges/measure?project=rdiffweb&metric=coverage"></a>
<a href="https://bestpractices.coreinfrastructure.org/projects/6583"><img src="https://bestpractices.coreinfrastructure.org/projects/6583/badge"></a>
</p>

<h1 align="center">
Welcome to Rdiffweb
</h1>

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

The Rdiffweb website is <https://rdiffweb.org/>.

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
* File and folder deletion

## Demo

If you quickly want to check how Rdiffweb is behaving, you may try our demo server hosted on:

[https://rdiffweb-demo.ikus-soft.com/](https://rdiffweb-demo.ikus-soft.com/)

Use the following credential to login:

* Username: admin
* Password: admin123

## Installation & Docker usage

For detailed installation steps, read the [Installation documentation](https://www.ikus-soft.com/archive/rdiffweb/doc/latest/html/installation.html).

## Current Build Status

[![Build Status](https://gitlab.com/ikus-soft/rdiffweb/badges/master/pipeline.svg)](https://gitlab.com/ikus-soft/rdiffweb/pipelines)

## Download

You should read the [Documentation](https://www.ikus-soft.com/archive/rdiffweb/doc/latest/html/index.html) to properly install Rdiffweb in your environment.

**Docker**

    docker pull ikus060/rdiffweb

**Debian**

    apt install lsb-release
    curl -L https://www.ikus-soft.com/archive/rdiffweb/public.key | gpg --dearmor > /usr/share/keyrings/rdiffweb-keyring.gpg
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/rdiffweb-keyring.gpg] https://nexus.ikus-soft.com/repository/apt-release-$(lsb_release -sc)/ $(lsb_release -sc) main" > /etc/apt/sources.list.d/rdiffweb.list
    apt update
    apt install rdiffweb

**Pypi**

    pip install rdiffweb

## Newsletter

Subscribing to our newsletter is an effective way to stay up-to-date on the latest news about Rdiffweb.
By signing up for, you will receive regular updates and notifications about new features, updates, and releases related to Rdiffweb.

[Rdiffweb Newsletter](https://rdiffweb.org/contactus).

## Google Group

Join our growing community to get answers to your technical questions.

Rdiffweb users should use the [Rdiffweb Google Group](https://groups.google.com/forum/#!forum/rdiffweb).

## Documentation

Want to know more about Rdiffweb and learn it thoroughly? Read our complete documentation.

[Rdiffweb Documentation](https://www.ikus-soft.com/archive/rdiffweb/doc/latest/html/).

## Bug Reports

Bug reports should be reported on the Rdiffweb Gitlab at <https://gitlab.com/ikus-soft/rdiffweb/-/issues>

## Professional support

Professional support for Rdiffweb is available by [contacting IKUS Soft](https://rdiffweb.org/contactus).

## Support Us Through Github Sponsorship

We are passionate about developing and maintaining this open-source project to make it better with each update. Your support can help us continue our efforts and enhance the project for the entire community. By becoming a Github Sponsor, you directly contribute to the project's sustainability and growth.

[Becoming a Sponsor](https://github.com/sponsors/ikus060)
