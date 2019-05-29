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

import unittest

from rdiffweb.core import InvalidUserError, RdiffError
from rdiffweb.test import AppTestCase


class SQLiteUserDBTest(AppTestCase):

    """Unit tests for the sqliteUserDBTeste class"""

    def setUp(self):
        AppTestCase.setUp(self)
        # Get reference to SQLite database
        self.db = self.app.userdb._database

    def test_add_user(self):
        """Add user to database."""
        self.db.add_user('joe')
        self.assertTrue(self.db.exists('joe'))

    def test_are_valid_credentials(self):
        self.db.add_user('mike')
        self.db.set_password('mike', 'password')
        self.assertEquals('mike', self.db.are_valid_credentials('mike', 'password'))

    def test_are_valid_credentials_with_invalid_password(self):
        self.db.add_user('jeff')
        self.assertFalse(self.db.are_valid_credentials('jeff', 'invalid'))
        # password is case sensitive
        self.assertFalse(self.db.are_valid_credentials('jeff', 'Password'))
        # Match entire password
        self.assertFalse(self.db.are_valid_credentials('jeff', 'pass'))
        self.assertFalse(self.db.are_valid_credentials('jeff', ''))

    def test_are_valid_credentials_with_invalid_user(self):
        self.assertFalse(self.db.are_valid_credentials('josh', 'password'))

    def test_delete_user(self):
        # Create user
        self.db.add_user('vicky')
        self.assertTrue(self.db.exists('vicky'))
        # Delete user
        self.assertTrue(self.db.delete_user('vicky'))
        self.assertFalse(self.db.exists('vicky'))

    def test_delete_user_with_invalid_user(self):
        self.assertFalse(self.db.delete_user('eve'))

    def test_exists(self):
        self.db.add_user('bob')
        self.assertTrue(self.db.exists('bob'))

    def test_exists_with_invalid_user(self):
        self.assertFalse(self.db.exists('invalid'))

    def test_get_set(self):
        user = 'larry'
        self.db.add_user(user)

        email = self.db.get_email(user)
        repos = self.db.get_repos(user)
        user_root = self.db.get_user_root(user)
        is_admin = self.db.is_admin(user)
        self.assertEqual('', email)
        self.assertEqual([], repos)
        self.assertEqual('', user_root)
        self.assertEqual(False, is_admin)

        self.db.set_user_root(user, '/backups/')
        self.db.set_is_admin(user, True)
        self.db.set_email(user, 'larry@gmail.com')
        self.db.set_repos(user, ['/backups/computer/', '/backups/laptop/'])

        email = self.db.get_email(user)
        repos = self.db.get_repos(user)
        user_root = self.db.get_user_root(user)
        self.assertEqual('larry@gmail.com', email)
        self.assertEqual(['/backups/computer/', '/backups/laptop/'], repos)
        self.assertEqual('/backups/', user_root)

    def test_get_invalid_user(self):
        with self.assertRaises(InvalidUserError):
            self.db.get_email('invalid')
        with self.assertRaises(InvalidUserError):
            self.db.get_repos('invalid')
        with self.assertRaises(InvalidUserError):
            self.db.get_user_root('invalid')

    def test_list(self):
        self.app.userdb.add_user('annik')
        users = list(self.app.userdb.list())
        self.assertEqual(1, len(users))
        self.assertEqual('annik', users[0].username)

    def test_set_invalid_user(self):
        with self.assertRaises(InvalidUserError):
            self.db.set_user_root('invalid', '/backups/')
        with self.assertRaises(InvalidUserError):
            self.db.set_is_admin('invalid', True)
        with self.assertRaises(InvalidUserError):
            self.db.set_email('invalid', 'larry@gmail.com')
        with self.assertRaises(InvalidUserError):
            self.db.set_repos('invalid', ['/backups/computer/', '/backups/laptop/'])

    def test_set_password_update(self):
        self.db.add_user('annik')
        self.assertFalse(self.db.set_password('annik', 'new_password'))
        # Check new credentials
        self.assertEqual('annik', self.db.are_valid_credentials('annik', 'new_password'))

    def test_set_password_with_old_password(self):
        self.db.add_user('john')
        self.db.set_password('john', 'password')
        self.db.set_password('john', 'new_password', old_password='password')
        # Check new credentials
        self.assertEqual('john', self.db.are_valid_credentials('john', 'new_password'))

    def test_set_password_with_invalid_old_password(self):
        self.db.add_user('foo')
        with self.assertRaises(RdiffError):
            self.db.set_password('foo', 'new_password', old_password='invalid')

    def test_set_password_update_not_exists(self):
        """Expect error when trying to update password of invalid user."""
        with self.assertRaises(InvalidUserError):
            self.assertFalse(self.db.set_password('bar', 'new_password'))

    def test_set_repos_empty(self):
        self.db.add_user('kim')
        self.db.set_repos("kim", [])
        self.assertEquals([], self.db.get_repos('kim'))

    def test_set_authorizedkeys(self):
        self.db.add_user('kim')
        value = "This should be a very long clob with sshkeys"
        self.db.set_authorizedkeys("kim", value)
        self.assertEquals(value, self.db.get_authorizedkeys('kim'))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
