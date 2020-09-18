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

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""


import unittest

from rdiffweb.core import RdiffError
from rdiffweb.test import AppTestCase


class SQLiteBackendTest(AppTestCase):

    """Unit tests for the sqliteUserDBTeste class"""

    def setUp(self):
        AppTestCase.setUp(self)
        # Get reference to SQLite database
        self.db = self.app.store._database

    def test_delete_user(self):
        # Create user
        self.db.insert('users', username='vicky')
        self.assertIsNotNone(self.db.findone('users', username='vicky'))
        # Delete user
        self.db.delete('users', username='vicky')
        self.assertIsNone(self.db.findone('users', username='vicky'))

    def test_delete_user_with_invalid_user(self):
        self.assertFalse(self.db.delete('users', username='eve'))

    def test_findone_with_valid_user(self):
        self.db.insert('users', username='bob')
        self.assertIsNotNone(self.db.findone('users', username='bob'))

    def test_findone_with_invalid_user(self):
        self.assertIsNone(self.db.findone('users', username='invalid'))

    def test_find_users(self):
        self.app.store.add_user('annik')
        records = list(self.db.find('users'))
        self.assertEqual(1, len(records))
        self.assertEqual({'isadmin': 0,
            'password': '',
            'restoreformat': 1,
            'role': 10,
            'useremail': '',
            'userid': 2,
            'username': 'annik',
            'userroot': ''}, records[0])

    def test_search_with_users(self):
        self.app.store.add_user('annik')
        self.app.store.add_user('kim')
        self.app.store.add_user('john')
        # Search
        users = list(self.db.search('users', 'k', 'username'))
        self.assertEqual(2, len(users))

    def test_search_with_repos(self):
        annik = self.app.store.add_user('annik')
        annik.add_repo('coucou1')
        annik.add_repo('repo1')
        kim = self.app.store.add_user('kim')
        kim.add_repo('coucou2')
        kim.add_repo('repo2')
        
        # Search in repo name
        repos = list(self.db.search('repos', 'cou', 'repopath'))
        self.assertEqual(2, len(repos))
        
        # Search in username
        repos = list(self.db.search('repos', 'annik', 'username'))
        self.assertEqual(2, len(repos))

    def test_insert(self):
        self.db.insert('users', username='kim')
        userid = self.db.findone('users', username='kim')['userid']
        self.db.insert(
            'sshkeys',
            userid=userid,
            fingerprint="12345678",
            key="This should be a very long clob with sshkeys")
        
        data = self.db.findone('sshkeys',
            userid=userid,
            fingerprint="12345678")
        
        self.assertEquals("This should be a very long clob with sshkeys", data.get('key'))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
