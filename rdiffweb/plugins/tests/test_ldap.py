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
import cherrypy
from cherrypy.test import helper
from mockldap import MockLdap

from .. import ldap  # noqa


def _ldap_user(name, password='password'):
    assert isinstance(name, str)
    assert isinstance(password, str)
    return ('uid=%s,ou=People,dc=nodomain' % (name), {
        'uid': [name],
        'cn': [name],
        'sAMAccountName': [name.encode(encoding='utf-8')],
        'userPassword': [password],
        'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount']})


class LdapPluginTest(helper.CPWebCase):

    basedn = ('dc=nodomain', {
        'dc': ['nodomain'],
        'o': ['nodomain']})
    people = ('ou=People,dc=nodomain', {
        'ou': ['People'],
        'objectClass': ['organizationalUnit']})
    groups = ('ou=Groups,dc=nodomain', {
        'ou': ['Groups'],
        'objectClass': ['organizationalUnit']})

    # This is the content of our mock LDAP directory. It takes the form
    # {dn: {attr: [value, ...], ...}, ...}.
    ldap_directory = dict([
        basedn,
        people,
        groups,
        _ldap_user('admin'),
        _ldap_user('annik'),
        _ldap_user('bob'),
        _ldap_user('foo'),
        _ldap_user('jeff'),
        _ldap_user('john'),
        _ldap_user('larry'),
        _ldap_user('mike'),
        _ldap_user('vicky'),
    ])

    @classmethod
    def setup_server(cls):
        cherrypy.config.update({
            'ldap.uri': '__default__',
            'ldap.base_dn': 'dc=nodomain',
        })

    def setUp(self):
        super().setUp()
        self.mockldap = MockLdap(self.ldap_directory)
        self.mockldap.start()

    def tearDown(self):
        self.mockldap.stop()
        return super().tearDown()

    def test_authenticate(self):
        user = cherrypy.ldap.authenticate('mike', 'password')
        self.assertTrue(user)
        self.assertEqual(user.username, 'mike')
        self.assertEqual(user.attrs, {'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'], 'userPassword': [
            'password'], 'uid': ['mike'], 'cn': ['mike'], 'sAMAccountName': ['mike']})

    def test_authenticate_with_invalid_password(self):
        self.assertFalse(
            cherrypy.ldap.authenticate('jeff', 'invalid'))
        # password is case sensitive
        self.assertFalse(
            cherrypy.ldap.authenticate('jeff', 'Password'))
        # Match entire password
        self.assertFalse(cherrypy.ldap.authenticate('jeff', 'pass'))
        self.assertFalse(cherrypy.ldap.authenticate('jeff', ''))

    def test_authenticate_with_invalid_user(self):
        self.assertIsNone(
            cherrypy.ldap.authenticate('josh', 'password'))


class LdapPluginWithRequiredGroupTest(helper.CPWebCase):
    """
    Test for required group for LDAP with posix schema.
    """

    basedn = ('dc=nodomain', {
        'dc': ['nodomain'],
        'o': ['nodomain']})
    people = ('ou=People,dc=nodomain', {
        'ou': ['People'],
        'objectClass': ['organizationalUnit']})
    groups = ('ou=Groups,dc=nodomain', {
        'ou': ['Groups'],
        'objectClass': ['organizationalUnit']})
    rdiffweb_group = ('cn=rdiffweb,ou=Groups,dc=nodomain', {
        'memberUid': ['jeff', 'mike'],
        'objectClass': ['posixGroup']})

    # This is the content of our mock LDAP directory. It takes the form
    # {dn: {attr: [value, ...], ...}, ...}.
    ldap_directory = dict([
        basedn,
        people,
        groups,
        rdiffweb_group,
        _ldap_user('jeff'),
        _ldap_user('mike'),
        _ldap_user('bob'),
    ])

    @classmethod
    def setup_server(cls):
        cherrypy.config.update({
            'ldap.uri': '__default__',
            'ldap.base_dn': 'dc=nodomain',
            'ldap.required_group': 'cn=rdiffweb,ou=Groups,dc=nodomain',
            'ldap.group_attribute': 'memberUid',
            'ldap.group_attribute_is_dn': False,
        })

    def setUp(self):
        super().setUp()
        self.mockldap = MockLdap(self.ldap_directory)
        self.mockldap.start()

    def tearDown(self):
        self.mockldap.stop()
        return super().tearDown()

    def test_authenticate(self):
        username, attrs = cherrypy.ldap.authenticate(
            'mike', 'password')
        self.assertEqual('mike', username)
        username, attrs = cherrypy.ldap.authenticate(
            'jeff', 'password')
        self.assertEqual('jeff', username)

    def test_authenticate_with_invalid_password(self):
        self.assertFalse(
            cherrypy.ldap.authenticate('jeff', 'invalid'))
        # password is case sensitive
        self.assertFalse(
            cherrypy.ldap.authenticate('jeff', 'Password'))
        # Match entire password
        self.assertFalse(cherrypy.ldap.authenticate('jeff', 'pass'))
        self.assertFalse(cherrypy.ldap.authenticate('jeff', ''))

    def test_authenticate_with_invalid_user(self):
        self.assertIsNone(
            cherrypy.ldap.authenticate('josh', 'password'))

    def test_authenticate_missing_group(self):
        self.assertFalse(
            cherrypy.ldap.authenticate('bob', 'password'))
