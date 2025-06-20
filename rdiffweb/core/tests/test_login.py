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

import rdiffweb.test
from rdiffweb.core.model import UserObject


class LoginAbstractTest(rdiffweb.test.WebCase):
    def setUp(self):
        super().setUp()
        self.listener = MagicMock()
        cherrypy.engine.subscribe('user_added', self.listener.user_added, priority=50)
        cherrypy.engine.subscribe('user_attr_changed', self.listener.user_attr_changed, priority=50)
        cherrypy.engine.subscribe('user_deleted', self.listener.user_deleted, priority=50)
        cherrypy.engine.subscribe('user_login', self.listener.user_login, priority=50)
        cherrypy.engine.subscribe('user_password_changed', self.listener.user_password_changed, priority=50)

    def tearDown(self):
        cherrypy.engine.unsubscribe('user_added', self.listener.user_added)
        cherrypy.engine.unsubscribe('user_attr_changed', self.listener.user_attr_changed)
        cherrypy.engine.unsubscribe('user_deleted', self.listener.user_deleted)
        cherrypy.engine.unsubscribe('user_login', self.listener.user_login)
        cherrypy.engine.unsubscribe('user_password_changed', self.listener.user_password_changed)
        return super().tearDown()


class LoginTest(LoginAbstractTest):
    def test_login(self):
        # Given a valid user in database with a password
        userobj = UserObject.add_user('tom', 'password')
        userobj.commit()
        # When trying to login with valid password
        login = cherrypy.engine.publish('login', 'tom', 'password')
        # Then login is successful
        self.assertEqual(login, [userobj])
        # Check if listener called
        self.listener.user_login.assert_called_once_with(userobj)

    def test_login_with_invalid_password(self):
        userobj = UserObject.add_user('jeff', 'password')
        userobj.commit()
        self.assertFalse(any(cherrypy.engine.publish('login', 'jeff', 'invalid')))
        # password is case sensitive
        self.assertFalse(any(cherrypy.engine.publish('login', 'jeff', 'Password')))
        # Match entire password
        self.assertFalse(any(cherrypy.engine.publish('login', 'jeff', 'pass')))
        self.assertFalse(any(cherrypy.engine.publish('login', 'jeff', '')))
        # Check if listener called
        self.listener.user_login.assert_not_called()

    def test_login_with_invalid_user(self):
        # Given a database without users
        # When trying to login with an invalid user
        login = cherrypy.engine.publish('login', 'josh', 'password')
        # Then login is not successful
        self.assertEqual(login, [None])
        # Check if listener called
        self.listener.user_login.assert_not_called()


class LoginWithAddMissing(LoginAbstractTest):
    default_config = {'ldap-uri': '__default__', 'ldap-base-dn': 'dc=nodomain', 'ldap-add-missing-user': 'true'}

    def setUp(self):
        super().setUp()
        cherrypy.engine.subscribe('authenticate', self.listener.authenticate, priority=50)

    def tearDown(self):
        cherrypy.engine.unsubscribe('authenticate', self.listener.authenticate)
        super().tearDown()

    def test_login_with_create_user(self):
        # Given an external authentication
        self.listener.authenticate.return_value = ('tony', {})
        # Given a user doesn't exists in database
        self.assertIsNone(UserObject.get_user('tony'))
        # When login successfully with that user
        login = cherrypy.engine.publish('login', 'tony', 'password')
        self.assertIsNotNone(login)
        userobj = login[0]
        # Then user is created in database
        self.assertIsNotNone(UserObject.get_user('tony'))
        self.assertFalse(userobj.is_admin)
        self.assertEqual(UserObject.USER_ROLE, userobj.role)
        self.assertEqual('', userobj.user_root)
        self.assertEqual('', userobj.email)
        # Check listener
        self.listener.authenticate.assert_called_once_with('tony', 'password')
        self.listener.user_added.assert_called_once_with(userobj)
        self.listener.user_login.assert_called_once_with(userobj)

    def test_login_with_create_user_with_email(self):
        # Given an external authentication with email attribute
        self.listener.authenticate.return_value = ('userwithemail', {'_email': 'user@example.com'})
        # Given a user doesn't exists in database
        self.assertIsNone(UserObject.get_user('userwithemail'))
        # When login successfully with that user
        login = cherrypy.engine.publish('login', 'userwithemail', 'password')
        self.assertIsNotNone(login)
        userobj = login[0]
        # Then user is created in database
        self.assertIsNotNone(UserObject.get_user('userwithemail'))
        self.assertFalse(userobj.is_admin)
        self.assertEqual(UserObject.USER_ROLE, userobj.role)
        self.assertEqual('', userobj.user_root)
        self.assertEqual('user@example.com', userobj.email)


class LoginWithAddMissingWithDefaults(LoginAbstractTest):
    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=nodomain',
        'ldap-add-missing-user': 'true',
        'ldap-add-user-default-role': 'maintainer',
        'ldap-add-user-default-userroot': '/backups/users/{uid[0]}',
    }

    def setUp(self):
        super().setUp()
        cherrypy.engine.subscribe('authenticate', self.listener.authenticate, priority=50)

    def tearDown(self):
        cherrypy.engine.unsubscribe('authenticate', self.listener.authenticate)
        super().tearDown()

    def test_login_with_create_user(self):
        # Given an external authentication with email attribute
        self.listener.authenticate.return_value = ('tony', {'uid': ['tony']})
        # Given a user doesn't exists in database
        self.assertIsNone(UserObject.get_user('tony'))
        # When login successfully with that user
        login = cherrypy.engine.publish('login', 'tony', 'password')
        self.assertIsNotNone(login)
        userobj = login[0]
        # Then user is create in database
        self.assertIsNotNone(UserObject.get_user('tony'))
        self.assertFalse(userobj.is_admin)
        self.assertEqual(UserObject.MAINTAINER_ROLE, userobj.role)
        self.assertEqual('/backups/users/tony', userobj.user_root)
        # Check listener
        self.listener.user_added.assert_called_once_with(userobj)
        self.listener.user_login.assert_called_once_with(userobj)


class LoginWithAddMissingWithComplexUserroot(LoginAbstractTest):
    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=nodomain',
        'ldap-add-missing-user': 'true',
        'ldap-add-user-default-role': 'maintainer',
        'ldap-add-user-default-userroot': '/home/{sAMAccountName[0]}/backups',
    }

    def setUp(self):
        super().setUp()
        cherrypy.engine.subscribe('authenticate', self.listener.authenticate, priority=50)

    def tearDown(self):
        cherrypy.engine.unsubscribe('authenticate', self.listener.authenticate)
        super().tearDown()

    def test_login_with_create_user(self):
        # Given an external authentication with email attribute
        self.listener.authenticate.return_value = ('tony', {'sAMAccountName': ['tony']})
        # Given a user doesn't exists in database
        self.assertIsNone(UserObject.get_user('tony'))
        # When login successfully with that user
        login = cherrypy.engine.publish('login', 'tony', 'password')
        self.assertIsNotNone(login)
        userobj = login[0]
        # Then user is created in database
        self.assertIsNotNone(UserObject.get_user('tony'))
        self.assertFalse(userobj.is_admin)
        self.assertEqual(UserObject.MAINTAINER_ROLE, userobj.role)
        self.assertEqual('/home/tony/backups', userobj.user_root)
        # Check listener
        self.listener.user_added.assert_called_once_with(userobj)
        self.listener.user_login.assert_called_once_with(userobj)


class LdapLoginAbstractTest(LoginAbstractTest):
    def setUp(self) -> None:
        self.server = ldap3.Server('my_fake_server')
        self.conn = ldap3.Connection(self.server, client_strategy=ldap3.MOCK_SYNC)
        self.patcher = patch('ldap3.Connection', return_value=self.conn)
        self.patcher.start()
        return super().setUp()

    def tearDown(self) -> None:
        self.patcher.stop()
        return super().tearDown()


class LoginWithLdap(LdapLoginAbstractTest):
    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=example,dc=org',
        'ldap-add-missing-user': 'true',
        'ldap-fullname-attribute': 'displayName',
        'ldap-email-attribute': 'email',
    }

    def test_login_valid(self):
        # Given an LDAP server with a user
        self.conn.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'displayName': ['MyUsername'],
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'email': ['myemail@example.com'],
            },
        )
        # When user try to login with valid crendentials
        login = cherrypy.engine.publish('login', 'user01', 'password1')
        # Then user is authenticated
        self.assertTrue(login[0])
        self.listener.user_added.assert_called_once_with(login[0])
        self.listener.user_login.assert_called_once_with(login[0])
        # Then user inherit attribute from LDAP server
        self.assertEqual('MyUsername', login[0].fullname)
        self.assertEqual('myemail@example.com', login[0].email)

    def test_login_invalid(self):
        # Given an LDAP server with a user
        self.conn.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        # When user try to login with invalid crendentials
        login = cherrypy.engine.publish('login', 'user01', 'invalid')
        # Then user is authenticated
        self.assertFalse(login[0])
        self.listener.user_added.assert_not_called()
        self.listener.user_login.assert_not_called()


class LoginWithLdapGroup(LdapLoginAbstractTest):
    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=example,dc=org',
        'ldap-add-missing-user': 'true',
        'ldap-user-filter': '(objectClass=posixAccount)',
        'ldap-group-filter': '(objectClass=posixGroup)',
        'ldap-required-group': 'appgroup',
        'ldap-group-attribute': 'memberUid',
    }

    def test_login_valid(self):
        # Given an LDAP server with a user & group
        self.conn.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        self.conn.strategy.add_entry(
            'cn=appgroup,ou=Groups,dc=example,dc=org',
            {
                'cn': ['appgroup'],
                'memberUid': ['user01'],
                'objectClass': ['posixGroup'],
            },
        )
        # When user try to login with valid crendentials
        login = cherrypy.engine.publish('login', 'user01', 'password1')
        # Then user is authenticated
        self.assertTrue(login[0])
        self.listener.user_added.assert_called_once_with(login[0])
        self.listener.user_login.assert_called_once_with(login[0])

    def test_login_invalid(self):
        # Given an LDAP server with a user
        self.conn.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        # When user try to login with valid crendentials
        login = cherrypy.engine.publish('login', 'user01', 'password1')
        # Then user is authenticated
        self.assertFalse(login[0])
        self.listener.user_added.assert_not_called()
        self.listener.user_login.assert_not_called()
