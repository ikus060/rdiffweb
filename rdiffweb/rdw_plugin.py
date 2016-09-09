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

from builtins import bytes
from builtins import object
from builtins import str
from glob import glob
import imp
import logging
import os
from pkg_resources import working_set, Environment
import pkg_resources
import sys
from collections import namedtuple
from itertools import chain
import inspect
import datetime

# Define logger for this module
logger = logging.getLogger(__name__)


PluginInfo = namedtuple(
    'PluginInfo',
    ['name', 'version', 'author', 'description', 'path', 'enabled', 'url', 'copyright'])


class PluginManager(object):

    def __init__(self, cfg):
        """
        Initialise the plugin system.
        """
        assert cfg
        self.cfg = cfg
        self._categories = {}
        self._names = {}
        self._plugin_infos = []

        # Load all enabled plugins.
        self._load_plugins()

    def _get_search_path(self):
        """
        Determine the search path to look for plugins.
        """
        # Load plugins from config
        search_path = self.cfg.get_config(
            "PluginSearchPath",
            default="/etc/rdiffweb/plugins")
        return [os.path.normpath(p) for p in search_path.split(',')]

    def _load_plugins(self):
        """
        Load plugin using multiple `loaders`.
        """
        # Get additional search path (from configuration).
        search_path = self._get_search_path()

        # Call each loaders
        for loadfunc in [self._load_eggs, self._load_py]:
            for name, module, dist in loadfunc(search_path):
                self._register_module(name, module, dist)

    def _load_eggs(self, search_path):
        # Redefine where to search entry point.
        distributions, errors = working_set.find_plugins(
            Environment(search_path)
        )
        if errors:
            logger.warn('could not load %s', errors)
        map(working_set.add, distributions)

        # Load each entry point one by one
        for entry in working_set.iter_entry_points('rdiffweb.plugins'):
            # Get unicode plugin name
            module_name = entry.name
            if isinstance(module_name, bytes):
                module_name = module_name.decode('ascii')
            # Plugin is enabled. Load it.
            logger.debug('loading module plugin [%s] from [%r]', module_name, entry.module_name)
            try:
                yield (module_name, entry.load(), entry.dist)
            except:
                logger.error('fail to load module plugin [%s] from [%r]', module_name, entry.module_name, exc_info=1)

    def _load_py(self, search_path):
        """
        Called to load py file.
        """
        for path in search_path:
            plugin_files = glob(os.path.join(path, '*.py'))
            for plugin_file in plugin_files:
                # Check if plugin is filtered
                module_name = os.path.basename(plugin_file[:-3])
                try:
                    logger.debug('loading module plugin [%s] from [%r]', module_name, plugin_file)
                    if module_name not in sys.modules:
                        yield (module_name, imp.load_source(module_name, plugin_file), None)
                except:
                    logger.error('failed to load module plugin [%s] from [%s]', module_name, plugin_file, exc_info=1)

        # Append core plugins directory (in bytes)
        # path = pkg_resources.resource_filename('rdiffweb', 'plugins')  # @UndefinedVariable
        # searchpath.append(path)
        # Append user plugins directory
        # plugin_locations = plugin_search_path.split(',')
        # searchpath.extend(plugin_locations)
        # Build the manager
        # logger.debug("plugin search path [%s]", searchpath)

        # Create the plugin manager.
        # PluginManagerSingleton.setBehaviour([FilteredPluginManager])
        # self.manager = PluginManagerSingleton.get()

        # Sets plugins locations.
        # plugin_locator = PluginLocator()
        # self.manager.setPluginLocator(plugin_locator)
        # plugin_locator.setPluginPlaces(searchpath)

        # Define categories
        # self.manager.setCategoriesFilter({
        #    IDatabase.CATEGORY: IDatabase,
        #    IDeamonPlugin.CATEGORY: IDeamonPlugin,
        #    ITemplateFilterPlugin.CATEGORY: ITemplateFilterPlugin,
        #    IPasswordStore.CATEGORY: IPasswordStore,
        #    IPreferencesPanelProvider.CATEGORY: IPreferencesPanelProvider,
        #    IUserChangeListener.CATEGORY: IUserChangeListener,
        # })

        # Set filter.
        # self.manager.isPluginOk = self.is_plugin_enabled

        # Load all plugins
        # self.manager.collectPlugins()

    def get_all_plugins(self):
        """
        Return a complete list of plugins. (enabled only).
        """
        return list(self._names.values())

    def get_plugin_by_name(self, name):
        """
        Get the plugin corresponding to a given name.
        """
        return self._names.get(name, None)

    def get_plugins_of_category(self, category):
        """
        Returns a list of all plugins in category.
        """
        return self._categories.get(category, [])

    def _get_plugin_info(self, name, module, dist):
        """
        Extract plugin information from module and distribution.
        """
        param = {
            'name': name,
            'author': getattr(module, 'author', None),
            'version': getattr(module, 'version', None),
            'description': inspect.getdoc(module),
            'path': getattr(module, '__locations__', None),
            'copyright': None,
            'url': None,
        }
        # Override value with dist.
        if dist:
            if dist.version:
                param['version'] = dist.version
            if dist.location:
                param['path'] = dist.location
            # Try to get more with metadata
            attrs = {
                'author': 'author',
                'license': 'copyright',
                'home-page': 'url',
            }
            metadata = 'METADATA' if dist.has_metadata('METADATA') else 'PKG-INFO'
            try:
                data = [line.partition(': ') for line in dist.get_metadata(metadata).split('\n')]
                for key, sep, value in data:
                    key = key.lower()
                    if key in attrs:
                        param[attrs[key]] = value
            except Exception:
                pass

        return param

    def get_plugin_infos(self):
        """
        Return list of plugin info.
        """
        return list(self._plugin_infos)

    def is_module_enabled(self, module_name):
        """
        Called to filter the plugin list. Current implementation return
        true if the config file enable the plugin.
        """
        assert isinstance(module_name, str)
        # Check if the plugin is enabled in config file.
        try:
            return self.cfg.get_config_bool(
                "%sEnabled" % (module_name,),
                default="False")
        except:
            return False

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

    def _register_module(self, name, module, dist):
        """
        Register the given module. Each class in the module will be registered
        as a plugin.
        """
        # Check if enabled
        enabled = self.is_module_enabled(name)

        # Collect plugin info
        param = self._get_plugin_info(name, module, dist)
        param['enabled'] = enabled
        self._plugin_infos.append(PluginInfo(**param))

        # Filter the modules.
        if not enabled:
            logger.info("module plugin [%s] rejected: plugins is not enabled", name)
            return

        # Get module name
        module_name = module.__name__
        if isinstance(module_name, bytes):
            module_name = module_name.decode('ascii')

        # Loop on element in the module to find plugin class.
        for element in (getattr(module, name) for name in dir(module)):
            # Check if element is a plugin class.
            try:
                if not issubclass(element, IRdiffwebPlugin):
                    continue
            except Exception:
                continue
            # Get plugin name
            plugin_name = element.__name__
            if isinstance(plugin_name, bytes):
                plugin_name = plugin_name.decode('ascii')
            # Make sure the element is not an interface too.
            # FIXME figure-out a different way to exclude interface.
            if plugin_name.startswith('I') or plugin_name in ['JobPlugin']:
                continue
            # Get categories
            categories = [c.CATEGORY for c in element.__bases__ if hasattr(c, 'CATEGORY')]
            categories.extend([c.__name__ for c in element.__bases__])
            # Create instance
            logger.debug('loading plugin [%s] from module [%s]', plugin_name, module_name)
            try:
                instance = element()
            except Exception:
                logger.warn('fail to create new instance of plugin [%s]', plugin_name)
                continue
            # Register the plugin.
            self._register_plugin(plugin_name, categories, instance)

    def _register_plugin(self, plugin_name, categories, instance):
        """
        Register the given plugin element.
        """
        # Then register the plugin with name
        self._names[plugin_name] = instance
        # Register plugin with category.
        for c in set(categories):
            self._categories.setdefault(c, list()).append(instance)

    def run(self, method, category=None):
        """
        Utility method to run plugins of given category.
        """
        assert method
        # Get plugins of given category.
        if category is None:
            plugins = self.get_all_plugins()
        else:
            plugins = self.get_plugins_of_category(category)
        # Run every plugin.
        for plugin in plugins:
            try:
                method(plugin)
            except:
                logger.exception("fail to run plugin [%r]", plugin.__class__.__name__)


class IRdiffwebPlugin(object):
    """
    Defines the interface for all plugins.
    """

    CATEGORY = "Undefined"

    def activate(self):
        logger.info("activate plugin object [%s]",
                    self.__class__.__name__)

    def deactivate(self):
        logger.info("deactivate plugin object [%s]",
                    self.__class__.__name__)

    def get_localesdir(self):
        """
        Return the location of the locales directory. Default implementation
        return the "locales" directory if exists. Otherwise return None.
        """
        if pkg_resources.resource_isdir(self.__module__, 'locales'):  # @UndefinedVariable
            return pkg_resources.resource_filename(self.__module__, 'locales')  # @UndefinedVariable
        return False

    def get_templatesdir(self):
        """
        Return the location of the templates director. Default implementation
        return the "templates" director if exists. Otherwise return None.
        """
        if pkg_resources.resource_isdir(self.__module__, 'templates'):  # @UndefinedVariable
            return pkg_resources.resource_filename(self.__module__, 'templates')  # @UndefinedVariable
        return False


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


class JobPlugin(IDeamonPlugin):
    """
    Extends the deamon plugin to run a job once a day at fixed time.

    Sub class should implement `job_execution_time` and `job_run`.
    """

    deamon_frequency = 300

    job_execution_time = '23:00'

    _next_execution_time = None

    def deamon_run(self):
        # Determine the next execution time.
        if not self._next_execution_time:
            self._next_execution_time = self._compute_next_execution_time()

        # Check if task should be run.
        now = datetime.datetime.now()
        if now < self._next_execution_time:
            return

        # Run job.
        try:
            self.job_run()
        finally:
            self._next_execution_time = None

    def _compute_next_execution_time(self):
        """
        Return a date time representing the next execution time.
        """
        now = datetime.datetime.now()
        time_str = self.job_execution_time
        exec_time = datetime.datetime.strptime(time_str, '%H:%M')
        exec_time = now.replace(hour=exec_time.hour, minute=exec_time.minute, second=0, microsecond=0)
        if exec_time < now:
            exec_time = exec_time.replace(day=exec_time.day + 1)
        return exec_time


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


class ITemplateFilterPlugin(IRdiffwebPlugin):
    """
    Plugin to extend any pages params.
    """
    CATEGORY = "TemplateFilter"

    def filter_data(self, template_name, data):
        """
        Called by to filter the params.
        """
        raise NotImplementedError("filter_data is not implemented")


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
