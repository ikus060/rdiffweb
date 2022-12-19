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
import time
import unittest
import unittest.mock
from threading import Thread
from urllib.parse import urlencode

import cherrypy
import pkg_resources
from cherrypy.test import helper

from rdiffweb.core.model import UserObject
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
        cherrypy.tools.db.drop_all()
        if hasattr(cherrypy, '_cache'):
            cherrypy._cache.clear()

    @classmethod
    def setup_server(cls):
        # Allow defining a custom database uri for testing.
        uri = os.environ.get(
            'RDIFFWEB_TEST_DATABASE_URI', 'sqlite:///' + tempfile.gettempdir() + '/test_rdiffweb_data.db'
        )
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
        if hasattr(cherrypy, '_cache'):
            cherrypy._cache.clear()
        cherrypy.tools.db.drop_all()
        cherrypy.tools.db.create_all()
        # Create default admin
        admin_user = UserObject.create_admin_user(self.USERNAME, self.PASSWORD)
        admin_user.commit()
        # Create testcases repo
        self.testcases = create_testcases_repo(self.app)
        if admin_user:
            admin_user.user_root = self.testcases
            admin_user.refresh_repos()
            admin_user.commit()
        # Login to web application.
        if self.login:
            self._login()

    def tearDown(self):
        if hasattr(self, 'testcases'):
            shutil.rmtree(self.testcases)
            delattr(self, 'testcases')
        cherrypy.tools.db.drop_all()
        if hasattr(cherrypy, '_cache'):
            cherrypy._cache.clear()

    @property
    def app(self):
        """
        Return reference to Rdiffweb application.
        """
        return cherrypy.tree.apps['']

    @property
    def session(self):
        return cherrypy.tools.db.get_session()

    @property
    def session_id(self):
        if hasattr(self, 'cookies') and self.cookies:
            for unused, value in self.cookies:
                for part in value.split(';'):
                    key, unused, value = part.partition('=')
                    if key == 'session_id':
                        return value

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
        self.getPage("/logout", method="POST")
        self.getPage("/login/", method='POST', body={'login': username, 'password': password})
        self.assertStatus('303 See Other')

    def wait_for_tasks(self):
        time.sleep(1)
        while len(cherrypy.scheduler.list_tasks()) or cherrypy.scheduler.is_job_running():
            time.sleep(1)
