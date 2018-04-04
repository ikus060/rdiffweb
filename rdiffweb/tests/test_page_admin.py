#!/usr/bin/env python
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
Created on Dec 30, 2015

@author: Patrik Dufresne
"""

from __future__ import print_function
from __future__ import unicode_literals

import logging
import unittest

from rdiffweb.test import WebCase


class AbstractAdminTest(WebCase):
    """Class to regroup command method to test admin page."""

    def _add_user(self, username=None, email=None, password=None, user_root=None, is_admin=None):
        b = {}
        b['action'] = 'add'
        if username is not None:
            b['username'] = username
        if email is not None:
            b['email'] = email
        if password is not None:
            b['password'] = password
        if user_root is not None:
            b['user_root'] = user_root
        if is_admin is not None:
            b['is_admin'] = str(bool(is_admin)).lower()
        self.getPage("/admin/users/", method='POST', body=b)

    def _edit_user(self, username=None, email=None, password=None, user_root=None, is_admin=None):
        b = {}
        b['action'] = 'edit'
        if username is not None:
            b['username'] = username
        if email is not None:
            b['email'] = email
        if password is not None:
            b['password'] = password
        if user_root is not None:
            b['user_root'] = user_root
        if is_admin is not None:
            b['is_admin'] = str(bool(is_admin)).lower()
        self.getPage("/admin/users/", method='POST', body=b)

    def _delete_user(self, username='test1'):
        b = {'action': 'delete',
             'username': username}
        self.getPage("/admin/users/", method='POST', body=b)


class AdminUsersAsAdminTest(AbstractAdminTest):
    """Integration test for page_admin"""

    login = True

    def test_add_edit_delete(self):
        #  Add user to be listed
        self._add_user("test2", "test2@test.com", "test2", "/var/backups/", False)
        try:
            self.assertInBody("User added successfully.")
            self.assertInBody("test2")
            self.assertInBody("test2@test.com")
            #  Update user
            self._edit_user("test2", "chaned@test.com", "new-password", "/tmp/", True)
            self.assertInBody("User information modified successfully.")
            self.assertInBody("test2")
            self.assertInBody("chaned@test.com")
            self.assertNotInBody("/var/backups/")
            self.assertInBody("/tmp/")
            #  Check with filters
            self.getPage("/admin/users/?userfilter=admins")
            self.assertInBody("test2")
        finally:
            self._delete_user("test2")
            self.assertInBody("User account removed.")
            self.assertNotInBody("test2")

    def test_add_edit_delete_user_with_encoding(self):
        """
        Check creation of user with non-ascii char.
        """
        self._add_user("Éric", "éric@test.com", "Éric", "/var/backups/", False)
        try:
            self.assertInBody("User added successfully.")
            self.assertInBody("Éric")
            self.assertInBody("éric@test.com")
            # Update user
            self._edit_user("Éric", "eric.létourno@test.com", "écureuil", "/tmp/", True)
            self.assertInBody("User information modified successfully.")
            self.assertInBody("Éric")
            self.assertInBody("eric.létourno@test.com")
            self.assertNotInBody("/var/backups/")
            self.assertInBody("/tmp/")
            # Check with filter
            self.getPage("/admin/users/?userfilter=admins")
            self.assertInBody("Éric")
        finally:
            self._delete_user("Éric")
        self.assertInBody("User account removed.")
        self.assertNotInBody("Éric")

    def test_add_user_with_empty_username(self):
        """
        Verify failure trying to create user without username.
        """
        self._add_user("", "test1@test.com", "test1", "/var/backups/", False)
        self.assertInBody("The username is invalid.")

    def test_add_user_with_existing_username(self):
        """
        Verify failure trying to add the same user.
        """
        self._add_user("test1", "test1@test.com", "test1", "/var/backups/", False)
        self._add_user("test1", "test1@test.com", "test1", "/var/backups/", False)
        self.assertInBody("User test1 already exists.")

    def test_add_user_with_invalid_root_directory(self):
        """
        Verify failure to add a user with invalid root directory.
        """
        try:
            self._delete_user("test5")
        except:
            pass
        self._add_user("test5", "test1@test.com", "test5", "/var/invalid/", False)
        self.assertNotInBody("User added successfully.")
        self.assertInBody("User root directory /var/invalid/ is not accessible!")

    def test_delete_user_with_not_existing_username(self):
        """
        Verify failure to delete invalid username.
        """
        self._delete_user("test3")
        self.assertInBody("User test3 doesn&#39;t exists.")

    def test_delete_our_self(self):
        """
        Verify failure to delete our self.
        """
        self._delete_user(self.USERNAME)
        self.assertInBody("You cannot remove your own account!")

    def test_edit_user_with_invalid_path(self):
        """
        Verify failure trying to update user with invalid path.
        """
        self._edit_user("test1", "test1@test.com", "test", "/var/invalid/", False)
        self.assertNotInBody("User added successfully.")
        self.assertInBody("User root directory /var/invalid/ is not accessible!")

    def test_list(self):
        self.getPage("/admin/users/")
        self.assertInBody("Users")
        self.assertInBody("User management")
        self.assertInBody("Add user")

    def test_edit_user_with_not_existing_username(self):
        """
        Verify failure trying to update invalid user.
        """
        self._edit_user("test4", "test1@test.com", "test1", "/var/backups/", False)
        self.assertInBody("User test4 doesn&#39;t exists.")

    def test_userfilter(self):
        """
        Check if admin filter is working.
        """
        self.getPage("/admin/users/?userfilter=admins")
        self.assertNotInBody("test1")

    def test_usersearch(self):
        """
        Check if user search is working.
        """
        self.getPage("/admin/users/?usersearch=tes")
        self.assertInBody("test1")
        self.getPage("/admin/users/?usersearch=coucou")
        self.assertNotInBody("test1")


class AdminUsersAsUserTest(AbstractAdminTest):
    """Integration test for page_admin"""

    reset_app = True

    def setUp(self):
        WebCase.setUp(self)
        # Add test user
        self.app.userdb.add_user('test', 'test123')
        self._login('test', 'test123')

    def test_add_user(self):
        """
        Check if adding user is forbidden.
        """
        self._add_user("test2", "test2@test.com", "test2", "/var/backups/", False)
        self.assertStatus(403)

    def test_delete_user(self):
        """
        Check if deleting user is forbidden.
        """
        self._delete_user("test")
        self.assertStatus(403)

    def test_edit_user(self):
        """
        Check if editing user is forbidden.
        """
        self._edit_user("test", "test1@test.com", "test", "/var/invalid/", False)
        self.assertStatus(403)

    def test_list(self):
        """
        Check if listing user is forbidden.
        """
        self.getPage("/admin/users/")
        self.assertStatus(403)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
