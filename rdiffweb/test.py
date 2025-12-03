# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import importlib.resources
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from contextlib import contextmanager
from threading import Thread
from urllib.parse import urlencode

import cherrypy
import html5lib
from cherrypy.test import helper
from selenium import webdriver

from rdiffweb.core.model import UserObject
from rdiffweb.rdw_app import RdiffwebApp

# For cherrypy8, we need to monkey patch Thread.isAlive
Thread.isAlive = Thread.is_alive


def create_testcases_repo():
    """Extract testcases."""
    # Extract 'testcases.tar.gz'
    testcases = importlib.resources.files('rdiffweb.tests') / 'testcases.tar.gz'
    new = str(tempfile.mkdtemp(prefix='rdiffweb_tests_'))
    subdir = os.path.join(new, 'admin')
    os.makedirs(subdir)
    subprocess.check_call(['tar', '-zxf', testcases], cwd=subdir)
    return subdir


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
        # Clear cherrypy.tools.caching
        if hasattr(cherrypy, '_cache'):
            cherrypy._cache.clear()
        # Create a clean environment by creating a new database and restarting all plugins.
        cherrypy.db.clear_sessions()
        cherrypy.db.drop_all()
        cherrypy.db.create_all()
        cherrypy.engine.publish('graceful')
        # Create default admin
        admin_user = UserObject.create_admin_user(self.USERNAME, self.PASSWORD)
        admin_user.commit()
        # Create testcases repo
        self.testcases = create_testcases_repo()
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
        cherrypy.db.clear_sessions()
        # Clear cherrypy.tools.caching
        if hasattr(cherrypy, '_cache'):
            cherrypy._cache.clear()

    def assertValidHTML(self, msg=None):
        """
        Verify if the current body is compliant HTML.
        """
        try:
            parser = html5lib.HTMLParser(strict=True)
            parser.parse(self.body)
        except html5lib.html5parser.ParseError as e:
            row, col_unused = parser.errors[0][0]
            line = self.body.splitlines()[row - 1].decode('utf8', errors='replace')
            msg = msg or ('URL %s contains invalid HTML: %s on line %s: %s' % (self.url, e, row, line))
            self.fail(msg)

    @property
    def app(self):
        """
        Return reference to Rdiffweb application.
        """
        return cherrypy.tree.apps['']

    @property
    def session(self):
        return cherrypy.db.get_session()

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
        else:
            headers = list(headers)  # Make a copy of headers because if get updated.

        # When body is a dict, send the data as form data.
        if isinstance(body, dict):
            is_json_content = ('Content-Type', 'application/json') in headers
            if is_json_content:
                body = json.dumps(body).encode('utf-8')
                headers.append(('Content-length', str(len(body))))
            else:
                # Default Post form
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

    @contextmanager
    def selenium(self, headless=True):
        """
        Decorator to load selenium for a test.
        """
        # Skip selenium test is display is not available.
        if not os.environ.get('DISPLAY', False):
            raise unittest.SkipTest("selenium require a display")
        # Start selenium driver
        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('--headless')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--window-size=1280,800')
        driver = webdriver.Chrome(options=options)
        # If logged in, reuse the same session id.
        try:
            if self.session_id:
                driver.get('http://%s:%s/login/' % (self.HOST, self.PORT))
                driver.add_cookie({"name": "session_id", "value": self.session_id})
            # Get log to clear them
            _ = driver.get_log('browser')
            yield driver
        finally:
            # Code to release resource, e.g.:
            driver.close()
