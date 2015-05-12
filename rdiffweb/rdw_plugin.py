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

    def __init__(self, config):
        """
        Initialise the plugin system.
        """

        assert config
        self.config = config

        # Get plugin locations.
        plugin_search_path_b = self.config.get_config_str(
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
            IUserDBPlugin.CATEGORY: IUserDBPlugin,
            IDeamonPlugin.CATEGORY: IDeamonPlugin,
            ILocationsPagePlugin.CATEGORY: ILocationsPagePlugin,
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
        value = self.config.get_config_bool(
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

    def activate_with_app(self, app):
        """
        This method is called by the RdiffwebApp to setup the plugin.
        """
        self._app = app
        try:
            self.activate()
        finally:
            self._app = None

    def deactivate(self):
        logger.debug("deactivate plugin object [%s]",
                     self.__class__.__name__)
        return IPlugin.deactivate(self)

    def __get_app(self):
        """
        Utility method to access the application. (a.k.a. RdiffwebApp)

        Raise a ValueError if the application is not accessible.
        """
        # Get app from cherrypy context.
        try:
            app = cherrypy.request.app.root  # @UndefinedVariable
        except:
            app = None
        # Fall back to use private _app reference.
        if hasattr(self, "_app") and self._app is not None:
            app = self._app
        # Raise an error if the app is not available.
        if app is None:
            raise ValueError("app is not available")
        return app

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

    def get_username(self):
        """
        Return current username (from cherrypy session).
        """
        try:
            return cherrypy.session['username']  # @UndefinedVariable
        except:
            return None

    app = property(fget=__get_app)


class IUserDBPlugin(IRdiffwebPlugin):
    """
    Plugin used to provide user authentication and user's persistence.
    """
    CATEGORY = "UserDB"


class IDeamonPlugin(IRdiffwebPlugin):
    """
    Daemon plugin used to run a background thread.
    """
    CATEGORY = "Daemon"


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
