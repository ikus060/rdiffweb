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

from __future__ import unicode_literals

import cherrypy
import logging
import os
import pkg_resources
import rdw_config
import rdw_plugin
import rdw_templating

from user import UserManager
from page_admin import AdminPage
from page_browse import BrowsePage
from page_history import HistoryPage
from page_locations import LocationsPage
from page_login import LoginPage
from page_logout import LogoutPage
from page_prefs import PreferencesPage
from page_restore import RestorePage
from page_settings import SettingsPage
from page_status import StatusPage

# Define the logger
logger = logging.getLogger(__name__)


class RdiffwebApp(LocationsPage):
    """This class represent the application context."""

    def __init__(self, configfile=None):

        # Initialise the configuration
        self.load_config(configfile)

        # Initialise the template enginge.
        self.templates = rdw_templating.TemplateManager()

        # Initialise the plugins
        self.plugins = rdw_plugin.PluginManager(self.config)

        # Setup pages.
        self.login = LoginPage(self)
        self.logout = LogoutPage(self)
        self.browse = BrowsePage(self)
        self.restore = RestorePage(self)
        self.history = HistoryPage(self)
        self.status = StatusPage(self)
        self.admin = AdminPage(self)
        self.prefs = PreferencesPage(self)
        self.settings = SettingsPage(self)

        # Activate every loaded plugin
        self.plugins.run(lambda x: self.activate_plugin(x))

        # create user
        self.userdb = UserManager(self)

        # Init Component
        LocationsPage.__init__(self, self)

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
        self.config = rdw_config.Configuration(configfile)

        # Define TEMP env
        tempdir = self.config.get_config_str("TempDir", default="")
        if tempdir:
            os.environ["TMPDIR"] = tempdir


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


class CurrentUser():

    def __init__(self, userdb, username):
        self._userdb = userdb
        self._username = username

    def __get_username(self):
        return self._username

    username = property(fget=__get_username)
    is_admin = property(fget=_getter('is_admin'))
    email = property(fget=_getter('get_email'))
    root_dir = property(fget=_getter('get_root_dir'))
    repos = property(fget=_getter('get_repos'))
