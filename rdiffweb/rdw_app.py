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

import page_admin
import page_browse
import page_history
import page_locations
import page_restore
import page_status
import page_prefs
import page_login
import page_logout
import page_settings
import rdw_plugin
import rdw_config
from rdiffweb import rdw_templating

# Define the logger
logger = logging.getLogger(__name__)


class RdiffwebApp(page_locations.LocationsPage):
    """This class represent the application context."""

    def __init__(self, configfile):

        # Initialise the configuration
        self.config = rdw_config.Configuration()
        if configfile:
            self.config.set_config_file(configfile)

        # Define TEMP env
        tempdir = self.config.get_config_str("TempDir", default="")
        if tempdir:
            os.environ["TMPDIR"] = tempdir

        # Initialise the template enginge.
        self.templates = rdw_templating.TemplateManager()

        # Initialise the plugins
        self.plugins = rdw_plugin.PluginManager(self.config)

        # Setup pages.
        self.login = page_login.LoginPage()
        self.logout = page_logout.LogoutPage()
        self.browse = page_browse.BrowsePage()
        self.restore = page_restore.RestorePage()
        self.history = page_history.HistoryPage()
        self.status = page_status.StatusPage()
        self.admin = page_admin.AdminPage()
        self.prefs = page_prefs.PreferencesPage()
        self.settings = page_settings.SettingsPage()

        # Activate every loaded plugin
        self.plugins.run(lambda x: x.activate_with_app(self))

        # Add templates location to the templating engine.
        self.plugins.run(lambda x:
                         x.get_templatesdir() is None or
                         self.templates.add_templatesdir(x.get_templatesdir()))

    def __get_userdb(self):
        """
        Return reference to the user database. Create a new instance of user
        db if it doesn't exists.
        """

        # Check if already exists.
        if hasattr(self, "_userdb") and self._userdb:
            return self._userdb

        # Create a new instance of userdb.
        self._userdb = self.__get_userdb_module()

        # Check result. If the db is not created raise an error.
        if not self._userdb:
            raise ValueError("invalid userdb type. Re-configure rdiffweb.")
        return self._userdb

    userdb = property(fget=__get_userdb)

    def __get_userdb_module(self):
        """
        Return a different implementation according to UserDB configuration.
        """

        # Get available plugins
        try:
            category = rdw_plugin.IUserDBPlugin.CATEGORY
            plugins = self.plugins.get_plugins_of_category(category)
        except:
            logger.error('fail to load UserDB plugin', exc_info=True)
            plugins = list()
        if len(plugins) == 0:
            raise ValueError("no UserDB plugins enabled, check your configuration")

        # If UserDB is defined, use it as a hint.
        userdb = self.config.get_config("UserDB")
        if userdb:
            # Find the plugin matching userdb
            matches = filter(lambda plugin: plugin.name.lower() == userdb.lower(), plugins)
            if len(matches) > 0:
                return matches[0].plugin_object
            else:
                raise ValueError('UserDB value [%s] is invalid' % (userdb,))
        else:
            # Otherwise return the first plugins
            return plugins[0].plugin_object

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
