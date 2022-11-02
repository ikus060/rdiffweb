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
Created on Nov 16, 2017

@author: Patrik Dufresne
"""


from base64 import b64encode

import rdiffweb.test
from rdiffweb.core.model import UserObject


class APITest(rdiffweb.test.WebCase):

    headers = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]

    def test_get_index(self):
        data = self.getJson('/api/', headers=self.headers)
        self.assertIsNotNone(data.get('version'))

    def test_get_currentuser(self):
        data = self.getJson('/api/currentuser/', headers=self.headers)
        self.assertEqual(data.get('username'), 'admin')
        self.assertEqual(data.get('email'), '')
        # This value change on every execution.
        self.assertEqual(2, len(data.get('repos')))
        repo = data.get('repos')[1]
        self.assertEqual(repo.get('keepdays'), -1)
        self.assertEqual(repo.get('last_backup_date'), '2016-02-02T16:30:40-05:00')
        self.assertEqual(repo.get('status'), 'ok')
        self.assertEqual(repo.get('display_name'), 'testcases')
        self.assertEqual(repo.get('encoding'), 'utf-8')
        self.assertEqual(repo.get('name'), 'testcases')
        self.assertEqual(repo.get('maxage'), 0)

    def test_getapi_without_authorization(self):
        """
        Check if 401 is return when authorization is not provided.
        """
        self.getPage('/api/')
        self.assertStatus('401 Unauthorized')

    def test_getapi_without_username(self):
        """
        Check if error 401 is raised when requesting /login without a username.
        """
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b":admin123").decode('ascii'))])
        self.assertStatus('401 Unauthorized')

    def test_getapi_with_empty_password(self):
        """
        Check if 401 is return when authorization is not provided.
        """
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b"admin:").decode('ascii'))])
        self.assertStatus('401 Unauthorized')

    def test_getapi_with_invalid_password(self):
        """
        Check if 401 is return when authorization is not provided.
        """
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b"admin:invalid").decode('ascii'))])
        self.assertStatus('401 Unauthorized')

    def test_getapi_with_authorization(self):
        """
        Check if 200 is return when authorization is not provided.
        """
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))])
        self.assertStatus('200 OK')

    def test_getapi_with_session(self):
        # Given an authenticate user
        b = {'login': self.USERNAME, 'password': self.PASSWORD}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('303 See Other')
        self.getPage('/')
        self.assertStatus('200 OK')
        # When querying the API
        self.getPage('/api/')
        # Then access is refused
        self.assertStatus('401 Unauthorized')

    def test_auth_with_access_token(self):
        # Given a user with an access token
        userobj = UserObject.get_user(self.USERNAME)
        token = userobj.add_access_token('test').encode('ascii')
        userobj.commit()
        # When using this token to authenticated with /api
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b"admin:" + token).decode('ascii'))])
        # Then authentication is successful
        self.assertStatus('200 OK')

    def test_auth_failed_with_mfa_enabled(self):
        # Given a user with MFA enabled
        userobj = UserObject.get_user(self.USERNAME)
        userobj.mfa = UserObject.ENABLED_MFA
        userobj.commit()
        # When authenticating with /api/
        self.getPage('/api/', headers=self.headers)
        # Then access is refused
        self.assertStatus('401 Unauthorized')


class APIRatelimitTest(rdiffweb.test.WebCase):

    default_config = {
        'rate-limit': 5,
    }

    def test_login_ratelimit(self):
        # Given invalid credentials sent to API
        headers = [("Authorization", "Basic " + b64encode(b"admin:invalid").decode('ascii'))]
        for i in range(1, 5):
            self.getPage('/api/', headers=headers)
            self.assertStatus(401)
        # Then the 6th request is refused
        self.getPage('/api/', headers=headers)
        self.assertStatus(429)
        # Next request is also refused event if credentials are valid.
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))])
        self.assertStatus(429)
