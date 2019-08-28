#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 Patrik Dufresne Service Logiciel
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

@author: Patrik Dufresne <info@patrikdufresne.com>
"""

from __future__ import unicode_literals

import logging
from rdiffweb.test import AppTestCase
import unittest

from builtins import str
from mockldap import MockLdap

from rdiffweb.core import RdiffError
from rdiffweb.core.user_ldap_auth import LdapPasswordStore


def _ldap_user(name, password='password'):
    assert isinstance(name, str)
    assert isinstance(password, str)
    return ('uid=%s,ou=People,dc=nodomain' % (name), {
        'uid': [name],
        'cn': [name],
        'userPassword': [password],
        'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount']})


class UserManagerLdapTest(AppTestCase):

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
    directory = dict([
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

    default_config = {
        'LdapUri': '__default__',
        'LdapBaseDn': 'dc=nodomain',
        'LdapAllowPasswordChange': 'true',
    }

    @classmethod
    def setUpClass(cls):
        # We only need to create the MockLdap instance once. The content we
        # pass in will be used for all LDAP connections.
        cls.mockldap = MockLdap(cls.directory)

    @classmethod
    def tearDownClass(cls):
        del cls.mockldap

    def setUp(self):
        AppTestCase.setUp(self)
        # Mock LDAP
        self.mockldap.start()
        self.ldapobj = self.mockldap['ldap://localhost/']
        # Get reference to LdapStore
        self.ldapstore = self.app.userdb._password_stores[0]
        self.assertTrue(isinstance(self.ldapstore, LdapPasswordStore))

    def tearDown(self):
        # Stop patching ldap.initialize and reset state.
        self.mockldap.stop()
        del self.ldapobj
        AppTestCase.tearDown(self)

    def test_are_valid_credentials(self):
        
        username, attrs = self.ldapstore.are_valid_credentials('mike', 'password')
        self.assertEquals('mike', username)
        self.assertEquals(attrs, {'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount'], 'userPassword': ['password'], 'uid': ['mike'], 'cn': ['mike']})

    def test_are_valid_credentials_with_invalid_password(self):
        self.assertFalse(self.ldapstore.are_valid_credentials('jeff', 'invalid'))
        # password is case sensitive
        self.assertFalse(self.ldapstore.are_valid_credentials('jeff', 'Password'))
        # Match entire password
        self.assertFalse(self.ldapstore.are_valid_credentials('jeff', 'pass'))
        self.assertFalse(self.ldapstore.are_valid_credentials('jeff', ''))

    def test_are_valid_credentials_with_invalid_user(self):
        self.assertIsNone(self.ldapstore.are_valid_credentials('josh', 'password'))

    def test_delete_user(self):
        # Delete_user is not supported by LdapPlugin.
        with self.assertRaises(AttributeError):
            self.ldapstore.delete_user('vicky')

    def test_delete_user_with_invalid_user(self):
        with self.assertRaises(AttributeError):
            self.ldapstore.delete_user('eve')

    def test_set_password_not_found(self):
        with self.assertRaises(RdiffError):
            self.assertTrue(self.ldapstore.set_password('joe', 'password'))

    def test_set_password_update(self):
        self.assertFalse(self.ldapstore.set_password('annik', 'new_password'))

    def test_set_password_with_old_password(self):
        self.assertFalse(self.ldapstore.set_password('john', 'new_password', old_password='password'))

    def test_set_password_with_invalid_old_password(self):
        with self.assertRaises(RdiffError):
            self.ldapstore.set_password('foo', 'new_password', old_password='invalid')

    def test_set_password_update_not_exists(self):
        """Expect error when trying to update password of invalid user."""
        with self.assertRaises(RdiffError):
            self.assertFalse(self.ldapstore.set_password('bar', 'new_password'))


class UserManagerLdapNoPasswordChangeTest(AppTestCase):

    basedn = ('dc=nodomain', {
        'dc': ['nodomain'],
        'o': ['nodomain']})
    people = ('ou=People,dc=nodomain', {
        'ou': ['People'],
        'objectClass': ['organizationalUnit']})

    # This is the content of our mock LDAP directory. It takes the form
    # {dn: {attr: [value, ...], ...}, ...}.
    directory = dict([
        basedn,
        people,
        _ldap_user('annik'),
        _ldap_user('bob'),
        _ldap_user('john'),
    ])

    default_config = {
        'LdapUri': '__default__',
        'LdapBaseDn': 'dc=nodomain',
        'LdapAllowPasswordChange': 'false'
    }

    @classmethod
    def setUpClass(cls):
        # We only need to create the MockLdap instance once. The content we
        # pass in will be used for all LDAP connections.
        cls.mockldap = MockLdap(cls.directory)

    @classmethod
    def tearDownClass(cls):
        del cls.mockldap

    def setUp(self):
        AppTestCase.setUp(self)
        # Mock LDAP
        self.mockldap.start()
        self.ldapobj = self.mockldap['ldap://localhost/']
        # Get reference to LdapStore
        self.ldapstore = self.app.userdb._password_stores[0]

    def tearDown(self):
        # Stop patching ldap.initialize and reset state.
        self.mockldap.stop()
        del self.ldapobj
        AppTestCase.tearDown(self)

    def test_set_password_update(self):
        with self.assertRaises(RdiffError):
            self.ldapstore.set_password('annik', 'new_password')

    def test_set_password_with_old_password(self):
        with self.assertRaises(RdiffError):
            self.ldapstore.set_password('john', 'new_password', old_password='password')

    def test_set_password_with_invalid_old_password(self):
        with self.assertRaises(RdiffError):
            self.ldapstore.set_password('foo', 'new_password', old_password='invalid')

    def test_set_password_update_not_exists(self):
        """Expect error when trying to update password of invalid user."""
        with self.assertRaises(RdiffError):
            self.assertFalse(self.ldapstore.set_password('bar', 'new_password'))


class UserManagerLdapWithRequiredGroupTest(AppTestCase):
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
    directory = dict([
        basedn,
        people,
        groups,
        rdiffweb_group,
        _ldap_user('jeff'),
        _ldap_user('mike'),
        _ldap_user('bob'),
    ])

    default_config = {
        'LdapUri': '__default__',
        'LdapBaseDn': 'dc=nodomain',
        'LdapAllowPasswordChange': 'true',
        'LdapRequiredGroup': 'cn=rdiffweb,ou=Groups,dc=nodomain',
        'LDAPGroupAttribute': 'memberUid',
        'LDAPGroupAttributeIsDN': 'false',
    }

    @classmethod
    def setUpClass(cls):
        # We only need to create the MockLdap instance once. The content we
        # pass in will be used for all LDAP connections.
        cls.mockldap = MockLdap(cls.directory)

    @classmethod
    def tearDownClass(cls):
        del cls.mockldap

    def setUp(self):
        AppTestCase.setUp(self)
        # Mock LDAP
        self.mockldap.start()
        self.ldapobj = self.mockldap['ldap://localhost/']
        # Get reference to LdapStore
        self.ldapstore = self.app.userdb._password_stores[0]
        self.assertTrue(isinstance(self.ldapstore, LdapPasswordStore))

    def tearDown(self):
        # Stop patching ldap.initialize and reset state.
        self.mockldap.stop()
        del self.ldapobj
        AppTestCase.tearDown(self)

    def test_are_valid_credentials(self):
        username, attrs = self.ldapstore.are_valid_credentials('mike', 'password')
        self.assertEquals('mike', username)
        username, attrs = self.ldapstore.are_valid_credentials('jeff', 'password')
        self.assertEquals('jeff', username)

    def test_are_valid_credentials_with_invalid_password(self):
        self.assertFalse(self.ldapstore.are_valid_credentials('jeff', 'invalid'))
        # password is case sensitive
        self.assertFalse(self.ldapstore.are_valid_credentials('jeff', 'Password'))
        # Match entire password
        self.assertFalse(self.ldapstore.are_valid_credentials('jeff', 'pass'))
        self.assertFalse(self.ldapstore.are_valid_credentials('jeff', ''))

    def test_are_valid_credentials_with_invalid_user(self):
        self.assertIsNone(self.ldapstore.are_valid_credentials('josh', 'password'))

    def test_are_valid_credentials_missing_group(self):
        self.assertFalse(self.ldapstore.are_valid_credentials('bob', 'password'))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
