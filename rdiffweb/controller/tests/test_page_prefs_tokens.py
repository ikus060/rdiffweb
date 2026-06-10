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
from datetime import datetime, timedelta, timezone
from unittest.mock import ANY

from parameterized import parameterized
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
            body={'action': 'add', 'name': 'test-token-name', 'expiration': ''},
        )
        # Then page return without error
        self.assertStatus(303)
        # Then token name get displayed in the view
        self.getPage("/prefs/tokens")
        self.assertStatus(200)
        self.assertInBody('test-token-name')
        # Then access token get created
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.id, Token.name == 'test-token-name').count())
        # Then and audit log is added
        userobj.expire()
        self.assertEqual({'tokens': [[], ['test-token-name']]}, userobj.changes[-1].changes)

    def test_add_access_token_with_expiration_time(self):
        # Given an existing user
        userobj = UserObject.get_user(self.USERNAME)
        # When adding a new access token
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'action': 'add', 'name': 'test-token-name', 'expiration': '1999-01-01'},
        )
        # Then page return without error
        self.assertStatus(303)
        # Then token name get displayed in the view
        self.getPage("/prefs/tokens")
        self.assertStatus(200)
        self.assertInBody('test-token-name')
        # Then access token get created
        token = Token.query.filter(Token.userid == userobj.id, Token.name == 'test-token-name').one()
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
            body={'action': 'add', 'name': '', 'expiration': ''},
        )
        # Then page return without error
        self.assertStatus(200)
        # Then token name get displayed in the view
        self.assertInBody('Token name: This field is required.')
        # Then access token is not created
        self.assertEqual(0, Token.query.filter(Token.userid == userobj.id, Token.name == 'test-token-name').count())

    @parameterized.expand(
        [
            # Success
            ('MyToken', False),
            ('My Laptop Backup', False),
            ('backup-token_v1.0', False),
            ('backup@token_v1.0-3', False),
            # Error
            ('A', 'Token name too short'),
            ('token' * 52, 'Token name too long'),
            ('', 'Token name: This field is required.'),
            (
                ' MyToken',
                'Token name: Must start with a letter and contain only letters',
            ),
            (
                '<script>',
                'Token name: Must start with a letter and contain only letters',
            ),
            (
                'say "hello"',
                'Token name: Must start with a letter and contain only letters',
            ),
        ]
    )
    def test_add_access_token_with_name(self, name, expected_body):
        # Given an existing user
        # When adding a new access token with name too long.
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'action': 'add', 'name': name, 'expiration': ''},
        )
        if expected_body:
            # Then page return with error message
            self.assertStatus(200)
            # Then token name get displayed in the view
            self.assertInBody(expected_body)
        else:
            self.assertStatus(303)

    def test_add_access_token_duplicate(self):
        # Given an existing user with access_token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test-token-name')
        userobj.commit()
        # When adding a new access token with same name
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'action': 'add', 'name': 'test-token-name', 'expiration': ''},
        )
        userobj.expire()
        # Then page return without error
        self.assertStatus(200)
        # Then token name get displayed in the view
        self.assertInBody('Duplicate token name: test-token-name')
        # Then access token get created
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.id, Token.name == 'test-token-name').count())

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
            body={'action': 'add', 'name': 'test-token-name', 'expiration': '', 'scope': scope},
        )
        # Then page return with error message
        self.assertStatus(303)
        # Then token get displayed in the view
        self.getPage("/prefs/tokens")
        self.assertStatus(200)
        self.assertInBody('test-token-name')
        self.assertInBody(expected_text)
        # Then access token get created
        token = Token.query.filter(Token.userid == userobj.id, Token.name == 'test-token-name').first()
        self.assertEqual(token.scope, [scope])

    def test_add_access_token_with_invalid_scope(self):
        # Given an existing user
        # When adding a new access token with name too long.
        self.getPage(
            "/prefs/tokens",
            method='POST',
            body={'action': 'add', 'name': 'test-token-name', 'expiration': '', 'scope': 'invalid'},
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
            body={'action': 'delete', 'name': 'test-token-name'},
        )
        # Then page return without error
        self.assertStatus(303)
        # Then token name get displayed in the view
        self.getPage("/prefs/tokens")
        self.assertStatus(200)
        self.assertInBody('The access token has been successfully deleted.')
        # Then access token is not created
        self.assertEqual(0, Token.query.filter(Token.userid == userobj.id, Token.name == 'test-token-name').count())
        # Then and audit log is added
        self.assertEqual({'tokens': [['test-token-name'], []]}, userobj.changes[-1].changes)

    def test_add_token_selenium(self):
        # Given a user without ssh key
        user_obj = UserObject.get_user('admin')
        self.assertEqual(0, len(list(user_obj.authorizedkeys)))
        with self.selenium() as driver:
            # When getting the sshkey pages
            driver.get(self.baseurl + "/prefs/tokens")
            # Then page load without error
            self.assertFalse(driver.get_log('browser'))
            # When user click on delete button
            btn = driver.find_element('css selector', '#rdw-btn-add-token')
            ActionChains(driver).scroll_to_element(btn).perform()
            btn.click()
            # Then a Modal get shown.
            modal = driver.find_element('css selector', '#rdw-add-token-modal')
            # When user enter the ssh key.
            txt_title = modal.find_element('css selector', 'input[name="name"]')
            txt_title.send_keys('My Token')
            submit_btn = modal.find_element('css selector', 'button[type="submit"]')
            submit_btn.click()
            self.assertFalse(driver.get_log('browser'))
            # Then user get redirected to home page.
            WebDriverWait(driver, 10).until(EC.staleness_of(submit_btn))
            user_obj.expire()
            self.assertEqual(1, len(list(user_obj.tokens)))

    def test_delete_token_selenium(self):
        # Given a user with a ssh key.
        user_obj = UserObject.get_user('admin')
        user_obj.add_access_token('foo')
        user_obj.commit()
        self.assertEqual(1, len(list(user_obj.tokens)))
        with self.selenium() as driver:
            # When getting the token pages
            driver.get(self.baseurl + "/prefs/tokens")
            # Then page load without error
            self.assertFalse(driver.get_log('browser'))
            # When user click on delete button
            btn = driver.find_element('css selector', '.rdw-btn-delete-token')
            ActionChains(driver).scroll_to_element(btn).perform()
            btn.click()
            # Then a Modal get shown.
            modal = driver.find_element('css selector', '#rdw-delete-token-modal')
            # When user confirm
            submit_btn = modal.find_element('css selector', 'button[type="submit"]')
            submit_btn.click()
            self.assertFalse(driver.get_log('browser'))
            # Then user get redirected to home page.
            WebDriverWait(driver, 10).until(EC.staleness_of(submit_btn))
            user_obj.expire()
            self.assertEqual(0, len(list(user_obj.tokens)))


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

        # When POST a duplicate token
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
        user.expire()
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
        # Given a user with an existing token
        user = UserObject.get_user('admin')
        user.add_access_token('my-token', None)
        user.commit()

        # When deleting the token
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
        # Given a user with an existing token
        user = UserObject.get_user('admin')
        user.add_access_token('my-token', None, scope='all,read_user')
        user.commit()

        # When querying the token
        data = self.getJson(
            '/api/currentuser/tokens/my-token',
            headers=self.auth,
            method='GET',
        )
        # Then page return with success with token
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
        # Given a user with an existing token
        user = UserObject.get_user('admin')
        user.add_access_token('my-token', None)
        user.commit()
        # When querying the token
        self.getPage(
            '/api/currentuser/tokens/invalid',
            headers=self.auth,
            method='GET',
        )
        # Then page return NotFound
        self.assertStatus(404)

    def test_list(self):
        # Given a user with an existing token
        user = UserObject.get_user('admin')
        user.add_access_token('my-token', None)
        user.commit()
        # When querying the ssh key
        data = self.getJson(
            '/api/currentuser/tokens',
            headers=self.auth,
            method='GET',
        )
        # Then page return with success with token
        self.assertStatus('200 OK')
        self.assertEqual(
            data,
            [{'title': 'my-token', 'access_time': None, 'creation_time': ANY, 'expiration_time': None, 'scope': []}],
        )
