# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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
import json
from base64 import b64encode
from datetime import datetime, timedelta, timezone
from unittest.mock import ANY

from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.model import Token, UserObject


class PagePrefTokensTest(rdiffweb.test.WebCase):
    login = True

    def test_get(self):
        # When getting the page
        self.getPage("/prefs/tokens")
        # Then the page is return without error
        self.assertStatus(200)

    def test_add_access_token(self):
        # Given an existing user
        userobj = UserObject.get_user(self.USERNAME)
        # When adding a new access token
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'add_access_token': '1', 'name': 'test-token-name', 'expiration': ''},
        )
        # Then page return without error
        self.assertStatus(303)
        # Then token name get displayed in the view
        self.getPage("/prefs/tokens")
        self.assertStatus(200)
        self.assertInBody('test-token-name')
        # Then access token get created
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid, Token.name == 'test-token-name').count())

    def test_add_access_token_with_expiration_time(self):
        # Given an existing user
        userobj = UserObject.get_user(self.USERNAME)
        # When adding a new access token
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'add_access_token': '1', 'name': 'test-token-name', 'expiration': '1999-01-01'},
        )
        # Then page return without error
        self.assertStatus(303)
        # Then token name get displayed in the view
        self.getPage("/prefs/tokens")
        self.assertStatus(200)
        self.assertInBody('test-token-name')
        # Then access token get created
        token = Token.query.filter(Token.userid == userobj.userid, Token.name == 'test-token-name').one()
        self.assertIsNotNone(token.expiration_time)
        # Expiration is almost equals to consider the timezone.
        self.assertAlmostEqual(
            token.expiration_time, datetime(1999, 1, 1, tzinfo=timezone.utc), delta=timedelta(hours=24)
        )

    def test_add_access_token_without_name(self):
        # Given an existing user
        userobj = UserObject.get_user(self.USERNAME)
        # When adding a new access token
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'add_access_token': '1', 'name': '', 'expiration': ''},
        )
        # Then page return without error
        self.assertStatus(200)
        # Then token name get displayed in the view
        self.assertInBody('Token name: This field is required.')
        # Then access token is not created
        self.assertEqual(0, Token.query.filter(Token.userid == userobj.userid, Token.name == 'test-token-name').count())

    def test_add_access_token_with_name_too_long(self):
        # Given an existing user
        # When adding a new access token with name too long.
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'add_access_token': '1', 'name': 'token' * 52, 'expiration': ''},
        )
        # Then page return with error message
        self.assertStatus(200)
        # Then token name get displayed in the view
        self.assertInBody('Token name too long')

    def test_add_access_token_duplicate(self):
        # Given an existing user with access_token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test-token-name')
        userobj.commit()
        # When adding a new access token with same name
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'add_access_token': '1', 'name': 'test-token-name', 'expiration': ''},
        )
        # Then page return without error
        self.assertStatus(200)
        # Then token name get displayed in the view
        self.assertInBody('Duplicate token name: test-token-name')
        # Then access token get created
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid, Token.name == 'test-token-name').count())

    @parameterized.expand(
        [
            ('all', 'Everything'),
            ('read_user', 'Read user settings'),
            ('write_user', 'Write user settings'),
        ]
    )
    def test_add_access_token_with_scope(self, scope, expected_text):
        # Given an existing user
        userobj = UserObject.get_user(self.USERNAME)
        # When adding a new access token with name too long.
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'add_access_token': '1', 'name': 'test-token-name', 'expiration': '', 'scope': scope},
        )
        # Then page return with error message
        self.assertStatus(303)
        # Then token get displayed in the view
        self.getPage("/prefs/tokens")
        self.assertStatus(200)
        self.assertInBody('test-token-name')
        self.assertInBody(expected_text)
        # Then access token get created
        token = Token.query.filter(Token.userid == userobj.userid, Token.name == 'test-token-name').first()
        self.assertEqual(token.scope, [scope])

    def test_add_access_token_with_invalid_scope(self):
        # Given an existing user
        # When adding a new access token with name too long.
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'add_access_token': '1', 'name': 'test-token-name', 'expiration': '', 'scope': 'invalid'},
        )
        # Then page return with error message
        self.assertStatus(200)
        # Then token name get displayed in the view
        self.assertInBody('&#39;invalid&#39; is not a valid choice for this field')

    def test_delete_access_token(self):
        # Given an existing user with access_token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test-token-name')
        userobj.commit()
        # When deleting access token
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'revoke': '1', 'name': 'test-token-name'},
        )
        # Then page return without error
        self.assertStatus(303)
        # Then token name get displayed in the view
        self.getPage("/prefs/tokens")
        self.assertStatus(200)
        self.assertInBody('The access token has been successfully deleted.')
        # Then access token is not created
        self.assertEqual(0, Token.query.filter(Token.userid == userobj.userid, Token.name == 'test-token-name').count())


class ApiTokensTest(rdiffweb.test.WebCase):
    auth = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]

    def test_post(self):
        # Given a user without tokens
        user = UserObject.get_user('admin')

        # When POST a valid token
        data = self.getJson(
            '/api/currentuser/tokens',
            headers=self.auth,
            method='POST',
            body={'name': "my-token"},
        )
        # Then page return a new secret
        self.assertIn('token', data)
        # Then key get added to the user
        self.assertEqual(1, Token.query.filter(Token.user == user).count())

    def test_post_json(self):
        # Given a user without tokens
        user = UserObject.get_user('admin')

        # When POST a valid token
        data = self.getJson(
            '/api/currentuser/tokens',
            headers=self.auth + [('Content-Type', 'application/json')],
            method='POST',
            body={'name': "my-token"},
        )
        # Then page return a new secret
        self.assertIn('token', data)
        # Then key get added to the user
        self.assertEqual(1, Token.query.filter(Token.user == user).count())

    def test_post_duplicate(self):
        # Given a user with an existing Token
        user = UserObject.get_user('admin')
        user.add_access_token('my-token', None)
        user.commit()

        # When POST a duplicate ssh key
        self.getPage(
            '/api/currentuser/tokens',
            headers=self.auth,
            method='POST',
            body={'name': "my-token"},
        )
        # Then page return error
        self.assertStatus(400)
        self.assertEqual(1, Token.query.filter(Token.user == user).count())

    @parameterized.expand(
        [
            ('all', True),
            ('write_user', True),
            ('read_user', False),
            (None, False),
        ]
    )
    def test_post_with_access_token(self, scope, success):
        # Given a user with an access token
        user = UserObject.get_user('admin')
        token = user.add_access_token(name='test', scope=scope)
        user.commit()
        headers = [("Authorization", "Basic " + b64encode(f"admin:{token}".encode('ascii')).decode('ascii'))]
        # When adding a ssh key
        self.getPage(
            '/api/currentuser/tokens',
            headers=headers,
            method='POST',
            body={'name': "my-token", "scope": "all"},
        )
        # Then sh get added or permissions is refused
        if success:
            self.assertStatus(200)
            self.assertEqual(2, Token.query.filter(Token.user == user).count())
            self.assertEqual(
                json.loads(self.body.decode('utf8')),
                {
                    'title': 'my-token',
                    'access_time': None,
                    'creation_time': ANY,
                    'expiration_time': None,
                    'token': ANY,
                    'scope': ["all"],
                },
            )
        else:
            self.assertStatus(403)
            self.assertEqual(1, Token.query.filter(Token.user == user).count())

    def test_delete(self):
        # Given a user with an existing ssh key
        user = UserObject.get_user('admin')
        user.add_access_token('my-token', None)
        user.commit()

        # When deleting the ssh key
        self.getPage(
            '/api/currentuser/tokens/my-token',
            headers=self.auth,
            method='DELETE',
        )
        # Then page return with success
        self.assertStatus('200 OK')

        # Then key get deleted from database
        self.assertEqual(0, Token.query.filter(Token.user == user).count())

    def test_get(self):
        # Given a user with an existing ssh key
        user = UserObject.get_user('admin')
        user.add_access_token('my-token', None, scope='all,read_user')
        user.commit()

        # When deleting the ssh key
        data = self.getJson(
            '/api/currentuser/tokens/my-token',
            headers=self.auth,
            method='GET',
        )
        # Then page return with success with sshkey
        self.assertStatus('200 OK')
        self.assertEqual(
            data,
            {
                'title': 'my-token',
                'access_time': None,
                'creation_time': ANY,
                'expiration_time': None,
                'scope': ['all', 'read_user'],
            },
        )

    def test_get_invalid(self):
        # Given a user with an existing ssh key
        user = UserObject.get_user('admin')
        user.add_access_token('my-token', None)
        user.commit()
        # When deleting the ssh key
        self.getPage(
            '/api/currentuser/tokens/invalid',
            headers=self.auth,
            method='GET',
        )
        # Then page return with success with sshkey
        self.assertStatus(404)

    def test_list(self):
        # Given a user with an existing ssh key
        user = UserObject.get_user('admin')
        user.add_access_token('my-token', None)
        user.commit()
        # When deleting the ssh key
        data = self.getJson(
            '/api/currentuser/tokens',
            headers=self.auth,
            method='GET',
        )
        # Then page return with success with sshkey
        self.assertStatus('200 OK')
        self.assertEqual(
            data,
            [{'title': 'my-token', 'access_time': None, 'creation_time': ANY, 'expiration_time': None, 'scope': []}],
        )
