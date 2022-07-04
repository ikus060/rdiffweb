# -*- coding: utf-8 -*-
# LDAP Plugins for cherrypy
# # Copyright (C) 2022 IKUS Software
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
Created on Oct 17, 2015

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""
import os
from unittest import mock, skipUnless

import cherrypy
import ldap3
from cherrypy.test import helper

from .. import ldap  # noqa


class LdapPluginTest(helper.CPWebCase):
    def setUp(self) -> None:
        self.server = ldap3.Server('my_fake_server')
        self.conn = ldap3.Connection(self.server, client_strategy=ldap3.MOCK_SYNC)
        self.patcher = mock.patch('ldap3.Connection', return_value=self.conn)
        self.patcher.start()
        return super().setUp()

    def tearDown(self) -> None:
        self.patcher.stop()
        return super().tearDown()

    @classmethod
    def setup_server(cls):
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

    def test_authenticate(self):
        # Given a user in LDAP
        self.conn.strategy.add_entry(
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
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'cn': ['user01'],
                '_email': None,
                '_fullname': None,
            },
            authenticated[1],
        )

    def test_authenticate_with_invalid_user(self):
        # Given a user in LDAP
        self.conn.strategy.add_entry(
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
        self.conn.strategy.add_entry(
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

    def test_authenticate_with_email(self):
        # Given a user in LDAP with firstname and lastname
        self.conn.strategy.add_entry(
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
                'cn': ['user01'],
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'mail': ['john@test.com'],
                '_email': 'john@test.com',
                '_fullname': None,
            },
            authenticated[1],
        )

    def test_authenticate_with_fullname(self):
        # Given a user in LDAP with firstname and lastname
        self.conn.strategy.add_entry(
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
                'cn': ['user01'],
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'displayName': ['John Kennedy'],
                '_email': None,
                '_fullname': 'John Kennedy',
            },
            authenticated[1],
        )

    def test_authenticate_with_firstname_lastname(self):
        # Given a user in LDAP with firstname and lastname
        self.conn.strategy.add_entry(
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
                'cn': ['user01'],
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'givenName': ['John'],
                'sn': ['Kennedy'],
                '_email': None,
                '_fullname': 'John Kennedy',
            },
            authenticated[1],
        )


class LdapPluginTestWithRequiredGroup(helper.CPWebCase):
    def setUp(self) -> None:
        self.server = ldap3.Server('my_fake_server')
        self.conn = ldap3.Connection(self.server, client_strategy=ldap3.MOCK_SYNC)
        self.patcher = mock.patch('ldap3.Connection', return_value=self.conn)
        self.patcher.start()
        return super().setUp()

    def tearDown(self) -> None:
        self.patcher.stop()
        return super().tearDown()

    @classmethod
    def setup_server(cls):
        cherrypy.config.update(
            {
                'ldap.uri': 'my_fake_server',
                'ldap.base_dn': 'dc=example,dc=org',
                'ldap.required_group': 'cn=appgroup,ou=Groups,dc=nodomain',
                'ldap.group_attribute': 'memberUid',
                'ldap.group_attribute_is_dn': False,
            }
        )

    def test_authenticate_with_valid_group(self):
        # Given a user and a group in LDAP
        self.conn.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        self.conn.strategy.add_entry(
            'cn=appgroup,ou=Groups,dc=nodomain', {'memberUid': ['user01', 'user02'], 'objectClass': ['posixGroup']}
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is authenticated
        self.assertTrue(authenticated)
        self.assertEqual(authenticated[0], 'user01')
        self.assertEqual(
            {
                'userPassword': ['password1'],
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
                'cn': ['user01'],
                '_email': None,
                '_fullname': None,
            },
            authenticated[1],
        )

    def test_authenticate_with_not_member(self):
        # Given a user and a group in LDAP
        self.conn.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        self.conn.strategy.add_entry(
            'cn=appgroup,ou=Groups,dc=nodomain', {'memberUid': ['invalid', 'user02'], 'objectClass': ['posixGroup']}
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is not authenticated
        self.assertEqual(False, authenticated)

    def test_authenticate_with_invalid_group(self):
        # Given a user and a group in LDAP
        self.conn.strategy.add_entry(
            'cn=user01,dc=example,dc=org',
            {
                'userPassword': 'password1',
                'uid': ['user01'],
                'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'],
            },
        )
        self.conn.strategy.add_entry(
            'cn=invalid,ou=Groups,dc=nodomain', {'memberUid': ['user01', 'user02'], 'objectClass': ['posixGroup']}
        )
        # When authenticating with that user
        authenticated = cherrypy.ldap.authenticate('user01', 'password1')
        # Then user is not authenticated
        self.assertEqual(False, authenticated)


class LdapPluginTestWithUnavailableServer(helper.CPWebCase):
    @classmethod
    def setup_server(cls):
        cherrypy.config.update(
            {
                'ldap.uri': '127.0.0.1:34578',
                'ldap.base_dn': 'dc=example,dc=org',
            }
        )

    def test_authenticate_with_unavailable_server(self):
        user = cherrypy.ldap.authenticate('user01', 'password1')
        self.assertIsNone(user)


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

    def test_authenticate(self):
        user = cherrypy.ldap.authenticate('user01', 'password1')
        self.assertTrue(user)
        self.assertEqual(user[0], 'user01')

    def test_authenticate_with_invalid_user(self):
        self.assertEqual(False, cherrypy.ldap.authenticate('josh', 'password'))
