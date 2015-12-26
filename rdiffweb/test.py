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
"""
Created on Oct 14, 2015

Mock class for testing.

@author: ikus060
"""

from __future__ import unicode_literals

from builtins import str
from cherrypy import HTTPRedirect
import cherrypy
from future.utils import native_str
import os
import pkg_resources
import shutil
import tarfile
import tempfile

from rdiffweb.rdw_app import RdiffwebApp


class MockRdiffwebApp(RdiffwebApp):

    def __init__(self, enabled_plugins=['SQLite'], default_config={}):
        assert enabled_plugins is None or isinstance(enabled_plugins, list)
        self.enabled_plugins = enabled_plugins
        assert default_config is None or isinstance(default_config, dict)
        self.default_config = default_config

        # Call parent constructor
        RdiffwebApp.__init__(self)

    def clear(self):
        if hasattr(self, 'testcases'):
            shutil.rmtree(native_str(self.testcases))

        if hasattr(self, 'database_dir'):
            shutil.rmtree(native_str(self.database_dir))

        cherrypy.session = {}
        if hasattr(cherrypy.request, 'user'):
            delattr(cherrypy.request, 'user')

    def load_config(self, configfile=None):
        RdiffwebApp.load_config(self, None)

        # Enabled given plugins
        for plugin_name in self.enabled_plugins:
            self.cfg.set_config('%sEnabled' % plugin_name, 'True')

        # database in memory
        if 'SQLite' in self.enabled_plugins:
            self.database_dir = tempfile.mkdtemp(prefix='rdiffweb_tests_db_')
            self.cfg.set_config('SQLiteDBFile', os.path.join(self.database_dir, 'rdiffweb.tmp.db'))

        if 'Ldap' in self.enabled_plugins:
            self.cfg.set_config('LdapUri', '__default__')
            self.cfg.set_config('LdapBaseDn', 'dc=nodomain')

        # Set config
        for key, val in list(self.default_config.items()):
            self.cfg.set_config(key, val)

    def reset(self):
        """
        Reset the application. Delete all data from database.
        """
        # Delete all user from database
        for user in self.userdb.list():
            self.userdb.delete_user(user)

        # Create new user admin
        if self.userdb.supports('add_user'):
            self.userdb.add_user('admin', 'admin123')

    def reset_testcases(self):
        """Extract testcases."""
        # Extract 'testcases.tar.gz'
        testcases = pkg_resources.resource_filename('rdiffweb.tests', 'testcases.tar.gz')  # @UndefinedVariable
        new = str(tempfile.mkdtemp(prefix='rdiffweb_tests_'))
        tarfile.open(testcases).extractall(native_str(new))

        # Register repository
        self.userdb.set_user_root('admin', new)
        self.userdb.set_repos('admin', ['testcases/'])

        assert self.userdb.get_user_root('admin') == new
        self.testcases = new

    def login(self):
        """
        Simulate login with admin user
        """
        # Login as admin
        if hasattr(cherrypy.request, 'user'):
            delattr(cherrypy.request, 'user')
        cherrypy.session = {}
        cherrypy.request.method = 'POST'
        try:
            self.root.login.index(login="admin", password="admin123")
        except HTTPRedirect:
            pass
        cherrypy.request.method = 'GET'
