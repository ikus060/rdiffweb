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
from datetime import datetime, timedelta, timezone

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
