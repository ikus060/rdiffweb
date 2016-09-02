# Latest

* Add a `limit` parameter to history page. Fix #7
* Force URL encoding ISO-8859-1 in py3 and cherrypy >= 5.5.0
* Remove funcsigs from dependencies
* Provide a tox configuration.
* Change nosetests verbosity
* Change requirement to babel >= 1.3
* Fix bug github/#65 in status.xml reported by bahamut45.
* Add path to librdiff exception.
* Upgrade cherrypy version to 3.5.0 to run around a bug.
* Fix package name python2 > python
* Add nginx config file to extras
* Update docs with nginx config.
* Remove trailing slash (/) from restore URLs
* Enable profiling when any --profile-* arguments is used.
* Replace login/logout page with a cherrypy tool.
* Allow plugin to add extra head.
* Change a bit the restore url to allow multiple kind
* Make a plugin from encoding settings.
* Make alerts messages dismissible.
* Fix notifications plugins to set max age. Fix #28
* Support remove_older by executing rdiff-backup command line.
* Reverse ordering of activate and add templates.
* Create a new JobPlugin to centralize code for fixed time execution.
* Change style of remove_older template.
* Add icons & colors to ajax form submit.
* Add `ok` icon to fontello.
* Add RemoveOlder plugin.
* Change location of javascripts. Add ajax form submit.
* Add `set_attr` and `get_attr` for repos.
* Add `attention` icons to fontello.less
* Make sure to add all `templates_content` to settings page.
* Fix locations templates to show all `templates_before_content`
* Refactor user library again to remove get_* and set_*.
* Update templates to set the right activate page.
* Make 'build_less' optional.
* Return false if resource_filename doesn't exists.
* Fix graphs browsing to `data` for python 3.
* Fix typo in default configuration comments.
* Add documentation about authentication.
* Relayout the download button in restore folder page.
* Remove useless border-bottom-right-* from login widget.
* Add text to static() assertion.
* Upgrade to basic Bootstrap 3.3.6 (default theme).
* Fix Graphs plugin to receive poppath are bytes.
* Fix poppath to read args using unquote.
* Replace Grunt by lessc. Relocated main.css.
* Serve favicon.ico using a page handler.
* Replace configuration by decorator for login page.
* Move delete repo into a plugins.
* Replace _cp_dispatch by class decorators.
* Enable Graphs plugin by default.
* Fix pages title in layout_repo.html
* Create a markdown file to hold all documentation. See pdsl-www/#63
* Compute next execution time once notifications are sent. see #3
* Add Graphs plugin. See #11
* Improve librdiff file statistics
* Add some icon to fontello
* Update layouts to support configurable nav bar.
* Make sure to log the exception shown using default error page.
* Remove obsolete `from builtins import object` from rdw_app
* Add test coverage to page_restore.
* Add Test coverage for page_prefs.
* Add test coverage for settings page.
* Change error handling in locations page. see #17
* Continue updating error handling to avoid using ValueError.
* Replace any call to _compile_error_template by an HTTPError
* Alway show header name in title
* Replace default error page by a nice one. see #17
* Enhance the logging configuration. see #24
* Remove debug flag when restoring files.
* Add mail notification. see #3
* Use UserObject as current user. Add RepoObject.
* Recover plugin description. Lost when migrating plugin.
* Support repo without backup date.
* In HTML templates replace non-breaking space (\xC2\xA0) by space.
* Fix archive encoding. See pdsl/minarca#121
* Continue to enhance content-disposition. see pdsl/minarca#120
* Fix content-disposition for file and archive. See pdsl/minarca#120
* Reorganize import in filter_authentication
* Fix small encoding issue with authform redirection.
* Quick implementation of UserObject.
* Fix archiver to support python < 2.7.3
* Pipe archive creation. see #8
* Add debug signal to dump thread.
* Reorganize jinja2 template to use extends
* Fix FavIcon and HeaderLogo support.
* Disable test_gc (because it randomly fail).
* Convert Yapsy plugin into entry_point plugins.
* Fix regression - support single repository browsing
* Re-organize i18n
* Add profiling option `--profile`
* Replace deprecated warn() by warning()
* Add logging to know how long it take to restore a file.
* Add directory in Zip archive.
* Ignore encoding problem in spider repos
* Fix attrib testcases (for py3)
* Add file recursively to tar.gz.
* Update testcases.tar.gz to include a sub directory with encoding.
* Add new {% attrib %} See pdsl/rdiffweb#12
* Review all logger modulo (%) formatting. See #9
* Add log to page_admin (for debugging)
* Add integration test and make it work in py2 and py3
* Major change to support py2 and py3
* Refactor plugin ILocationsPagePlugin into ITemplateFilterPlugin.
* Convert update repos into core plugin.
* Start fixing spider repo auto refresh

# Release 0.8.1

* Set owner for authorized_keys. pdsl/minarca#100
* refactor some code to use list comprehension syntax in librdiff
* Fix change_dates ordering. see pdsl/minarca#97
* Send logined notification at the right time.
* Add logined notification.
* Fix creation of admin user when creating database.
* Remove initscript, default config and logrotate from setup.py.
* Improve in_progress detection -- verify if PID is running
* Add msapplication meta tag (for Win8 pinning) see #57
* Support translated Welcome message.
* Add a bit of logging into page_settings.
* Fix password check unicode.
* Fix change email.
* Fix allow add user if missing.
* Fix ldap unicode vs str.
* Update default configuration. Remove obsolete UserDB option.
* Reffactor RdiffApp to implement Application directly.
* Add nosetests config to setup.cfg
* Refactor user & password system
* Remove file_statistics cache replace by pure python implementation.
* Try to support 'X-Forwarded-For' header.
* Add log line when login failed.
* Add ip and username in log.
* Try to fix encoding normalization.
* Allow HTML in "WelcomeMsg". Ref #76
* Allow user to delete repository.
* Fix ssh keys plugin to create file and directory.
* Add new "settings" tabs to change encoding. Ref #52
* Reffactor browsing view a bit (to introduce Settings) Ref #52 #57
* Fix issue related to SSH Prefs page not being available.
* Add ru translation received by Евгений Максимов <me@vragam.net>
* Add RLock to SQLite user db.
* Add options to customize the welcome message.
* Remove setup page and auto configure rdiffweb when required.
* Provide a default info message if userprefs are not availables.
* Use SQLite UserDB by default. Fix default configuration file.
* Fix ZIP operation to use ISO-8859-1 encoding for filenames. Fix #55
* Reffactoring replace remove_dir() by shutil.rmtree()
* Set a error page to workarround encoding in error in cherrypy.
* Add threadname to logging line.
* Correction to the temp file name generate to use a prefix.
* Use weakref in librdiff in attempt to fix memoryleak. refs #52
* Prefix temp directory with rdiffweb.
* Add itemprop=id for sshkeys.
* Change default filesize format to use GiB and not GB
* Localize some string related to password validation.
* Don't check SSH key length in autorizedkeys. Use Crypto to get key length. Correct field name in template: comment -> title.
* Add email validation
* Add SSH Keys plugin to manage authorized_keys
* Set cherrypy max_request_body_size to 2MiB to increase security.
* Create a CurrentUser object to lazy load data about current user. Refactor the preferences page to use plugins architecture.
* Dump memory when receiving SIGUSR2.
* Add 'START' and 'STOP' log line to clearly identify startup.
* Remove obsolete https filter.
* Add microdata to plugin page.
* Remove hardcoded version. Get it from package info.
* Move forward a plugin architecture. First implementation include UserDB plugins: LDAP and SQLite. MySQL is on the way.
* Correct librdiff to avoid encoding problem during logging.
* Correct i18n to fallback when translation is not available to current resquest/response.
* Correct basic auth (for RSS feed).
* Cache configuration setting. Use unicode string in every module.
* Remove ref url from readme file.

# v.0.7.0

* Enhance repository view. Reduce item size. Include number of repos in title.
* Change logrotate configuration to copytruncate the file.
* Correction to init script. Use >> instead of > to write log file.
* Upgrade Bootstrap to 3.3.4. Align dropdown menu in xs. Fix #43
* Align the "delete" buttons. Fix #42
* Hide "Signed in as..." for xs and sm. Fix #41
* Change the navigation layout to avoid showing bootstrap menu button in loging page. Fix #40
* Fix LDAP TLS.
* Change filter setup to redirect users to setup page if no user in database.
* Avoid replacing configuration file rdw.conf.
* Include a logrotate configuration to setup.py
* Declare license information in setup.py
* Fix init script. Fix problem related to logs, background process.
* Remove userdb cache. Ref #38
* Add python-babel to list of dependencies to compile the translation.
* Translate rdiffweb to french. Provide translation based on browser accepted language.
* Set rdiffweb branding
* Update login page format
* Support symbolic link by showing the target directory content. Fix #30

* Fix tempdir encoding.
* Update init script to fix some issue related to starting rdiffweb.
* Update install instruction in README.md
* Remove reference to "rdiffweb-config".
* Add "tempdir" configuration parameter to relocate where to restore data.
* Add copyright statement where missing. Update satement to 2014.
* Minor UI improvement for mobile
* Change the setup to create a default admin users.
* Before validating LDAP credentials, check if user exists in local database.
* Fix login redirect for edge cases when url need quote. Redirect doesn't work for non-utf-8 chars.
* Handle situation where UserRoot is None.
* Correct encoding error in db_sqlite and db_ldap to support username and password with non-ascii characther.
* Change authentication filter to redirect to /login/.
* Enhance administration view.
* Fix setup to include javascripts.
* Provide hint when no backup locations is available.
* Enhance initial setup.
* Fix restore to delete temporary directory when download is complete.
* Use permalink
* Remove zip vs tar preference. Allow user to select when restoring. Fix #23
* Add new fontello icons.
* Fix sorting to display directory first.
* Fix filesize for quoted path.
* Rename all variation of rdiff-web, rdiffWeb into rdiffweb. Fix #24
* Change GUI to bootstrap. Update templating engine to jinja2
* Update author information.
* Add LDAP authentication support.
* Add logging error to page restore.
* Fix encoding support for file and folder restore.
* Show error message instead of "Invalid date parameter."
* Fix encoding issue when creating archive

# Release v0.6.5

* Change sorting implementation to use TimSort.
* Minor modification to CSS to add more focus to warnings and errors.
* Minor change to color palette.
* Modification to CSS and templates for better support on mobile devices. Fix #4
* Add arrow to indicate the sorting direction.
* Save sorting preference in local storage. Restore the user preference on page load. Fix #1
* Add license informations to source file and package info.
* Validate pages using w3c validator againts HTML5.
* Add column sorting using JavaScript. Use css :nth-child(even) to replace altRow implementation.
* Refactor librdiff.py to fix handling of different timezone for the same increment. Fix #2
* Minor realignment of the login screen using css.
* Change the creation of the status entry url to make it relative instead of absolute.

# Release V0.6.4

* Update readme file with installation instruction.
* Make the web server listen on all network interface by default.
* Change the repository icon and the favicon.
* Use modal dialog to add user in admin panel.
* Add rdiffWeb branding
* Use overlay to select revision to be restored.
* Remove deprecated emailsEnabled section.
* Fix minor issue with deployment script. Redesign the pages with modification to templates and CSS. Add JQuery.

# Release v0.6.3
* Initial commit
