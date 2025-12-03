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
from unittest.mock import MagicMock, patch

import cherrypy
import ldap3
import responses

import rdiffweb.test
from rdiffweb.core.model import UserObject

original_connection = ldap3.Connection


def mock_ldap_connection(*args, **kwargs):
    kwargs.pop('client_strategy', None)
    return original_connection(*args, client_strategy=ldap3.MOCK_ASYNC, **kwargs)


class AbstractLdapLoginTest:
    @classmethod
    def teardown_class(cls):
        cherrypy.ldap.uri = None
        # Release Ldap mock server.
        cls.patcher.stop()
        return super().teardown_class()

    @classmethod
    def setup_server(cls):
        # Configure Mock server early.
        cls.server = ldap3.Server('my_fake_server')
        cls.patcher = patch('ldap3.Connection', side_effect=mock_ldap_connection)
        cls.patcher.start()
        cherrypy.config.update(
            {
                'ldap.uri': 'my_fake_server',
                'ldap.base_dn': 'dc=example,dc=org',
                'ldap.email_attribute': ['mail', 'email'],
                'ldap.fullname_attribute': ['displayName'],
                'ldap.firstname_attribute': ['givenName'],
                'ldap.lastname_attribute': ['sn'],
            }
        )
        # Get defaultconfig from test class
        default_config = getattr(cls, 'default_config', {})
        default_config['ldap-uri'] = 'my_fake_server'
        default_config['ldap-base-dn'] = 'dc=example,dc=org'
        super().setup_server()

    def setUp(self):
        super().setUp()
        self.listener = MagicMock()
        cherrypy.engine.subscribe('user_added', self.listener.user_added, priority=50)
        cherrypy.engine.subscribe('user_updated', self.listener.user_updated, priority=50)
        cherrypy.engine.subscribe('user_deleted', self.listener.user_deleted, priority=50)
        cherrypy.engine.subscribe('user_login', self.listener.user_login, priority=50)
        cherrypy.engine.subscribe('user_password_changed', self.listener.user_password_changed, priority=50)
        # Clear LDAP entries before test.
        for entry in list(cherrypy.ldap._pool.strategy.connection.server.dit):
            if entry == 'cn=schema':
                continue
            cherrypy.ldap._pool.strategy.remove_entry(entry)
        # Create a default user
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=tony,dc=example,dc=org',
            {
                'displayName': ['Tony Martinez'],
                'userPassword': 'password1',
                'uid': ['tony'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'mail': ['myemail@example.com'],
            },
        )

    def tearDown(self):
        cherrypy.engine.unsubscribe('user_added', self.listener.user_added)
        cherrypy.engine.unsubscribe('user_updated', self.listener.user_updated)
        cherrypy.engine.unsubscribe('user_deleted', self.listener.user_deleted)
        cherrypy.engine.unsubscribe('user_login', self.listener.user_login)
        cherrypy.engine.unsubscribe('user_password_changed', self.listener.user_password_changed)
        return super().tearDown()


class LdapLoginTest(AbstractLdapLoginTest, rdiffweb.test.WebCase):
    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=nodomain',
        'ldap-email-attribute': 'mail',
        'ldap-fullname-attribute': 'displayName',
    }

    def test_login_invalid(self):
        # Given an existing user in database.
        UserObject.add_user(username='tony').add().commit()
        # When trying tol ogin with invalid password with that user
        self.getPage("/logout", method="POST")
        self.getPage("/login/", method='POST', body={'login': 'tony', 'password': 'invalid'})
        self.assertStatus(200)
        # Then user is not authenticated.
        self.assertInBody('Invalid username or password.')

    def test_login_with_existing_user(self):
        # Given an existing user in database.
        userobj = UserObject.add_user(username='tony').add().commit()
        # When login successfully with that user
        self._login('tony', 'password1')
        # Then user is updated
        userobj.expire()
        self.assertFalse(userobj.is_admin)
        self.assertEqual('myemail@example.com', userobj.email)
        self.assertEqual('Tony Martinez', userobj.fullname)


class LdapLoginAddMissingTest(AbstractLdapLoginTest, rdiffweb.test.WebCase):
    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=nodomain',
        'ldap-email-attribute': 'mail',
        'ldap-fullname-attribute': 'displayName',
        'add-missing-user': 'true',
        'add-user-default-role': 'maintainer',
        'add-user-default-userroot': '/backups/users/{uid[0]}',
    }

    def test_login_with_create_user(self):
        # Given a user doesn't exists in database
        self.assertIsNone(UserObject.get_user('tony'))
        # When login successfully with that user
        self._login('tony', 'password1')
        # Then user is create in database
        userobj = UserObject.get_user('tony')
        self.assertIsNotNone(userobj)
        self.assertFalse(userobj.is_admin)
        self.assertEqual(UserObject.MAINTAINER_ROLE, userobj.role)
        self.assertEqual('/backups/users/tony', userobj.user_root)
        self.assertEqual('myemail@example.com', userobj.email)
        self.assertEqual('Tony Martinez', userobj.fullname)
        # Check listener
        self.listener.user_added.assert_called_once_with(userobj)
        self.listener.user_login.assert_called_once_with(userobj)

    def test_login_with_update_user(self):
        # Given an existing user in database.
        userobj = UserObject.add_user(username='tony').add().commit()
        # When login successfully with that user
        self._login('tony', 'password1')
        # Then user is updated
        userobj.expire()
        self.assertFalse(userobj.is_admin)
        self.assertEqual('myemail@example.com', userobj.email)
        self.assertEqual('Tony Martinez', userobj.fullname)


class AbstractOAuthLoginTest:
    def setUp(self):
        super().setUp()
        # Mock OAuth provider.
        responses.add(
            responses.POST,
            "https://mock-provider.com/oauth/token",
            json={
                "access_token": "mock_access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "mock_refresh_token",
            },
            status=200,
        )
        responses.add(
            responses.GET,
            "https://mock-provider.com/user",
            json={"id": "12345", "email": "tony@example.com", "name": "Tony Martinez", "nickname": "tony"},
            status=200,
            headers={"Authorization": "Bearer mock_access_token"},
        )
        responses.start()
        self.listener = MagicMock()
        cherrypy.engine.subscribe('user_added', self.listener.user_added, priority=50)
        cherrypy.engine.subscribe('user_login', self.listener.user_login, priority=50)

    def tearDown(self):
        responses.stop()
        responses.reset()
        cherrypy.engine.unsubscribe('user_added', self.listener.user_added)
        cherrypy.engine.unsubscribe('user_login', self.listener.user_login)
        return super().tearDown()


class OAuthLoginWithUsernameTest(AbstractOAuthLoginTest, rdiffweb.test.WebCase):
    default_config = {
        'oauth-client-id': "test_client_id",
        'oauth-client-secret': "test_client_secret",
        'oauth-auth-url': "https://mock-provider.com/oauth/authorize",
        'oauth-token-url': "https://mock-provider.com/oauth/token",
        'oauth-userinfo-url': "https://mock-provider.com/user",
        'oauth-fullname-claim': "name",
        'oauth-userkey-claim': "nickname",
        'login-with-email': False,
    }

    def test_login_success(self):
        # Given user exists
        userobj = UserObject.add_user('tony', email='random@email.com').commit()
        # When user try to loging with OAuth
        self.getPage('/oauth/login')
        # Then user is redirect to oauth provider
        self.assertStatus(303)
        redirect = self.assertHeader('Location')
        self.assertIn(
            'https://mock-provider.com/oauth/authorize?response_type=code&client_id=test_client_id&redirect_uri=http%3A%2F%2F127.0.0.1%3A54583%2Foauth%2Fcallback&scope=openid+profile+email&state=',
            redirect,
        )
        state = redirect.split('state=')[1]
        # When OAuth provider redirect to callback
        self.getPage(f'/oauth/callback?code=test&state={state}')
        # Then user is redirect to main page.
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', 'http://%s:%s/' % (self.HOST, self.PORT))
        # Then user is authenticated
        self.getPage('/', headers=self.cookies)
        self.assertStatus(200)
        # Then user is create in database
        userobj.expire()
        self.assertEqual('Tony Martinez', userobj.fullname)
        # Then listener got called.
        self.listener.user_login.assert_called_once_with(userobj)


class OAuthLoginWithEmailTest(AbstractOAuthLoginTest, rdiffweb.test.WebCase):
    default_config = {
        'oauth-client-id': "test_client_id",
        'oauth-client-secret': "test_client_secret",
        'oauth-auth-url': "https://mock-provider.com/oauth/authorize",
        'oauth-token-url': "https://mock-provider.com/oauth/token",
        'oauth-userinfo-url': "https://mock-provider.com/user",
        'oauth-fullname-claim': "name",
        'oauth-userkey-claim': "email",
        'login-with-email': True,
    }

    def test_login_success(self):
        # Given user exists
        userobj = UserObject.add_user('myuser', email='tony@example.com').commit()
        # When user try to loging with OAuth
        self.getPage('/oauth/login')
        # Then user is redirect to oauth provider
        self.assertStatus(303)
        redirect = self.assertHeader('Location')
        self.assertIn(
            'https://mock-provider.com/oauth/authorize?response_type=code&client_id=test_client_id&redirect_uri=http%3A%2F%2F127.0.0.1%3A54583%2Foauth%2Fcallback&scope=openid+profile+email&state=',
            redirect,
        )
        state = redirect.split('state=')[1]
        # When OAuth provider redirect to callback
        self.getPage(f'/oauth/callback?code=test&state={state}')
        # Then user is redirect to main page.
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', 'http://%s:%s/' % (self.HOST, self.PORT))
        # Then user is authenticated
        self.getPage('/', headers=self.cookies)
        self.assertStatus(200)
        # Then user is create in database
        userobj.expire()
        self.assertEqual('Tony Martinez', userobj.fullname)
        # Then listener got called.
        self.listener.user_login.assert_called_once_with(userobj)


class OAuthLoginAddMissingTest(AbstractOAuthLoginTest, rdiffweb.test.WebCase):
    default_config = {
        'oauth-client-id': "test_client_id",
        'oauth-client-secret': "test_client_secret",
        'oauth-auth-url': "https://mock-provider.com/oauth/authorize",
        'oauth-token-url': "https://mock-provider.com/oauth/token",
        'oauth-userinfo-url': "https://mock-provider.com/user",
        'oauth-fullname-claim': "name",
        'oauth-userkey-claim': "nickname",
        'add-missing-user': 'true',
        'add-user-default-role': 'maintainer',
        'add-user-default-userroot': '/backups/users/{username}',
    }

    def test_login_with_create_user(self):
        # Given a user doesn't exists in database
        self.assertIsNone(UserObject.get_user('tony'))
        # When user try to loging with OAuth
        self.getPage('/oauth/login')
        # Then user is redirect to oauth provider
        self.assertStatus(303)
        redirect = self.assertHeader('Location')
        self.assertIn(
            'https://mock-provider.com/oauth/authorize?response_type=code&client_id=test_client_id&redirect_uri=http%3A%2F%2F127.0.0.1%3A54583%2Foauth%2Fcallback&scope=openid+profile+email&state=',
            redirect,
        )
        state = redirect.split('state=')[1]
        # When OAuth provider redirect to callback
        self.getPage(f'/oauth/callback?code=test&state={state}')
        # Then user is redirect to main page.
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', 'http://%s:%s/' % (self.HOST, self.PORT))
        # Then user is authenticated
        self.getPage('/', headers=self.cookies)
        self.assertStatus(200)
        # Then user is create in database
        userobj = UserObject.get_user('tony')
        self.assertIsNotNone(userobj)
        self.assertFalse(userobj.is_admin)
        self.assertEqual(UserObject.MAINTAINER_ROLE, userobj.role)
        self.assertEqual('/backups/users/tony', userobj.user_root)
        self.assertEqual('tony@example.com', userobj.email)
        self.assertEqual('Tony Martinez', userobj.fullname)
        # Then listener got called.
        self.listener.user_added.assert_called_once_with(userobj)
        self.listener.user_login.assert_called_once_with(userobj)


class OAuthLoginAddMissingWithEmailTest(AbstractOAuthLoginTest, rdiffweb.test.WebCase):
    default_config = {
        'oauth-client-id': "test_client_id",
        'oauth-client-secret': "test_client_secret",
        'oauth-auth-url': "https://mock-provider.com/oauth/authorize",
        'oauth-token-url': "https://mock-provider.com/oauth/token",
        'oauth-userinfo-url': "https://mock-provider.com/user",
        'oauth-fullname-claim': "name",
        'oauth-userkey-claim': "email",
        'add-missing-user': 'true',
        'add-user-default-role': 'maintainer',
        'add-user-default-userroot': '/backups/users/{username}',
    }

    def test_login_with_create_user(self):
        # Given a user doesn't exists in database
        self.assertIsNone(UserObject.get_user('tony'))
        # When user try to loging with OAuth
        self.getPage('/oauth/login')
        # Then user is redirect to oauth provider
        self.assertStatus(303)
        redirect = self.assertHeader('Location')
        self.assertIn(
            'https://mock-provider.com/oauth/authorize?response_type=code&client_id=test_client_id&redirect_uri=http%3A%2F%2F127.0.0.1%3A54583%2Foauth%2Fcallback&scope=openid+profile+email&state=',
            redirect,
        )
        state = redirect.split('state=')[1]
        # When OAuth provider redirect to callback
        self.getPage(f'/oauth/callback?code=test&state={state}')
        # Then user is redirect to main page.
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', 'http://%s:%s/' % (self.HOST, self.PORT))
        # Then user is authenticated
        self.getPage('/', headers=self.cookies)
        self.assertStatus(200)
        # Then user is create in database
        userobj = UserObject.get_user('tony_example.com')
        self.assertIsNotNone(userobj)
        self.assertFalse(userobj.is_admin)
        self.assertEqual(UserObject.MAINTAINER_ROLE, userobj.role)
        self.assertEqual('/backups/users/tony_example.com', userobj.user_root)
        self.assertEqual('tony@example.com', userobj.email)
        self.assertEqual('Tony Martinez', userobj.fullname)
        # Then listener got called.
        self.listener.user_added.assert_called_once_with(userobj)
        self.listener.user_login.assert_called_once_with(userobj)
