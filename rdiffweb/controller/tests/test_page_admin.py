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

import logging
import os
import unittest
from unittest.mock import MagicMock, ANY

from rdiffweb.core.quota import QuotaUnsupported
from rdiffweb.core.store import ADMIN_ROLE, MAINTAINER_ROLE, USER_ROLE
from rdiffweb.test import WebCase


class AbstractAdminTest(WebCase):
    """Class to regroup command method to test admin page."""

    def _add_user(self, username=None, email=None, password=None, user_root=None, role=None):
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
        if role is not None:
            b['role'] = str(role)
        self.getPage("/admin/users/", method='POST', body=b)

    def _edit_user(self, username=None, email=None, password=None, user_root=None, role=None, disk_quota=None):
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
        if role is not None:
            b['role'] = str(role)
        if disk_quota is not None:
            b['disk_quota'] = disk_quota
        self.getPage("/admin/users/", method='POST', body=b)

    def _delete_user(self, username='test1'):
        b = {'action': 'delete',
             'username': username}
        self.getPage("/admin/users/", method='POST', body=b)


class AdminUsersAsAdminTest(AbstractAdminTest):
    """Integration test for page_admin"""

    login = True

    def test_add_user_with_role(self):
        #  Add user to be listed
        self._add_user("admin_role", "admin_role@test.com", "test2", "/home/", ADMIN_ROLE)
        self.assertEqual(ADMIN_ROLE, self.app.store.get_user('admin_role').role)

        self._add_user("maintainer_role", "maintainer_role@test.com", "test2", "/home/", MAINTAINER_ROLE)
        self.assertEqual(MAINTAINER_ROLE, self.app.store.get_user('maintainer_role').role)

        self._add_user("user_role", "user_role@test.com", "test2", "/home/", USER_ROLE)
        self.assertEqual(USER_ROLE, self.app.store.get_user('user_role').role)

    def test_add_user_with_invalid_role(self):
        # Invalid roles
        self._add_user("invalid", "invalid@test.com", "test2", "/home/", 'admin')
        self.assertStatus(200)
        self.assertInBody('role: Invalid Choice: could not coerce')

        self._add_user("invalid", "invalid@test.com", "test2", "/home/", -1)
        self.assertStatus(200)
        self.assertInBody('role: Not a valid choice')

    def test_add_edit_delete(self):
        #  Add user to be listed
        self._add_user("test2", "test2@test.com", "test2", "/home/", USER_ROLE)
        self.assertInBody("User added successfully.")
        self.assertInBody("test2")
        self.assertInBody("test2@test.com")
        #  Update user
        self._edit_user("test2", "chaned@test.com", "new-password", "/tmp/", ADMIN_ROLE)
        self.assertInBody("User information modified successfully.")
        self.assertInBody("test2")
        self.assertInBody("chaned@test.com")
        self.assertNotInBody("/home/")
        self.assertInBody("/tmp/")
        #  Check with filters
        self.getPage("/admin/users/?criteria=admins")
        self.assertInBody("test2")

        self._delete_user("test2")
        self.assertStatus(200)
        self.assertInBody("User account removed.")
        self.assertNotInBody("test2")

    def test_add_edit_delete_user_with_encoding(self):
        """
        Check creation of user with non-ascii char.
        """
        self._add_user("Éric", "éric@test.com", "Éric", "/home/", USER_ROLE)
        self.assertInBody("User added successfully.")
        self.assertInBody("Éric")
        self.assertInBody("éric@test.com")
        # Update user
        self._edit_user("Éric", "eric.létourno@test.com", "écureuil", "/tmp/", ADMIN_ROLE)
        self.assertInBody("User information modified successfully.")
        self.assertInBody("Éric")
        self.assertInBody("eric.létourno@test.com")
        self.assertNotInBody("/home/")
        self.assertInBody("/tmp/")
        # Check with filter
        self.getPage("/admin/users/?criteria=admins")
        self.assertInBody("Éric")

        self._delete_user("Éric")
        self.assertInBody("User account removed.")
        self.assertNotInBody("Éric")

    def test_add_user_with_empty_username(self):
        """
        Verify failure trying to create user without username.
        """
        self._add_user("", "test1@test.com", "test1", "/tmp/", USER_ROLE)
        self.assertStatus(200)
        self.assertInBody("username: This field is required.")

    def test_add_user_with_existing_username(self):
        """
        Verify failure trying to add the same user.
        """
        self._add_user("test1", "test1@test.com", "test1", "/tmp/", USER_ROLE)
        self._add_user("test1", "test1@test.com", "test1", "/tmp/", USER_ROLE)
        self.assertInBody("User test1 already exists.")

    def test_add_user_with_invalid_root_directory(self):
        """
        Verify failure to add a user with invalid root directory.
        """
        try:
            self._delete_user("test5")
        except:
            pass
        self._add_user("test5", "test1@test.com", "test5", "/var/invalid/", USER_ROLE)
        self.assertInBody("User added successfully.")
        self.assertInBody("User&#39;s root directory /var/invalid/ is not accessible!")

    def test_add_without_email(self):
        #  Add user to be listed
        self._add_user("test2", None, "test2", "/tmp/", USER_ROLE)
        self.assertInBody("User added successfully.")

    def test_add_without_user_root(self):
        #  Add user to be listed
        self._add_user("test6", None, "test6", None, USER_ROLE)
        self.assertInBody("User added successfully.")

        user = self.app.store.get_user('test6')
        self.assertEquals('', user.user_root)

    def test_delete_user_with_not_existing_username(self):
        """
        Verify failure to delete invalid username.
        """
        self._delete_user("test3")
        self.assertInBody("User doesn&#39;t exists!")

    def test_delete_our_self(self):
        """
        Verify failure to delete our self.
        """
        self._delete_user(self.USERNAME)
        self.assertInBody("You cannot remove your own account!")

    def test_delete_user_admin(self):
        """
        Verify failure to delete our self.
        """
        # Create another admin user
        self._add_user('admin2', '', 'password', '' , ADMIN_ROLE)
        self.getPage("/logout/")
        self._login('admin2', 'password')

        # Try deleting admin user
        self._delete_user(self.USERNAME)
        self.assertStatus(200)
        self.assertInBody("can&#39;t delete admin user")

    def test_edit_user_with_invalid_path(self):
        """
        Verify failure trying to update user with invalid path.
        """
        self._edit_user("test1", "test1@test.com", "test", "/var/invalid/", USER_ROLE)
        self.assertNotInBody("User added successfully.")
        self.assertInBody("User&#39;s root directory /var/invalid/ is not accessible!")

    def test_list(self):
        self.getPage("/admin/users/")
        self.assertInBody("Users")
        self.assertInBody("User management")
        self.assertInBody("Add user")

    def test_edit_user_with_not_existing_username(self):
        """
        Verify failure trying to update invalid user.
        """
        self._edit_user("test4", "test1@test.com", "test1", "/tmp/", USER_ROLE)
        self.assertStatus(500)

    def test_criteria(self):
        """
        Check if admin criteria is working.
        """
        self.getPage("/admin/users/?criteria=admins")
        self.assertNotInBody("test1")

    def test_search(self):
        """
        Check if user search is working.
        """
        self.getPage("/admin/users?search=tes")
        self.assertInBody("test1")
        self.getPage("/admin/users?search=coucou")
        self.assertNotInBody("test1")

    def test_user_invalid_root(self):
        # Delete all user's
        for user in self.app.store.users():
            if user.username != self.USERNAME:
                user.delete()
        # Change the user's root
        user = self.app.store.get_user('admin')
        user.user_root = "/invalid"
        self.getPage("/admin/users")
        self.assertInBody("Root directory not accessible!")

        # Query the page by default
        user = self.app.store.get_user('admin')
        user.user_root = "/tmp/"
        self.getPage("/admin/users")
        self.assertNotInBody("Root directory not accessible!")

    def test_get_quota(self):
        # Mock a quota.
        self.app.quota.get_disk_quota = MagicMock(return_value=654321)
        self.getPage("/admin/users/?criteria=admins")
        self.assertInBody("638.99 KiB")
        self.assertStatus(200)

    def test_set_quota(self):
        # Mock a quota.
        self.app.quota.set_disk_quota = MagicMock()
        self._edit_user("admin", disk_quota='8765432')
        self.app.quota.set_disk_quota.assert_called_once_with(ANY, 8765432)
        self.assertInBody("User&#39;s quota updated")
        self.assertStatus(200)

    def test_set_quota_as_gib(self):
        # Mock a quota.
        self.app.quota.set_disk_quota = MagicMock()
        self._edit_user("admin", disk_quota='1GiB')
        self.app.quota.set_disk_quota.assert_called_once_with(ANY, 1073741824)
        self.assertInBody("User&#39;s quota updated")
        self.assertStatus(200)

    def test_set_quota_as_with_comma(self):
        # Mock a quota.
        self.app.quota.set_disk_quota = MagicMock()
        self._edit_user("admin", disk_quota='1,5 GiB')
        self.app.quota.set_disk_quota.assert_called_once_with(ANY, 1610612736)
        self.assertInBody("User&#39;s quota updated")
        self.assertStatus(200)

    def test_set_quota_as_with_leading_dot(self):
        # Mock a quota.
        self.app.quota.set_disk_quota = MagicMock()
        self._edit_user("admin", disk_quota='.5 GiB')
        self.app.quota.set_disk_quota.assert_called_once_with(ANY, 536870912)
        self.assertInBody("User&#39;s quota updated")
        self.assertStatus(200)

    def test_set_quota_empty(self):
        # Mock a quota.
        self.app.quota.set_disk_quota = MagicMock()
        self._edit_user("admin", disk_quota='')
        # Make sure quota isnot called.
        self.app.quota.set_disk_quota.assert_not_called()
        self.assertNotInBody("User&#39;s quota updated")
        self.assertStatus(200)

    def test_set_quota_same_value(self):
        # Mock a quota.
        self.app.quota.get_disk_quota = MagicMock(return_value=1234567890)
        self.app.quota.set_disk_quota = MagicMock()
        self._edit_user("admin", disk_quota='1.15 GiB')
        # Verify that set_quota is not called.
        self.app.quota.set_disk_quota.assert_not_called()
        self.assertNotInBody("User&#39;s quota updated")
        self.assertStatus(200)

    def test_set_quota_unsupported(self):
        # Mock a quota.
        self.app.quota.set_disk_quota = MagicMock(side_effect=QuotaUnsupported())
        self._edit_user("admin", disk_quota='8765432')
        self.app.quota.set_disk_quota.assert_called_once_with(ANY, 8765432)
        self.assertInBody("Setting user&#39;s quota is not supported")
        self.assertStatus(200)


class AdminUsersAsUserTest(AbstractAdminTest):
    """Integration test for page_admin"""

    reset_app = True

    def setUp(self):
        WebCase.setUp(self)
        # Add test user
        self.app.store.add_user('test', 'test123')
        self._login('test', 'test123')

    def test_add_user(self):
        """
        Check if adding user is forbidden.
        """
        self._add_user("test2", "test2@test.com", "test2", "/tmp/", USER_ROLE)
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
        self._edit_user("test", "test1@test.com", "test", "/var/invalid/", USER_ROLE)
        self.assertStatus(403)

    def test_users(self):
        """
        Check if listing user is forbidden.
        """
        self.getPage("/admin/users")
        self.assertStatus(403)

    def test_repos(self):
        """
        Check if listing user is forbidden.
        """
        self.getPage("/admin/repos")
        self.assertStatus(403)


class AdminLogsTest(WebCase):

    login = True

    def test_no_logs(self):
        self.app.cfg['logfile'] = None
        self.app.cfg['logaccessfile'] = None

        self.getPage("/admin/logs/")
        self.assertStatus(200)
        self.assertInBody("No log files")

    def test_logs(self):
        self.app.cfg['logfile'] = './rdiffweb.log'
        self.app.cfg['logaccessfile'] = './rdiffweb-access.log'

        with open('./rdiffweb.log', 'w') as f:
            f.write("content of log file")

        self.getPage("/admin/logs/")
        self.assertStatus(200)
        self.assertInBody("rdiffweb.log")
        self.assertInBody("content of log file")
        self.assertInBody("rdiffweb-access.log")

        os.remove('./rdiffweb.log')

    def test_logs_with_no_file(self):
        self.app.cfg['logfile'] = './rdiffweb.log'
        self.app.cfg['logaccessfile'] = './rdiffweb-access.log'

        self.getPage("/admin/logs/")
        self.assertStatus(200)
        self.assertInBody("rdiffweb.log")
        self.assertInBody("Error getting file content")

    def test_logs_with_invalid_file(self):
        self.app.cfg['logfile'] = './rdiffweb.log'
        self.app.cfg['logaccessfile'] = './rdiffweb-access.log'

        self.getPage("/admin/logs/invalid")
        self.assertStatus(404)


class AdminReposTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    def test_repos(self):
        self.getPage("/admin/repos")
        self.assertStatus(200)

    def test_repos_with_search(self):
        # Search something that exists
        self.getPage("/admin/repos?search=test")
        self.assertStatus(200)
        self.assertInBody(self.REPO)

        # Search something that doesn't exists
        self.getPage("/admin/repos?search=coucou")
        self.assertStatus(200)
        self.assertNotInBody(self.REPO)
        self.assertInBody("No repository found")

    def test_repos_with_criteria(self):
        # Search something that exists
        self.getPage("/admin/repos?criteria=ok")
        self.assertStatus(200)
        self.assertInBody(self.REPO)

        # Search something that exists
        self.getPage("/admin/repos?criteria=failed")
        self.assertStatus(200)
        self.assertNotInBody(self.REPO)
        self.assertInBody("No repository found")


class AdminSysinfoTest(WebCase):

    login = True

    def test_sysinfo(self):
        self.getPage("/admin/sysinfo")
        self.assertStatus(200)
        self.assertInBody("Operating System Info")
        self.assertInBody("Python Info")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
