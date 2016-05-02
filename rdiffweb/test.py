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

from builtins import str, delattr
import cherrypy
from cherrypy.test import helper
from future.utils import native_str
import os
import pkg_resources
import shutil
import tarfile
import tempfile
import unittest

from rdiffweb.rdw_app import RdiffwebApp


try:
    from urllib.parse import urlencode  # @UnresolvedImport @UnusedImport
except:
    from urllib import urlencode  # @UnresolvedImport @UnusedImport @Reimport


class MockRdiffwebApp(RdiffwebApp):
    def __init__(self, enabled_plugins=['SQLite'], default_config={}):
        assert enabled_plugins is None or isinstance(enabled_plugins, list)
        self.enabled_plugins = enabled_plugins
        assert default_config is None or isinstance(default_config, dict)
        self.default_config = default_config

        # Call parent constructor
        RdiffwebApp.__init__(self)

    def clear_db(self):
        if hasattr(self, 'database_dir'):
            shutil.rmtree(self.database_dir)
            delattr(self, 'database_dir')

    def clear_testcases(self):
        if hasattr(self, 'testcases'):
            shutil.rmtree(native_str(self.testcases))
            delattr(self, 'testcases')

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

    def reset(self, username=None, password=None):
        """
        Reset the application. Delete all data from database.
        """
        # Delete all user from database
        for user in self.userdb.list():
            self.userdb.delete_user(user)

        # Create new user admin
        if self.userdb.supports('add_user') and username and password:
            user = self.userdb.add_user(username, password)
            user.is_admin = True

    def reset_testcases(self):
        """Extract testcases."""
        # Extract 'testcases.tar.gz'
        testcases = pkg_resources.resource_filename('rdiffweb.tests', 'testcases.tar.gz')  # @UndefinedVariable
        new = str(tempfile.mkdtemp(prefix='rdiffweb_tests_'))
        tarfile.open(testcases).extractall(native_str(new))

        # Register repository
        for user in self.userdb.list():
            user.user_root = new
            user.repos = ['testcases/']

        self.testcases = new


class AppTestCase(unittest.TestCase):

    enabled_plugins = ['SQLite']

    default_config = {}

    reset_app = True

    reset_testcases = False

    REPO = 'testcases/'

    USERNAME = None

    PASSWORD = None

    def setUp(self):
        self.app = MockRdiffwebApp(self.enabled_plugins, self.default_config)
        if self.reset_app:
            self.app.reset(self.USERNAME, self.PASSWORD)
        if self.reset_testcases:
            self.app.reset_testcases()
        unittest.TestCase.setUp(self)

    def tearDown(self):
        self.app.clear_db()
        if self.reset_testcases:
            self.app.clear_testcases()
        unittest.TestCase.tearDown(self)


class WebCase(helper.CPWebCase):
    """
    Helper class for the rdiffweb test suite.
    """

    REPO = 'testcases'

    USERNAME = 'admin'

    PASSWORD = 'admin123'

    interactive = False

    login = False

    reset_app = False

    reset_testcases = False

    @classmethod
    def setUpClass(cls):
        super(helper.CPWebCase, cls).setUpClass()
        cls.setup_class()

    @classmethod
    def tearDownClass(cls):
        cls.teardown_class()
        app = cherrypy.tree.apps['']
        app.clear_db()

    @classmethod
    def setup_server(cls, enabled_plugins=['SQLite'], default_config={}):
        app = MockRdiffwebApp(enabled_plugins, default_config)
        cherrypy.tree.mount(app)

    def setUp(self):
        helper.CPWebCase.setUp(self)
        if self.reset_app:
            self.app.reset(self.USERNAME, self.PASSWORD)
        if self.reset_testcases:
            self.app.reset_testcases()
        if self.login:
            self._login()

    def tearDown(self):
        if self.reset_testcases:
            self.app.clear_testcases()

    @property
    def app(self):
        """
        Return reference to Rdiffweb application.
        """
        return cherrypy.tree.apps['']

    @property
    def baseurl(self):
        return 'http://%s:%s' % (self.HOST, self.PORT)

    def getPage(self, url, headers=None, method="GET", body=None,
                protocol=None):
        if headers is None:
            headers = []
        # When body is a dict, send the data as form data.
        if isinstance(body, dict) and method in ['POST', 'PUT']:
            data = [(k.encode(encoding='latin1'), v.encode(encoding='utf-8'))
                    for k, v in body.items()]
            body = urlencode(data)
        # Send back cookies if any
        if hasattr(self, 'cookies') and self.cookies:
            headers.extend(self.cookies)
        helper.CPWebCase.getPage(self, url, headers, method, body, protocol)

    def _login(self, username=USERNAME, password=PASSWORD):
        self.getPage("/login/", method='POST', body={'login': username, 'password': password})
        self.assertStatus('303 See Other')

    def test_gc(self):
        "Override test_gc to skip the test."
        # Disable gc check (because it randomly fail).
