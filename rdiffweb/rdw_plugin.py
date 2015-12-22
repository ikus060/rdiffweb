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

import logging
import os
import pkg_resources

from yapsy.IPlugin import IPlugin
from yapsy.PluginFileLocator import PluginFileLocator
from yapsy.PluginFileLocator import PluginFileAnalyzerWithInfoFile
from yapsy.PluginManager import PluginManagerSingleton
from yapsy.FilteredPluginManager import FilteredPluginManager

# Define logger for this module
logger = logging.getLogger(__name__)


class PluginLocator(PluginFileLocator):
    """
    Custom plugin file locator to handle an error when loading plugin. To
    avoid all the application to crash.
    """

    def __init__(self):
        analyzer = PluginFileAnalyzerWithInfoFile(
            name="rdiffweb-info",
            extensions="plugin")
        PluginFileLocator.__init__(self, analyzers=[analyzer])
        # Disable recursive search.
        self.recursive = False

    def _getInfoForPluginFromAnalyzer(self, analyzer, dirpath, filename):
        try:
            return PluginFileLocator._getInfoForPluginFromAnalyzer(self, analyzer, dirpath, filename)
        except ValueError:
            logger.exception("fail to load plugin [%s]" % (filename,))


class PluginManager():

    def __init__(self, cfg):
        """
        Initialise the plugin system.
        """

        assert cfg
        self.cfg = cfg

        # Get plugin locations.
        plugin_search_path_b = self.cfg.get_config_str(
            "PluginSearchPath",
            default=b"/etc/rdiffweb/plugins")

        # Determine the search path
        searchpath = []
        # Append core plugins directory (in bytes)
        path_b = pkg_resources.resource_filename('rdiffweb', b'plugins')  # @UndefinedVariable
        searchpath.append(path_b)
        # Append user plugins directory
        plugin_locations = plugin_search_path_b.split(b',')
        searchpath.extend(plugin_locations)
        # Build the manager
        logger.debug("plugin search path [%s]" % (searchpath))

        # Create the plugin manager.
        PluginManagerSingleton.setBehaviour([FilteredPluginManager])
        self.manager = PluginManagerSingleton.get()

        # Sets plugins locations.
        plugin_locator = PluginLocator()
        self.manager.setPluginLocator(plugin_locator)
        plugin_locator.setPluginPlaces(searchpath)

        # Define categories
        self.manager.setCategoriesFilter({
            IDatabase.CATEGORY: IDatabase,
            IDeamonPlugin.CATEGORY: IDeamonPlugin,
            ILocationsPagePlugin.CATEGORY: ILocationsPagePlugin,
            IPasswordStore.CATEGORY: IPasswordStore,
            IPreferencesPanelProvider.CATEGORY: IPreferencesPanelProvider,
            IUserChangeListener.CATEGORY: IUserChangeListener,
        })

        # Set filter.
        self.manager.isPluginOk = self.is_plugin_enabled

        # Load all plugins
        self.manager.collectPlugins()

    def get_all_plugins(self):
        """
        Return a complete list of plugins. (enabled only).
        """
        return self.manager.getAllPlugins()

    def get_plugin_by_name(self, name, category=None):
        """
        Get the plugin corresponding to a given name.
        """
        if category is None:
            categories = self.manager.getCategories()
            for category in categories:
                plugin_info = self.manager.getPluginByName(name, category)
                if plugin_info is not None:
                    return plugin_info
        return self.manager.getPluginByName(name, category)

    def get_plugins_of_category(self, category):
        """
        Returns a list of all plugins in category.
        """
        return self.manager.getPluginsOfCategory(category)

    def is_plugin_enabled(self, plugin_info):
        """
        Called to filter the plugin list. Current implementation return
        true if the config file enable the plugin.
        """

        # Check if the plugin is enabled in config file.
        value = self.cfg.get_config_bool(
            plugin_info.name + "Enabled",
            default="False")
        if not value:
            logger.info("plugin [%s v%s] rejected: plugins is not enabled",
                        plugin_info.name,
                        plugin_info.version)
        return value

    def locate_plugins(self):
        """
        Get list of every plugin (enabled and disabled).
        Return a list of PluginInfo.
        """
        plugins_list = list()
        plugins_data = self.manager.getPluginLocator().locatePlugins()[0]
        for data in plugins_data:
            plugins_list.append(data[2])
        return plugins_list

    def run(self, method, category=None):
        """
        Utility method to run plugins of given category.
        """
        # Get plugins of given category.
        if category is None:
            plugins = self.manager.getAllPlugins()
        else:
            plugins = self.manager.getPluginsOfCategory(category)
        # Run every plugin.
        for plugin in plugins:
            try:
                method(plugin.plugin_object)
            except:
                logger.exception("fail to run plugin [%s]" % (plugin.name))


class IRdiffwebPlugin(IPlugin):
    """
    Defines the interface for all plugins.
    """

    CATEGORY = "Undefined"

    def activate(self):
        logger.debug("activate plugin object [%s]",
                     self.__class__.__name__)
        return IPlugin.activate(self)

    def deactivate(self):
        logger.debug("deactivate plugin object [%s]",
                     self.__class__.__name__)
        return IPlugin.deactivate(self)

    def get_localesdir(self):
        """
        Return the location of the locales directory. Default implementation
        return the "locales" directory if exists. Otherwise return None.
        """
        # Add plugin translation too.
        mo_dir = pkg_resources.resource_filename(# @UndefinedVariable
            self.__module__, 'locales')
        if os.path.exists(mo_dir):
            return mo_dir
        return None

    def get_templatesdir(self):
        """
        Return the location of the templates director. Default implementation
        return the "templates" director if exists. Otherwise return None.
        """
        templates_dir = pkg_resources.resource_filename(# @UndefinedVariable
            self.__module__, 'templates')
        if os.path.exists(templates_dir):
            return templates_dir
        return None


class IDatabase(IRdiffwebPlugin):
    """
    Database plugins to allow alternative database implementation.
    """
    CATEGORY = "Database"

    def add_user(self, user):
        """
        Add a new username to this userdb.

        Returns True, if a new account was created, False if user already
        exists.
        """

    def delete_user(self, user):
        """
        Deletes the user account.

        Returns True, if the account existed and was deleted, False otherwise.
        """

    def get_user_root(self, user):
        """Get user root directory."""

    def get_repos(self, user):
        """Get list of repos for the given `username`."""

    def get_email(self, user):
        """Return the user email."""

    def set_user_root(self, user, user_root):
        """Sets the user information."""

    def set_email(self, user, email):
        """Sets the given user email."""

    def set_is_admin(self, user, is_admin):
        """Sets the user information."""

    def set_repos(self, user, repoPaths):
        """Sets the list of repos for the given user."""

    def set_repo_maxage(self, user, repoPath, maxAge):
        """Sets the max age for the given repo."""

    def get_repo_maxage(self, user, repoPath):
        """Return the max age of the given repo."""

    def is_admin(self, user):
        """Return True if the user is Admin."""


class IDeamonPlugin(IRdiffwebPlugin):
    """
    Daemon plugin used to run a background thread.
    """
    CATEGORY = "Daemon"

    @property
    def deamon_frequency(self):
        """
        Return the frequency of the deamon plugin in seconds.
        """
        raise NotImplementedError("frequency is not implemented")

    def deamon_run(self):
        """
        Called periodically.
        """
        raise NotImplementedError("run is not implemented")


class ILocationsPagePlugin(IRdiffwebPlugin):
    """
    Plugin to extend the LocationsPage.
    """
    CATEGORY = "LocationsPage"

    def locations_update_params(self, params):
        """
        Called by the LocationsPage to add extra data to the page.
        """
        raise NotImplementedError("locations_update_params is not implemented")


class IPasswordStore(IRdiffwebPlugin):
    """
    Plugin used to provide user authentication.

    Implementations may omit implementing `delete_user` and `set_password`.
    """
    CATEGORY = "PasswordStore"

    def are_valid_credentials(self, user, password):
        """Checks if the password is valid for the user.

        Returns `username`, if the correct user and password are specified.
        Returns False, if the incorrect password was specified.
        Returns None, if the user doesn't exist in this password store.

        Note: Returning `False` is an active rejection of the login attempt.
        Return None to let the authentication eventually fall through to
        next store in a chain.
        """
        return None

    def delete_user(self, user):
        """
        Deletes the user account.

        Returns True, if the account existed and was deleted, False otherwise.
        """
        return False

    def has_password(self, user):
        """Returns whether the user account exists in password store."""
        return False

    def set_password(self, user, password, old_password=None):
        """Sets the password for the user."""

    def supports(self, operation):
        """
        Return true if the given operation is supported.
        """
        return False


class IPreferencesPanelProvider(IRdiffwebPlugin):
    """
    Rdiffweb provide a user settings page to allow users to change some
    preference settings. Plugins can participate to this system by extending
    this interface.
    """
    CATEGORY = "PreferencesPanelProvider"

    def get_prefs_panels(self):
        """
        Called by the PreferencesPage.
        Subclasses should return a list of panels.

        e.g.:

            def get_prefs_panels(self):
                yield ('photo',_('User picture'))
                yield ('profile', _('Profile info'))

        """
        raise NotImplementedError("prefs_update_params is not implemented")

    def render_prefs_panel(self, pageid, **kwargs):
        """
        This method is called when one of the page is requested by the user.
        The `pageid` define the page to be randered.
        The `params` is a dict() with the data to generate the page.

        e.g.:

            def render_prefs_panel(self, pageid, params)
                if pageid == 'photo':
                    params['photo_url'] = ...
                    template = self.app.templates.get_template("page_prefs_photo.html")
                    params['template_content'] = template
        """


class IUserChangeListener(IRdiffwebPlugin):
    """
    A plugin to receive user changes event.
    """
    CATEGORY = "UserChangeListener"

    def user_added(self, user, password):
        """New user (account) created."""

    def user_attr_changed(self, user, attrs={}):
        """User attribute changed."""

    def user_deleted(self, user):
        """User and related account information have been deleted."""

    def user_logined(self, user, password):
        """User successfully logged into rdiffweb."""

    def user_password_changed(self, user, password):
        """Password changed."""
