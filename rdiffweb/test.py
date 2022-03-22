# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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
import unittest.mock
from threading import Thread
from urllib.parse import urlencode

import cherrypy
import pkg_resources
from cherrypy.test import helper

from rdiffweb.core.store import _REPOS, _SSHKEYS, _USERS
from rdiffweb.rdw_app import RdiffwebApp

# For cherrypy8, we need to monkey patch Thread.isAlive
Thread.isAlive = Thread.is_alive


def create_testcases_repo(app):
    """Extract testcases."""
    # Extract 'testcases.tar.gz'
    testcases = pkg_resources.resource_filename('rdiffweb.tests', 'testcases.tar.gz')  # @UndefinedVariable
    new = str(tempfile.mkdtemp(prefix='rdiffweb_tests_'))
    subprocess.check_call(['tar', '-zxf', testcases], cwd=new)
    return new


class AppTestCase(unittest.TestCase):

    REPO = 'testcases'

    USERNAME = 'admin'

    PASSWORD = 'admin123'

    default_config = {}

    app_class = RdiffwebApp

    @classmethod
    def setup_class(cls):
        if cls is AppTestCase:
            raise unittest.SkipTest("%s is an abstract base class" % cls.__name__)

    @classmethod
    def teardown_class(cls):
        pass

    def setUp(self):
        # Allow defining a custom database uri for testing.
        self.database_dir = tempfile.mkdtemp(prefix='rdiffweb_tests_db_')
        uri = os.path.join(self.database_dir, 'rdiffweb.tmp.db')
        uri = os.environ.get('RDIFFWEB_TEST_DATABASE_URI', uri)
        self.default_config['database-uri'] = uri
        cfg = self.app_class.parse_args(
            args=[], config_file_contents='\n'.join('%s=%s' % (k, v) for k, v in self.default_config.items())
        )
        # Create Application
        self.app = self.app_class(cfg)
        # Create repositories
        self.testcases = create_testcases_repo(self.app)
        # Register repository
        admin_user = self.app.store.get_user(self.USERNAME)
        if admin_user:
            admin_user.user_root = self.testcases

    def tearDown(self):
        if hasattr(self, 'database_dir'):
            shutil.rmtree(self.database_dir)
            delattr(self, 'database_dir')
        if hasattr(self, 'testcases'):
            shutil.rmtree(self.testcases)
            delattr(self, 'testcases')


class WebCase(helper.CPWebCase):
    """
    Helper class for the rdiffweb test suite.
    """

    REPO = 'testcases'

    USERNAME = 'admin'

    PASSWORD = 'admin123'

    interactive = False

    login = False

    default_config = {}

    app_class = RdiffwebApp

    @classmethod
    def setup_class(cls):
        if cls is WebCase:
            raise unittest.SkipTest("%s is an abstract base class" % cls.__name__)
        super().setup_class()
        cls.do_gc_test = False

    @classmethod
    def teardown_class(cls):
        super().teardown_class()

    @classmethod
    def setup_server(cls):
        # Allow defining a custom database uri for testing.
        cls.database_dir = tempfile.mkdtemp(prefix='rdiffweb_tests_db_')
        uri = os.path.join(cls.database_dir, 'rdiffweb.tmp.db')
        uri = os.environ.get('RDIFFWEB_TEST_DATABASE_URI', uri)
        cls.default_config['database-uri'] = uri
        # Disable rate-limit for testing.
        if 'rate-limit' not in cls.default_config:
            cls.default_config['rate-limit'] = -1
        cfg = cls.app_class.parse_args(
            args=[], config_file_contents='\n'.join('%s=%s' % (k, v) for k, v in cls.default_config.items())
        )
        # Create Application
        app = cls.app_class(cfg)
        cherrypy.tree.mount(app)

    def setUp(self):
        helper.CPWebCase.setUp(self)
        # Clear database
        with self.app.store.engine.connect() as conn:
            conn.execute(_SSHKEYS.delete())
            conn.execute(_REPOS.delete())
            conn.execute(_USERS.delete())
        self.app.store.create_admin_user()
        # Create testcases repo
        self.testcases = create_testcases_repo(self.app)
        admin_user = self.app.store.get_user(self.USERNAME)
        if admin_user:
            admin_user.user_root = self.testcases
        # Login to web application.
        if self.login:
            self._login()

    def tearDown(self):
        if hasattr(self, 'testcases'):
            shutil.rmtree(self.testcases)
            delattr(self, 'testcases')

    @property
    def app(self):
        """
        Return reference to Rdiffweb application.
        """
        return cherrypy.tree.apps['']

    @property
    def baseurl(self):
        return 'http://%s:%s' % (self.HOST, self.PORT)

    def getPage(self, url, headers=None, method="GET", body=None, protocol=None):
        if headers is None:
            headers = []
        # When body is a dict, send the data as form data.
        if isinstance(body, dict) and method in ['POST', 'PUT']:
            data = [(k.encode(encoding='latin1'), v.encode(encoding='utf-8')) for k, v in body.items()]
            body = urlencode(data)
        # Send back cookies if any
        if hasattr(self, 'cookies') and self.cookies:
            headers.extend(self.cookies)
        # CherryPy ~8.9.1 is not handling absolute URL properly and web browser
        # are usually not sending absolute URL either. So trim the base.
        base = 'http://%s:%s' % (self.HOST, self.PORT)
        if url.startswith(base):
            url = url[len(base) :]
        helper.CPWebCase.getPage(self, url, headers, method, body, protocol)

    def getJson(self, *args, **kwargs):
        self.getPage(*args, **kwargs)
        self.assertStatus(200)
        return json.loads(self.body.decode('utf8'))

    def _login(self, username=USERNAME, password=PASSWORD):
        self.getPage("/login/", method='POST', body={'login': username, 'password': password})
        self.assertStatus('303 See Other')
