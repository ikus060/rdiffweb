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
import json
from base64 import b64encode

from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.model import UserObject


class APITest(rdiffweb.test.WebCase):
    headers = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]

    def test_get_index(self):
        data = self.getJson('/api/', headers=self.headers)
        self.assertIsNotNone(data.get('version'))

    @parameterized.expand(
        [
            ('all', True),
            ('write_user', True),
            ('read_user', True),
            (None, True),
        ]
    )
    def test_get_index_with_access_token(self, scope, success):
        # Given a user with access token
        user = UserObject.get_user('admin')
        token = user.add_access_token(name='test', scope=scope)
        user.commit()
        headers = [("Authorization", "Basic " + b64encode(f"admin:{token}".encode('ascii')).decode('ascii'))]
        # When querying current user info
        self.getPage('/api/', headers=headers)
        # Then an error is raised or data is returned
        if success:
            self.assertStatus(200)
        else:
            self.assertStatus(403)

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

    @parameterized.expand(
        [
            ('all', True),
            ('write_user', True),
            ('read_user', True),
            (None, False),
        ]
    )
    def test_get_currentuser_with_access_token(self, scope, success):
        # Given a user with access token
        user = UserObject.get_user('admin')
        token = user.add_access_token(name='test', scope=scope)
        user.commit()
        headers = [("Authorization", "Basic " + b64encode(f"admin:{token}".encode('ascii')).decode('ascii'))]
        # When querying current user info
        self.getPage('/api/currentuser/', headers=headers)
        # Then an error is raised or data is returned
        if success:
            self.assertStatus(200)
        else:
            self.assertStatus(403)

    @parameterized.expand(
        [
            # Not suported field
            ('userid', '1234', False),
            ('username', 'myuser', False),
            ('role', 'guest', False),
            ('mfa', '1', False),
            # Supported field.
            ('fullname', 'My Name', True),
            ('email', 'test@test.com', True),
            ('lang', 'fr', True),
            ('report_time_range', '30', True),
        ]
    )
    def test_post_currentuser(self, field, new_value, success):
        # When trying to update user's settings
        self.getPage(
            '/api/currentuser',
            headers=self.headers,
            method='POST',
            body={field: new_value},
        )
        # Then it's working or not
        user = UserObject.get_user('admin')
        if success:
            self.assertStatus(200)
            self.assertEqual(str(getattr(user, field)), new_value)
        else:
            self.assertStatus(400)
            self.assertNotEqual(str(getattr(user, field)), new_value)

    def test_post_currentuser_json(self):
        # When trying to update currentuser with json payload
        self.getPage(
            '/api/currentuser',
            headers=self.headers + [('Content-Type', 'application/json')],
            method='POST',
            body={"fullname": "My Name", "lang": "fr"},
        )
        # Then it's working.
        user = UserObject.get_user('admin')
        self.assertStatus(200)
        self.assertEqual(user.fullname, "My Name")
        self.assertEqual(user.lang, "fr")

    def test_post_currentuser_invalid_json(self):
        # When trying to update invalid field
        self.getPage(
            '/api/currentuser',
            headers=self.headers + [('Content-Type', 'application/json')],
            method='POST',
            body={"invalid_field": "My Name"},
        )
        # Then an error is return as Json
        self.assertStatus(400)
        self.assertEqual(
            json.loads(self.body.decode('utf8')),
            {"message": "unsuported field: invalid_field", "status": "400 Bad Request"},
        )

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
