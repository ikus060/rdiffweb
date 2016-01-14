#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import absolute_import
from __future__ import unicode_literals

from builtins import object
from cherrypy import Application
import cherrypy
from cherrypy.process.plugins import Monitor
import logging
import os
import pkg_resources

from rdiffweb import filter_authentication  # @UnusedImport
from rdiffweb import i18n  # @UnusedImport
from rdiffweb import rdw_config
from rdiffweb import rdw_plugin
from rdiffweb import rdw_templating
from rdiffweb.page_admin import AdminPage
from rdiffweb.page_browse import BrowsePage
from rdiffweb.page_history import HistoryPage
from rdiffweb.page_locations import LocationsPage
from rdiffweb.page_login import LoginPage
from rdiffweb.page_logout import LogoutPage
from rdiffweb.page_prefs import PreferencesPage
from rdiffweb.page_restore import RestorePage
from rdiffweb.page_settings import SettingsPage
from rdiffweb.page_status import StatusPage
from rdiffweb.user import UserManager
from future.utils import native_str


# Define the logger
logger = logging.getLogger(__name__)


class Root(LocationsPage):

    def __init__(self, app):
        LocationsPage.__init__(self, app)
        self.login = LoginPage(app)
        self.logout = LogoutPage(app)
        self.browse = BrowsePage(app)
        self.restore = RestorePage(app)
        self.history = HistoryPage(app)
        self.status = StatusPage(app)
        self.admin = AdminPage(app)
        self.prefs = PreferencesPage(app)
        self.settings = SettingsPage(app)


class RdiffwebApp(Application):
    """This class represent the application context."""

    def __init__(self, configfile=None):

        # Initialise the configuration
        self.load_config(configfile)

        # Initialise the template enginge.
        self.templates = rdw_templating.TemplateManager()

        # Initialise the plugins
        self.plugins = rdw_plugin.PluginManager(self.cfg)

        # Initialise the application
        cwd = os.path.abspath(os.path.dirname(__file__))
        config = {
            native_str('/'): {
                'tools.authform.on': True,
                'tools.i18n.on': True,
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.gzip.on': True,
                'tools.sessions.on': True,
            },
            native_str('/favicon.ico'): {
                'tools.authform.on': False,
                'tools.staticfile.on': True,
                'tools.staticfile.filename': os.path.join(cwd, 'static', 'favicon.ico'),
            },
            native_str('/login'): {
                'tools.authform.on': False,
            },
            native_str('/static'): {
                'tools.staticdir.on': True,
                'tools.staticdir.root': cwd,
                'tools.staticdir.dir': "static",
                'tools.authform.on': False,
            },
        }
        self._setup_favicon(config)
        self._setup_header_logo(config)
        self._setup_session_storage(config)
        Application.__init__(self, root=Root(self), config=config)

        # Activate every loaded plugin
        self.plugins.run(lambda x: self.activate_plugin(x))

        # create user manager
        self.userdb = UserManager(self)

        # Start deamon plugins
        self._start_deamons()

    def activate_plugin(self, plugin_obj):
        """Activate the given plugin object."""
        plugin_obj.app = self
        plugin_obj.activate()
        # Add templates location to the templating engine.
        if plugin_obj.get_templatesdir():
            self.templates.add_templatesdir(plugin_obj.get_templatesdir())

    def __get_currentuser(self):
        """
        Get the current user.
        """
        try:
            username = cherrypy.session['username']  # @UndefinedVariable
        except:
            username = False
        if not username:
            return None

        # Check if object already exists.
        if not hasattr(cherrypy.request, 'user'):
            cherrypy.request.user = CurrentUser(self.userdb, username)
        return cherrypy.request.user  # @UndefinedVariable

    currentuser = property(fget=__get_currentuser)

    def get_version(self):
        """
        Get the current running version (using package info).
        """
        # Use a cached version
        if hasattr(self, "_version"):
            return self._version
        # Get version.
        try:
            self._version = pkg_resources.get_distribution("rdiffweb").version
        except:
            self._version = "DEV"
        return self._version

    def load_config(self, configfile=None):
        """Called during app creating to load the configuration from file."""
        self.cfg = rdw_config.Configuration(configfile)

        # Define TEMP env
        tempdir = self.cfg.get_config("TempDir", default="")
        if tempdir:
            os.environ["TMPDIR"] = tempdir

    def _setup_favicon(self, config):
        """
        Used to add an entry to the page setting if the FavIcon configuration is
        defined.
        """
        favicon = self.cfg.get_config("FavIcon")
        if not favicon:
            return

        # Append custom favicon
        if (not os.path.exists(favicon) or
                not os.path.isfile(favicon) or
                not os.access(favicon, os.R_OK)):
            logger.warn("""path define by FavIcon doesn't exists or is no
                        accessible: %s""", favicon)
            return

        logger.info("use custom favicon: %s", favicon)
        basename = os.path.basename(favicon)
        self.favicon = '/%s' % (basename)
        config.update({
            self.favicon: {
                'tools.authform.on': False,
                'tools.staticfile.on': True,
                'tools.staticfile.filename': favicon,
            }
        })

    def _setup_header_logo(self, config):
        """
        Used to add an entry to the page setting if the FavIcon configuration is
        defined.
        """
        header_logo = self.cfg.get_config("HeaderLogo")
        if not header_logo:
            return
        # Append custom header logo
        if (not os.path.exists(header_logo) or
                not os.path.isfile(header_logo) or
                not os.access(header_logo, os.R_OK)):
            logger.warn("path define by HeaderLogo doesn't exists: %s",
                        header_logo)
            return

        logger.info("use custom header logo: %s", header_logo)
        basename = os.path.basename(header_logo)
        self.header_logo = '/%s' % (basename)
        config.update({
            self.header_logo: {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': header_logo,
                'tools.authform.on': False,
            }
        })

    def _setup_session_storage(self, config):
        # Configure session storage.
        session_storage = self.cfg.get_config("SessionStorage")
        session_dir = self.cfg.get_config("SessionDir")
        if session_storage.lower() != "disk":
            return

        if (not os.path.exists(session_dir) or
                not os.path.isdir(session_dir) or
                not os.access(session_dir, os.W_OK)):
            return

        logger.info("Setting session mode to disk in directory %s", session_dir)
        config.update({
            'tools.sessions.on': True,
            'tools.sessions.storage_type': True,
            'tools.sessions.storage_path': session_dir,
        })

    def _start_deamons(self):
        """
        Start deamon plugins
        """
        logger.debug("starting deamon plugins")

        def start_deamon(p):
            Monitor(cherrypy.engine,
                    p.deamon_run,
                    frequency=p.deamon_frequency,
                    name="DeamonPlugin").subscribe()

        self.plugins.run(start_deamon, category='Daemon')


def _getter(field):
    """
    Getter to fetch field from CurrentUser.
    """
    def get_field(x):
        attrname = '__%s' % (field,)
        if not hasattr(x, attrname):
            func = getattr(x._userdb, field)
            value = func(x._username)
            setattr(x, attrname, value)
        return getattr(x, attrname)

    return get_field


class CurrentUser(object):

    def __init__(self, userdb, username):
        self._userdb = userdb
        self._username = username

    def __get_username(self):
        return self._username

    username = property(fget=__get_username)
    is_admin = property(fget=_getter('is_admin'))
    email = property(fget=_getter('get_email'))
    root_dir = property(fget=_getter('get_user_root'))
    repos = property(fget=_getter('get_repos'))
