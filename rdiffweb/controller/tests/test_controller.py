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
Created on Mar 13, 2019

@author: Patrik Dufresne
"""

import datetime

from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.model import DbSession, SessionObject


class ControllerTest(rdiffweb.test.WebCase):

    login = True

    default_config = {'HeaderName': 'MyTest'}

    def test_headername(self):
        """
        Check if the headername is used in the page.
        """
        self.getPage("/")
        self.assertStatus('200 OK')
        self.assertInBody('MyTest')

    def test_proxy(self):
        """
        Check if the headername is used in the page.
        """
        self.getPage("/", headers=[('Host', 'this.is.a.test.com')])
        self.assertStatus('200 OK')
        self.assertInBody('http://this.is.a.test.com/favicon.ico')

    def test_proxy_https(self):
        """
        Check if the headername is used in the page.
        """
        self.getPage("/", headers=[('Host', 'this.is.a.test.com'), ('X-Forwarded-Proto', 'https')])
        self.assertStatus('200 OK')
        self.assertInBody('https://this.is.a.test.com/favicon.ico')

    @parameterized.expand(
        [
            '/favicon.ico',
            '/static/blue.css',
            '/static/css/bootstrap.min.css',
            '/static/css/font-awesome.min.css',
            '/static/css/jquery.dataTables.min.css',
            '/static/default.css',
            '/static/js/bootstrap.bundle.min.js',
            '/static/js/jquery.dataTables.min.js',
            '/static/js/jquery.min.js',
            '/static/js/rdiffweb.js',
            '/static/orange.css',
        ]
    )
    def test_static_files(self, path):
        """
        Check if the theme is properly configure.
        """
        self.getPage('/logout')
        self.getPage(path)
        self.assertStatus(200)

    def test_static_invalid_method(self):
        """
        Check if the theme is properly configure.
        """
        self.getPage("/static/default.css", method="POST")
        self.assertStatus(400)

    def test_static_invalid_file(self):
        """
        Check if the theme is properly configure.
        """
        self.getPage("/static/invalid.css")
        self.assertStatus(400)

    def test_path_traversal(self):
        self.getPage('/static//../../test.txt')
        self.assertStatus(403)


class ControllerOrangeThemeTest(rdiffweb.test.WebCase):

    login = True

    default_config = {'DefaultTheme': 'orange'}

    def test_static(self):
        """
        Check if the theme is properly configure.
        """
        self.getPage("/")
        self.assertStatus('200 OK')
        self.assertInBody('/static/orange.css')


class ControllerBlueThemeTest(rdiffweb.test.WebCase):

    login = True

    default_config = {'DefaultTheme': 'blue'}

    def test_theme(self):
        """
        Check if the theme is properly configure.
        """
        self.getPage("/")
        self.assertInBody('/static/blue.css')


class ControllerSession(rdiffweb.test.WebCase):
    def test_enrich_session_anonymous(self):
        # When making a query to a page while unauthenticated
        self.getPage('/', headers=[('User-Agent', 'test')])
        # Then a session object is enriched
        self.assertEqual(1, SessionObject.query.filter(SessionObject.id == self.session_id).count())
        SessionObject.query.filter(SessionObject.id == self.session_id).first()
        session = DbSession(id=self.session_id)
        session.load()
        self.assertIsNotNone(session.get('ip_address'))
        self.assertIsNotNone(session.get('user_agent'))
        self.assertIsNotNone(session.get('access_time'))

    def test_enrich_session_authenticated(self):
        # When making a query to a page while unauthenticated
        self.getPage(
            '/login/',
            method='POST',
            headers=[('User-Agent', 'test')],
            body={'login': self.USERNAME, 'password': self.PASSWORD},
        )
        # Then a session object is enriched
        self.assertEqual(1, SessionObject.query.filter(SessionObject.id == self.session_id).count())
        SessionObject.query.filter(SessionObject.id == self.session_id).first()
        session = DbSession(id=self.session_id)
        session.load()
        self.assertIsNotNone(session.get('ip_address'))
        self.assertIsNotNone(session.get('user_agent'))
        self.assertIsNotNone(session.get('access_time'))

    def test_create_session(self):
        # Given a server with no session.
        self.assertEqual(0, len(SessionObject.query.all()))
        # When querying a new page
        self.getPage('/')
        self.assertStatus(303)
        # Then a new session get created
        self.assertEqual(1, len(SessionObject.query.all()))
        session = SessionObject.query.filter(SessionObject.id == self.session_id).first()
        self.assertIsNotNone(session)

    def test_clean_up_session(self):
        # Given a server with a session
        self.getPage('/')
        self.assertStatus(303)
        self.assertEqual(1, len(SessionObject.query.all()))
        # When this session get old
        data = SessionObject.query.filter(SessionObject.id == self.session_id).first()
        data.expiration_time = datetime.datetime.now() - datetime.timedelta(seconds=1)
        data.add()
        session = DbSession(id=self.session_id)
        # Then the session get deleted by clean_up process
        session.clean_up()
        # Then session is deleted
        data = SessionObject.query.filter(SessionObject.id == self.session_id).first()
        self.assertIsNone(data)
