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

# Changelog

# 2.11.0 (2025-x-x)

* **New Features**
  * Administrators can disable user accounts (#313).
  * Administrators can delete users with or without data (#335).
  * Added OAuth authentication support (sponsored by Orion Service Numérique)
  * Added activity logs with support for comments/messages on users and repositories (#345).

* **Improvements**
  * Updated login page.
  * Improved loading of user repositories view with caching (#331).
  * API now accepts role names in POST /api/users (#341).
  * Added PT‑BR translation.
  * Updated French translation.
  * Updated OS/platform support:
    * Added Ubuntu Plucky support.
    * Add Debian Trixie support.
    * Add Python 3.13 supports.

* **Bug Fixes**
  * Fixed error sending email when repository is damaged (#326).
  * Fixed document upload (#337).
  * Fixed selenium execution on Bookworm.
  * Fixed handling of damaged‑repo email notifications (#326).

* **Internal / Under‑the‑Hood Changes**
  * Renamed internal identifiers (`userid` and `repoid`) to unified `id`.
  * Upgraded SQL timestamp implementation.
  * Verified OAuth URL at startups (#339).
  * Cleaned deprecated codes and removed warnings.
  * Removed python3‑future and python3‑nose dependencies.
  * Pinned cheroot < 11 due to upstream thread issue (#769).
  * Updated documentation (installation.md).
  * General maintenance updates (copyright, RestAPI plugin metadata).
  * Multiple dependency upgrades: LDAP modules, auth plugins, secure headers, flake8 bump, new python‑zxcvbn‑rs‑py dependency, RestAPI plugin updates.
  * Dropped Python 3.8.
  * Dropped Ubuntu Oracular
  * Dropped Debian Bullseye due to backports/EOL.

# 2.10.6 (2025-10-02)

* Security: fix token impersonation vulnerability (CVE-2025-67796).

# 2.10.5 (2025-06-20)

* Send deprecation warning into the logs

# 2.10.4 (2025-06-13)

* **New Features:**
    * Added Swagger documentation for the Rdiffweb API (#325).
    * Added keepdays and maxage display in the admin repositories view (#310).
    * Added an intermediate loading page when restoring a file or folder (#322).
* **Improvements:**
    * Adjusted filter button labels for better clarity.
    * Improved translation loading with caching.
    * Renamed "Backup Log" and "Restore Log" labels for better clarity (#316).
    * Enhanced backup inactivity email notifications for better clarity (#312).
    * Adjusted quota settings to align with the nearest block size, preventing the "Setting user's quota is not supported" error.
    * Renamed the Admin repository view page title.
* **Bug Fixes:**
    * Fixed reported change dates to exclude .missing entries.
    * Fixed display of filenames containing < or > in the file statistics view.
    * Fix database schema upgrade with null mfa, lang or report_time_range.
* **Internal/Under-the-Hood Changes:**
    * Updated Debian packaging to conform to Debian packaging rules.
    * Migrated project configuration to pyproject.toml (#281).
    * Used forking instead of subprocess to restore files.
    * Remove wsgi entrypoint that was never officially supported.
    * Lookup for rdiff-backup and rdiff-backup-delete in current executable location.

## 2.9.7 (2025-02-19)

* Trigger creation of default user `admin` after plugin startup  minarca#295

## 2.9.6 (2025-01-06)

* Remove Ubuntu Mantic & Ubuntu Lunar
* Explicitly declare pytz dependency

## 2.9.5 (2024-11-05)

* Add support for Ubuntu Noble 24.04 LTS & Oracular 24.10 #317

## 2.9.4 (2024-10-24)

* Complete french translation #315

## 2.9.3 (2024-08-02)

* Provide default encoding value to support old database with NOT NULL contrains

## 2.9.2 (2024-07-03)

* Use default language to send notification if user doesn't have a "Preferred Language" #306

## 2.9.1 (2024-06-11)

* Add "Preferred Language" to Admin view to allow administrator to update the value
* Improve DockerImage by removing cache files
* Upgrade rdiff-backup to v2.2.6 in DockerFile

## 2.9.0 (2024-04-22)

* Add API entry point to create and list access token
* Add access token scope #298
* Add user's quota to Rdiffweb API #299
* Change Debian and Ubuntu version numbering
* Drop support for Debian Buster

## 2.8.9 (2023-02-19)

* Fix display of page settings for user with role "user"

## 2.8.8 (2023-01-08)

* Fix usage of `session-idle-timeout` in config file #296

## 2.8.7 (2024-01-04)

* Adjust the session idle and absolute timeouts to 10 and 30 minutes, respectively.
* Fix date calculation when generating report in January #295

## 2.8.6 (2023-11-24)

* Fix broken URL to <https://ikus-soft.com>
* Fix "Remember me" check box to allow cliking on label to ease usability #293
* Fix translation of backup status in email report #291
* Adding German translation file - credit to [Michael Nitzsche](https://github.com/einzelfabrik)

## 2.8.5 (2023-10-10)

* Fix reported version in Debian package #289
* Add support for WTForms v3.1.0
* Add last backup date to email notification

## 2.8.4 (2023-09-29)

* Add ratelimit to Access Token, SSH Keys and User creation [CVE-2023-5289](https://nvd.nist.gov/vuln/detail/CVE-2023-5289)

## 2.8.3 (2023-08-22)

* Drop support of Ubuntu Kinetic

## 2.8.2 (2023-08-22)

* Add Ubuntu Mantic Support
* Use Multi-Step to build Docker image
* Update layout of file statistics to display a single day
* Stop sending notification for ignored days #284
* Handle warning exit code 2 return by rdiff-backup version 2.2

## 2.8.1 (2023-08-01)

* Pin version of selenium to v4.10

## 2.8.0 (2023-07-31)

* Log detailed error message when restore command failed to help debugging
* Update interface used to manage users to be more user friendly #237
* Disable Disk Quota in users view when quota command is not configured #237
* Hide LDAP label in users view when LDAP is not configured #237
* Allow administrator to change user's reporting preferences
* Add support for Ubuntu Lunar
* Add support for SQLAlchemy v2.0 for forward compatibility
* When reaching 100% disk usage, show quota in red to improve visibility
* Send notification when user's quota reach 90% #46
* Add ratelimit to "send me a status report" to avoid email flooding #272 - credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Fix creation of access token with expiration time #277
* Allow user to disable notification for selected day of week #278
* Add detailed file statistics to show created, modified and deleted files #103
* Trim spaces on verification code to improve usability #279
* Determine default username when user get redirected to login page #283
* Sort repository by dates in administration view #282
* Document how to configure fail2ban to improve server hardening
* Document how to configure certbot for automatic SSL certificate generation
* Update installation steps to include `arch=amd64`
* Update french translation

## 2.7.1 (2023-04-27)

* Fix encoding problem with older Outlook 2007 client #273

## 2.7.0 (2023-04-20)

* Support Python 3.11
* Provide a Monthly, Weekly or Daily repport for user #71
* Fix MFA verification code email's subjet #270
* Add translation for footer not in email layout
* Send email to administrator when a new version is available #266
* Improve automatic testing

## 2.6.1 (2023-03-22)

* Refused to start if `rdiff-backup` executable is not found #267

## 2.6.0 (2023-03-15)

* Review the application layout to use Fluid container to use all the space available on the screen
* Rename status view to Dashboard
* Display more useful data in Dashboard view: Backups per days, Oldest backup, Storage Usage, Average duration, Least Active, Most active
* Fix deletion confirmation of repositories within subdirectory #250
* Properly clean-up plain text email from HTML tags
* Send notification for inactive backup based on statistics
* Send notification using a new template following the web interface branding
* Send notification to user when repository get added or removed
* Send all notification to an optional "catch-all" email address configured using `--email-catch-all` option #258
* Redistribute logos in PNG format for better compatibility
* Disable error page logs for 4xx errors
* Add username and IP address to logs only for HTTP Request
* Fix LDAP integration to support non-list attributes - credit to [Shane Robinson](https://gitlab.com/shanesq)
* Add support of multiple required-group for LDAP integration
* Improve System Logs view to identify "User Activity", "Threats" and "User Login"
* Fix display of "* minutes ago" #264
* Add `default-lang` option to configure default language #263
* Allow user to select a preferred language #263
* Use user's preferred language when sending notifications #263

## 2.5.8 (2023-02-19)

* Support Setuptools v66 for compatibility with Debian Bookworm
* Fix execution of rdiffweb remove-older job to clean-up repository history #262

## 2.5.7 (2023-01-27)

* Enforce SQLAlchemy version between 1.2 or 1.4

## 2.5.6 (2023-01-11)

* Fixed display of Hamburger menu on mobiles (minarca#192)
* Change wording for interupted backup

## 2.5.5 (2022-12-23)

* Fix loading of Charts in Status page
* Ensure Gmail and other mail client doesn't create hyperlink automatically for any nodification sent by Rdiffweb to avoid phishing - credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Sent email notification to user when a new SSH Key get added - credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Ratelimit "Resend code to my email" in Two-Factor Authentication view - credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Username are not case-insensitive - credits to [raiders0786](https://www.linkedin.com/in/chirag-agrawal-770488144/)
* Make sure that all ssh keys are unique, regardless of the user - credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Disable translation caching

Breaking changes:

* Username with different cases (e.g.: admin vs Ammin) are not supported. If your database contains such username make sure to remove them before upgrading otherwise Rdiffweb will not start.

## 2.5.4 (2022-12-19)

* Discard `X-Forwarded-Host` headers credit to [Anishka Shukla](https://github.com/anishkashukla)
* Create proper symbolic link of `chartkick.js` on Ubuntu Jammy to fix loading of Charts in web interface
* Add CSRF verification on `/logout` credits to [reza.duty](https://rezaduty.me)

## 2.5.3 (2022-12-05)

* Add support for WTForms v3 to support Debian Bookworm
* Fix strange behavior in access token management #247

## 2.5.2 (2022-11-28)

* Block repository access when user_root directory is empty or relative path [CVE-2022-4314](https://nvd.nist.gov/vuln/detail/CVE-2022-4314) credit to [neverjunior](https://github.com/neverjunior)
* Replace admin password only when `--admin-password` option is provided #246
* Invalidate browser cache for `logo`, `headerlogo` and `favicon` on restart #245

## 2.5.1 (2022-11-11)

* Add support for Ubuntu Kinetic #240
* Disable filesize for deleted files to improve page loading #241

## 2.5.0 (2022-11-09)

This next release focus on two-factor-authentication as a measure to increase security of user's account.

* Store User's session information into database
* Update ldap plugin to load additional attributes from LDAP server
* Improve `/status` page error handling when `session_statistics` cannot be read
* Add support for Ubuntu Jammy
* Upgrade from Bootstrap v3 to v4 #204
* Replace Fontello by Font-Awesome v4
* Use CSS variables `var()` to customize themes using `--branding-X` options #239
* Remove usage of Jquery.validate
* Replace custom timsort by jquery DataTables #205
* Add Active Session managements #203
  * Active session should be visible in user's profiles
  * Active session may be revoked by user
  * Active session should be visible in administration view
  * Action session may be revoke by administrator
  * Show number of active users within the last 24 hours in dashboard
* Handle migration of older Rdiffweb database by adding the missing `repos.Encoding`, `repos.keepdays` and `users.role` columns #185
* Replace deprecated references of `disutils.spawn.find_executable()` by `shutil.which()` #208
* Add two-factor authentication with email verification #201
* Generate a new session on login and 2FA #220
* Enforce permission on /etc/rdiffweb configuration folder
* Enforce validation on fullname, username and email
* Limit incorrect attempts to change the user's password to prevent brute force attacks #225 [CVE-2022-3273](https://nvd.nist.gov/vuln/detail/CVE-2022-3273) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Enforce password policy new password cannot be set as new password [CVE-2022-3376](https://nvd.nist.gov/vuln/detail/CVE-2022-3376) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Enforce better rate limit on login, mfa, password change and API [CVE-2022-3439](https://nvd.nist.gov/vuln/detail/CVE-2022-3439) [CVE-2022-3456](https://nvd.nist.gov/vuln/detail/CVE-2022-3456) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Enforce 'Origin' validation [CVE-2022-3457](https://nvd.nist.gov/vuln/detail/CVE-2022-3457) credit to [Nithissh12](Nithissh12)
* Define idle and absolute session timeout with agressive default to protect usage on public computer [CVE-2022-3327](https://nvd.nist.gov/vuln/detail/CVE-2022-3327) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Send email notification when enabling or disabling MFA [CVE-2022-3363](https://nvd.nist.gov/vuln/detail/CVE-2022-3363) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Use Argon2id to store password hash #231
* Fixed plugin priorities to ensure that jobs are scheduled at each startup #232
* Revoke previous user's sessions on password change [CVE-2022-3362](https://nvd.nist.gov/vuln/detail/CVE-2022-3362) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)

Breaking changes:

* Drop Ubuntu Hirsute & Impish (End-of-life)
* `session-dir` is deprecated and should be replace by `rate-limit-dir`. User's session are stored in database.
* previous `.css` customization are not barkward compatible. Make usage of the `--branding-X` options.

**Thanks to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172) with whom I collaborate to improve the security of this project.**

## 2.4.10 (2022-10-03)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Mitigate path traversal vulnerability [CVE-2022-3389](https://nvd.nist.gov/vuln/detail/CVE-2022-3389) credit to [Hoang Van Hiep](https://www.linkedin.com/in/hiephv2410/)

## 2.4.9 (2022-09-28)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Add `Cache-Control` and other security headers [CVE-2022-3292](https://nvd.nist.gov/vuln/detail/CVE-2022-3292) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Enforce password policy using `password-score` based on [zxcvbn](https://github.com/dropbox/zxcvbn) [CVE-2022-3326](https://nvd.nist.gov/vuln/detail/CVE-2022-3326) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)

## 2.4.8 (2022-09-26)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Clean-up invalid path on error page
* Limit username field length [CVE-2022-3290](https://nvd.nist.gov/vuln/detail/CVE-2022-3290) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Limit user's email field length [CVE-2022-3272](https://nvd.nist.gov/vuln/detail/CVE-2022-3272) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Limit user's root directory field length [CVE-2022-3295](https://nvd.nist.gov/vuln/detail/CVE-2022-3295) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)
* Limit SSH Key title field length [CVE-2022-3298](https://nvd.nist.gov/vuln/detail/CVE-2022-3298) credit to [Nehal Pillai](https://www.linkedin.com/in/nehal-pillai-02a854172)

## 2.4.7 (2002-09-21)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Generate a new session on login and 2FA #220 [CVE-2022-3269](https://nvd.nist.gov/vuln/detail/CVE-2022-3269) credit to [Ambadi MP](https://www.linkedin.com/in/ambadi-m-p-16a95217b/)
* Mitigate CSRF on user's settings #221 [CVE-2022-3274](https://nvd.nist.gov/vuln/detail/CVE-2022-3274) credit to [irfansayyed](https://github.com/irfansayyed-github)

## 2.4.6 (2022-09-20)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Support MarkupSafe<3 for Debian bookworm
* Mitigate CSRF on user's notification settings #216 [CVE-2022-3233](https://nvd.nist.gov/vuln/detail/CVE-2022-3233) credit to [Ambadi MP](https://www.linkedin.com/in/ambadi-m-p-16a95217b/)
* Mitigate CSRF on repository settings #217 [CVE-2022-3267](https://nvd.nist.gov/vuln/detail/CVE-2022-3267) credit to [irfansayyed](https://github.com/irfansayyed-github)
* Use 'Secure' Attribute with Sensitive Cookie in HTTPS Session on HTTP Error #218 [CVE-2022-3174](https://nvd.nist.gov/vuln/detail/CVE-2022-3174) credit to [Chuu](https://github.com/uonghoangminhchau)

## 2.4.5 (2002-09-16)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Mitigate CSRF on repository deletion and user deletion [CVE-2022-3232](https://nvd.nist.gov/vuln/detail/CVE-2022-3232) #214 #215 credit to [Ambadi MP](https://www.linkedin.com/in/ambadi-m-p-16a95217b/)

## 2.4.4 (2002-09-15)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Use `X-Real-IP` to identify client IP address to mitigate Brute-Force attack #213

## 2.4.3 (2022-09-14)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Mitigate CSRF in profile's SSH Keys [CVE-2022-3221](https://nvd.nist.gov/vuln/detail/CVE-2022-3221) #212 credit to [Ambadi MP](https://www.linkedin.com/in/ambadi-m-p-16a95217b/)

## 2.4.2 (2022-09-12)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Use 'Secure' Attribute with Sensitive Cookie in HTTPS Session. [CVE-2022-3174](https://nvd.nist.gov/vuln/detail/CVE-2022-3174) #209 credit to [Chuu](https://github.com/uonghoangminhchau)
* Avoid leakage of the stack trace in the default error page. [CVE-2022-3175](https://nvd.nist.gov/vuln/detail/CVE-2022-3175) #210 credit to [Chuu](https://github.com/uonghoangminhchau)
* Enforce minimum and maximum password length [CVE-2022-3175](https://nvd.nist.gov/vuln/detail/CVE-2022-3179) #211 credit to [Chuu](https://github.com/uonghoangminhchau)

## 2.4.1 (2022-09-08)

This releases include a security fix. If you are using an earlier version, you should upgrade to this release immediately.

* Add Clickjacking Defense [CVE-2022-3167](https://nvd.nist.gov/vuln/detail/CVE-2022-3167) credit to [tharunavula](https://github.com/tharunavula)
* Drop Ubuntu Hirsute & Impish (End-of-life)

## 2.4.0 (2022-06-21)

This new release brings a lot of improvement since the last version, multiple bug fixes
to make the application stable. A couple of new features to improve the overall
usability and a new security feature to block a brute force attack.

* Add RateLimit to login page and API to mitigate robots attacks #167
* Send email notification only if `email-sender` option is defined to avoid raising exception in logs #176
* Support file restore cancellation without leaving `rdiffweb-restore` process in `<defunct>` state #174
* Replace `python-ldap` by `ldap3` a pure python implementation to avoid dependencies on `sasl` and `ldap` binaries #186
* Reffactor core module to allow better extendability and reusability #183
* Add support for Debian Bookworm #180
* Add support for Ubuntu Impish #175
* Add rdiff-backup version to administration view
* Run unit test during Debian build package
* Refresh repository list automatically when required #188 #189
* Fix error 500 displayed in status page #191
* Improve repository browsing speed by minimizing the number of I/O call #192
* Publish Docker image directly to DockerHub #144
* Add REST API to manage sshkeys

Breaking changes:

* Ldap Password changes is not supported anymore.
* Ldap Check Shadow expire config is not supported anymore. It should be replace by a custom filter.
* Drop CentOS 7 and CentOS 8 support

## 2.3.9 (2022-01-05)

Maintenance release to fix minor issues

* Improve date parsing for `backup.log` to avoid printing exception in logs #170
* Return HTTP error 403 for invalid symlink to avoid returning a misleading HTTP 500 Server Error #168
* Show a user friendly error message when trying to create a new user with an existing username #169
* Handle repository without last-backup date during the notification process to ensure notifications are sent #171
* Replace CherryPy `storage_type` by `storage_class` to avoid warning in logs
* Update code to avoid deprecation warning where applicable
* Add Flake8 validation to improve code quality
* Remove Ubuntu Groovy support

## 2.3.8 (2021-12-01)

* Push all artefacts to nexus server including binaries and documentation
* Fix `Chart.js` loading on Debian bullseye #164
* Update installation steps documentation
* Improve LDAP authentication to lookup entire directory
* Fix usage of `--ldap-add-user-default-userroot` to avoid error related to wrong encoding
* Improve authentication mechanics
* Avoid raising an HTTP error 500 when login form receive invalid payload
* Mitigate open redirect vulnerability in login form

## 2.3.7 (2021-10-21)

* To avoid backward compatibility issue, revert CSRF Token validation
* Mitigate CSRF vulnerability using cookies with `SameSite=Lax`
* Mitigate CSRF vulnerability by validating the `Origin` header when a form is submited
* Improve usage of WTForm for all form validation
* Update installation stepd for debian #162
* Build Ubuntu packages and publish them to our APT repo

## 2.3.6 (2021-10-20)

* Broken build

## 2.3.5 (2021-10-18)

* Mitigate CSRF vulnerability to user, ssh and repo management with CSRF Token

## 2.3.4 (2021-09-20)

* Skip email notification if `email-host` configuration is not provided #157
* Skip email notification when the new attribute value has the same value #159
* USE LDAP `mail` attribute when creating new user from LDAP directory #156

## 2.3.3 (2021-09-10)

* Provide a new theme `blue` to match IKUS Soft colors #158

## 2.3.2 (2021-09-07)

* Automatically update user's repository list based on user's home directory

## 2.3.1 (2021-07-14)

* Update default `session-dir` location to `/var/lib/rdiffweb/session` to avoid using `/var/run` #148

## 2.3.0 (2021-07-06)

* Improve timezone handling to display date with local timezone using javascript #143
* Improve charts by replacing d3js by chartkick #122
* Replace the status view by something meaningful with chartkick #122
* Provide Docker image with Rdiffweb `docker pull ikus060/rdiffweb` #55
* Fix file and folder sorting #143

## 2.2.0 (2021-05-11)

* Debian package:
  * Add rdiff-backup as dependencies to comply with Debian packaging rules
  * Multiple other fixed to control files
  * Use debhelper-compat (= 13)
  * Use debhelper-compat (= 13)
  * Run test during packaging
  * Create default folder `/var/run/rdiffweb/sessions` to store user session
* Use ConfigArgPare for configuration to support configuration file, environment variables and arguments to configure rdiffweb #114
* Fix cache in localization module
* Add `ldap-add-default-role` and `ldap-add-default-userroot` option to define default value for role and user root when creating user from LDAP #125
* Support PostgreSQL database by replacing our storage layer by SQLAlchemy #126
* Fix to retrieve user quota only for valid user_root #135
* Add option `disable-ssh-keys` to disable SSH Key management
* Use absolute URL everywhere
* Add support for `X-Forwarded-For`, `X-Forwarded-proto` and other reverse proxy header when generating absolute URL
* Drop Debian Stretch support
* Implement a new background scheduler using apscheduler #82
* Use background job to send email notification to avoid blocking web page loading #47
* Use background job to delete repository to avoid blocking web page loading #48
* Allow deleting a specific file or folder from the history using `rdiff-backup-delete` #128
* Improve support for `session-dir` #131
* Add option `admin-password` to define administrator password for better security
* Improve performance of repository browsing
* Add a new view to display logs of a specific repository
* Allow downloading the log
* Define a default limit to graph statistics to make it display faster
* Fix `get-quota-cmd` option to properly return a value

## 2.1.0 (2021-01-15)

* Debian package: Remove dh-systemd from Debian build dependencies (<https://bugs.debian.org/871312we>)
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

## 2.0.0 (2020-12-04)

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
