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
        self.getPage(path)
        self.assertStatus(200)

    def test_static_invalid_method(self):
        """
        Check if the theme is properly configure.
        """
        self.getPage("/static/default.css", method="POST")
        self.assertStatus(405)

    def test_static_invalid_file(self):
        """
        Check if the theme is properly configure.
        """
        self.getPage("/static/invalid.css")
        self.assertStatus(404)


class ControllerOrangeThemeTest(rdiffweb.test.WebCase):

    login = True

    default_config = {'DefaultTheme': 'orange'}

    def test_theme(self):
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


class ControllerEnrichSession(rdiffweb.test.WebCase):
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
