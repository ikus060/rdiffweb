# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest

import cherrypy
from cherrypy.test import helper
import pkg_resources

from rdiffweb.core.store import ADMIN_ROLE
from rdiffweb.rdw_app import RdiffwebApp

try:
    from urllib.parse import urlencode  # @UnresolvedImport @UnusedImport
except:
    from urllib import urlencode  # @UnresolvedImport @UnusedImport @Reimport


class MockRdiffwebApp(RdiffwebApp):

    def __init__(self, default_config={}):
        assert default_config is None or isinstance(default_config, dict)
        self.default_config = default_config

        # database in memory
        self.database_dir = tempfile.mkdtemp(prefix='rdiffweb_tests_db_')
        default_config['SQLiteDBFile'] = os.path.join(self.database_dir, 'rdiffweb.tmp.db')

        # Call parent constructor
        RdiffwebApp.__init__(self, cfg=default_config)

    def clear_db(self):
        if hasattr(self, 'database_dir'):
            shutil.rmtree(self.database_dir)
            delattr(self, 'database_dir')

    def clear_testcases(self):
        if hasattr(self, 'testcases'):
            shutil.rmtree(self.testcases)
            delattr(self, 'testcases')

    def reset(self, username=None, password=None):
        """
        Reset the application. Delete all data from database.
        """
        # Delete all data from database directly.
        self.store._database.delete('users')
        self.store._database.delete('repos')
        self.store._database.delete('sshkeys')

        # Create new user admin
        if username and password:
            user = self.store.add_user(username, password)
            user.role = ADMIN_ROLE

    def reset_testcases(self):
        """Extract testcases."""
        # Extract 'testcases.tar.gz'
        testcases = pkg_resources.resource_filename('rdiffweb.tests', 'testcases.tar.gz')  # @UndefinedVariable
        new = str(tempfile.mkdtemp(prefix='rdiffweb_tests_'))
        subprocess.check_call(['tar', '-zxf', testcases], cwd=new)

        # Register repository
        for user in self.store.users():
            user.user_root = new
            user.add_repo('testcases')

        self.testcases = new


class AppTestCase(unittest.TestCase):

    default_config = {}

    reset_app = True

    reset_testcases = False

    REPO = 'testcases'

    USERNAME = None

    PASSWORD = None

    def setUp(self):
        self.app = MockRdiffwebApp(self.default_config)
        if self.reset_app:
            self.app.reset(self.USERNAME, self.PASSWORD)
        if self.reset_testcases:
            assert self.reset_app, 'reset_app must be True when reset_testcases is True'
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
    def setup_server(cls, default_config={}):
        app = MockRdiffwebApp(default_config)
        cherrypy.tree.mount(app)

    def setUp(self):
        helper.CPWebCase.setUp(self)
        if self.reset_app:
            self.app.reset(self.USERNAME, self.PASSWORD)
        if self.reset_testcases:
            assert self.reset_app, 'reset_app must be True when reset_testcases is True'
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

    def getJson(self, *args, **kwargs):
        self.getPage(*args, **kwargs)
        self.assertStatus(200)
        return json.loads(self.body.decode('utf8'))

    def _login(self, username=USERNAME, password=PASSWORD):
        self.getPage("/login/", method='POST', body={'login': username, 'password': password})
        self.assertStatus('303 See Other')

    def test_gc(self):
        "Override test_gc to skip the test."
        # Disable gc check (because it randomly fail).
        pass
