# LDAP Plugins for cherrypy
# Copyright (C) 2025 IKUS Software
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
"""
Created on Oct 17, 2015

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""
import os
from unittest import mock, skipUnless

import cherrypy
import ldap3
from cherrypy.test import helper

from .. import ldap  # noqa

original_connection = ldap3.Connection


def mock_ldap_connection(*args, **kwargs):
    kwargs.pop('client_strategy', None)
    return original_connection(*args, client_strategy=ldap3.MOCK_ASYNC, **kwargs)


class LdapPluginTest(helper.CPWebCase):

    @classmethod
    def setup_server(cls):
        # Configure Mock server early.
        cls.server = ldap3.Server('my_fake_server')
        cls.patcher = mock.patch('ldap3.Connection', side_effect=mock_ldap_connection)
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

    @classmethod
    def teardown_class(cls):
        cherrypy.ldap.uri = None
        # Release mock server.
        cls.patcher.stop()
        return super().teardown_class()

    def setUp(self) -> None:
        # Clear LDAP entries before test.
        for entry in list(cherrypy.ldap._pool.strategy.connection.server.dit):
            if entry == 'cn=schema':
                continue
            cherrypy.ldap._pool.strategy.remove_entry(entry)
        return super().setUp()

    def test_authenticate(self):
        # Given a user in LDAP
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is authenticated
        self.assertTrue(authenticated)
        self.assertEqual(authenticated[0], 'user01')
        self.assertEqual(
            {
                'dn': 'cn=user01,dc=example,dc=org',
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'cn': ['user01'],
                'email': None,
                'fullname': '',
            },
            authenticated[1],
        )

    def test_authenticate_with_wildcard(self):
        # Given a user in LDAP
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        # When authenticating with a username containing wildcard
        authenticated = cherrypy.ldap.authenticate('user*', 'password1')
        # Then user is NOT authenticated
        self.assertFalse(authenticated)

    def test_authenticate_with_invalid_user(self):
        # Given a user in LDAP
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        # When authenticating with an invalid user
        authenticated = cherrypy.ldap.authenticate('invalid', 'password1')
        # Then user is authenticated
        self.assertEqual(False, authenticated)

    def test_authenticate_with_invalid_password(self):
        # Given a user in LDAP
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        # When authenticating with an invalid user
        authenticated = cherrypy.ldap.authenticate('user01', 'invalid')
        # Then user is not authenticated
        self.assertEqual(False, authenticated)
        # When authenticating with an valid password
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is not authenticated
        self.assertTrue(authenticated)

    def test_authenticate_with_email(self):
        # Given a user in LDAP with firstname and lastname
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'cn': ['user01'],
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'mail': ['john@test.com'],
            },
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is authenticated and firstname is composed of firstname and lastname
        self.assertTrue(authenticated)
        self.assertEqual(authenticated[0], 'user01')
        self.assertEqual(
            {
                'dn': 'cn=user01,dc=example,dc=org',
                'cn': ['user01'],
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'mail': ['john@test.com'],
                'email': 'john@test.com',
                'fullname': '',
            },
            authenticated[1],
        )

    def test_authenticate_with_fullname(self):
        # Given a user in LDAP with firstname and lastname
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'cn': ['user01'],
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'displayName': ['John Kennedy'],
            },
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is authenticated and firstname is composed of firstname and lastname
        self.assertTrue(authenticated)
        self.assertEqual(authenticated[0], 'user01')
        self.assertEqual(
            {
                'dn': 'cn=user01,dc=example,dc=org',
                'cn': ['user01'],
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'displayName': ['John Kennedy'],
                'email': None,
                'fullname': 'John Kennedy',
            },
            authenticated[1],
        )

    def test_authenticate_with_firstname_lastname(self):
        # Given a user in LDAP with firstname and lastname
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'cn': ['user01'],
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'givenName': ['John'],
                'sn': ['Kennedy'],
            },
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is authenticated and firstname is composed of firstname and lastname
        self.assertTrue(authenticated)
        self.assertEqual(authenticated[0], 'user01')
        self.assertEqual(
            {
                'dn': 'cn=user01,dc=example,dc=org',
                'cn': ['user01'],
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'givenName': ['John'],
                'sn': ['Kennedy'],
                'email': None,
                'fullname': 'John Kennedy',
            },
            authenticated[1],
        )


class LdapPluginTestWithRequiredGroup(helper.CPWebCase):

    @classmethod
    def setup_server(cls):
        # Configure Mock server early.
        cls.server = ldap3.Server('my_fake_server')
        cls.conn = ldap3.Connection(cls.server, client_strategy=ldap3.MOCK_ASYNC, raise_exceptions=True)
        cls.patcher = mock.patch('ldap3.Connection', return_value=cls.conn)
        cls.patcher.start()
        cherrypy.config.update(
            {
                'ldap.uri': 'my_fake_server',
                'ldap.base_dn': 'dc=example,dc=org',
                'ldap.required_group': ['appgroup', 'secondgroup'],
                'ldap.group_attribute': 'memberUid',
                'ldap.group_attribute_is_dn': False,
            }
        )

    @classmethod
    def teardown_class(cls):
        cherrypy.ldap.uri = None
        # Release mock server.
        cls.patcher.stop()
        return super().teardown_class()

    def setUp(self) -> None:
        # Clear LDAP entries before test.
        for entry in list(cherrypy.ldap._pool.strategy.connection.server.dit):
            if entry == 'cn=schema':
                continue
            cherrypy.ldap._pool.strategy.remove_entry(entry)
        return super().setUp()

    def test_authenticate_with_valid_group(self):
        # Given a user and a group in LDAP
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=appgroup,ou=Groups,dc=example,dc=org',
            {
                'cn': ['appgroup'],
                'memberUid': ['user01', 'user02'],
                'objectClass': ['posixGroup'],
            },
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is authenticated
        self.assertTrue(authenticated)
        self.assertEqual(authenticated[0], 'user01')
        self.assertEqual(
            {
                'dn': 'cn=user01,dc=example,dc=org',
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'cn': ['user01'],
                'email': None,
                'fullname': '',
            },
            authenticated[1],
        )

    def test_authenticate_with_not_member(self):
        # Given a user and a group in LDAP
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=appgroup,ou=Groups,dc=nodomain', {'memberUid': ['invalid', 'user02'], 'objectClass': ['posixGroup']}
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is not authenticated
        self.assertEqual(False, authenticated)

    def test_authenticate_with_invalid_group(self):
        # Given a user and a group in LDAP
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        cherrypy.ldap._pool.strategy.add_entry(
            'cn=invalid,ou=Groups,dc=nodomain', {'memberUid': ['user01', 'user02'], 'objectClass': ['posixGroup']}
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is not authenticated
        self.assertEqual(False, authenticated)


@skipUnless(os.environ.get('TEST_LDAP_URI', None), "required TEST_LDAP_URI pointing to openldap server")
class LdapPluginTestWithOpenldap(helper.CPWebCase):
    """
    This test required a real openldap serer running with 'user01' and 'password1'.
    """

    @classmethod
    def setup_server(cls):
        cherrypy.config.update(
            {
                'ldap.uri': os.environ.get('TEST_LDAP_URI'),
                'ldap.base_dn': os.environ.get('TEST_LDAP_BASE_DN', 'dc=example,dc=org'),
            }
        )

    @classmethod
    def teardown_class(cls):
        cherrypy.ldap.uri = None
        return super().teardown_class()

    def test_authenticate(self):
        user = cherrypy.ldap.authenticate('user01', 'password1')
        self.assertTrue(user)
        self.assertEqual(user[0], 'user01')

    def test_authenticate_with_invalid_user(self):
        self.assertEqual(False, cherrypy.ldap.authenticate('josh', 'password'))
