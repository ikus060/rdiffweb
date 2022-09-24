# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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

import os
from unittest.mock import ANY, MagicMock

import cherrypy

import rdiffweb.test
from rdiffweb.core.store import ADMIN_ROLE, MAINTAINER_ROLE, USER_ROLE


class AbstractAdminTest(rdiffweb.test.WebCase):
    """Class to regroup command method to test admin page."""

    def setUp(self):
        super().setUp()
        self._quota = {}
        self.listener = MagicMock()
        cherrypy.engine.subscribe('user_added', self.listener.user_added, priority=50)
        cherrypy.engine.subscribe('user_attr_changed', self.listener.user_attr_changed, priority=50)
        cherrypy.engine.subscribe('user_deleted', self.listener.user_deleted, priority=50)
        cherrypy.engine.subscribe('user_password_changed', self.listener.user_password_changed, priority=50)
        self.listener.get_disk_quota.side_effect = self._load_quota
        cherrypy.engine.subscribe('get_disk_quota', self.listener.get_disk_quota, priority=40)
        self.listener.get_disk_usage.return_value = 0
        cherrypy.engine.subscribe('get_disk_usage', self.listener.get_disk_usage, priority=40)
        self.listener.set_disk_quota.side_effect = self._store_quota
        cherrypy.engine.subscribe('set_disk_quota', self.listener.set_disk_quota, priority=40)

    def tearDown(self):
        cherrypy.engine.unsubscribe('user_added', self.listener.user_added)
        cherrypy.engine.unsubscribe('user_attr_changed', self.listener.user_attr_changed)
        cherrypy.engine.unsubscribe('user_deleted', self.listener.user_deleted)
        cherrypy.engine.unsubscribe('user_password_changed', self.listener.user_password_changed)
        cherrypy.engine.unsubscribe('get_disk_quota', self.listener.get_disk_quota)
        cherrypy.engine.unsubscribe('get_disk_usage', self.listener.get_disk_usage)
        cherrypy.engine.unsubscribe('set_disk_quota', self.listener.set_disk_quota)
        return super().tearDown()

    def _store_quota(self, userobj, value):
        self._quota[userobj.username] = value

    def _load_quota(self, userobj):
        return self._quota.get(userobj.username, 0)

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
        b = {'action': 'delete', 'username': username}
        self.getPage("/admin/users/", method='POST', body=b)


class AdminUsersAsAdminTest(AbstractAdminTest):
    """Integration test for page_admin"""

    login = True

    def test_add_user_with_role_admin(self):
        # When trying to create a new user with role admin
        self._add_user("admin_role", "admin_role@test.com", "password", "/home/", ADMIN_ROLE)
        # Then page return success
        self.assertStatus(200)
        # Then database is updated
        userobj = self.app.store.get_user('admin_role')
        self.assertEqual(ADMIN_ROLE, userobj.role)
        # Then notification was raised
        self.listener.user_added.assert_called_once_with(userobj)

    def test_add_user_with_role_maintainer(self):
        self._add_user("maintainer_role", "maintainer_role@test.com", "password", "/home/", MAINTAINER_ROLE)
        self.assertStatus(200)
        self.assertEqual(MAINTAINER_ROLE, self.app.store.get_user('maintainer_role').role)

    def test_add_user_with_role_user(self):
        self._add_user("user_role", "user_role@test.com", "password", "/home/", USER_ROLE)
        self.assertStatus(200)
        self.assertEqual(USER_ROLE, self.app.store.get_user('user_role').role)

    def test_add_user_with_invalid_role(self):
        # When trying to create a new user with an invalid role (admin instead of 0)
        self._add_user("invalid", "invalid@test.com", "test1234", "/home/", 'admin')
        # Then an error message is displayed to the user
        self.assertStatus(200)
        self.assertInBody('role: Invalid Choice: could not coerce')
        # Then listener are not called
        self.listener.user_added.assert_not_called()

        # When trying to create a new user with an invalid role (-1)
        self._add_user("invalid", "invalid@test.com", "test2", "/home/", -1)
        # Then an error message is displayed to the user
        self.assertStatus(200)
        self.assertInBody('role: Not a valid choice')
        # Then listener are not called
        self.listener.user_added.assert_not_called()

    def test_add_edit_delete(self):
        #  Add user to be listed
        self._add_user("test2", "test2@test.com", "test1234", "/home/", USER_ROLE)
        self.assertInBody("User added successfully.")
        self.assertInBody("test2")
        self.assertInBody("test2@test.com")
        self.listener.user_added.assert_called_once()
        self.listener.user_password_changed.assert_called_once()
        self.listener.user_password_changed.reset_mock()
        #  Update user
        self._edit_user("test2", "chaned@test.com", "new-password", "/tmp/", ADMIN_ROLE)
        self.listener.user_attr_changed.assert_called()
        self.listener.user_password_changed.assert_called_once()
        self.assertInBody("User information modified successfully.")
        self.assertInBody("test2")
        self.assertInBody("chaned@test.com")
        self.assertNotInBody("/home/")
        self.assertInBody("/tmp/")
        #  Check with filters
        self.getPage("/admin/users/?criteria=admins")
        self.assertInBody("test2")

        self._delete_user("test2")
        self.listener.user_deleted.assert_called()
        self.assertStatus(200)
        self.assertInBody("User account removed.")
        self.assertNotInBody("test2")

    def test_add_edit_delete_user_with_encoding(self):
        """
        Check creation of user with non-ascii char.
        """
        self._add_user("Éric", "éric@test.com", "password", "/home/", USER_ROLE)
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
        # Given a user named `test1`
        self._add_user("test1", "test1@test.com", "password", "/tmp/", USER_ROLE)
        # When trying to create a new user with the same name
        self._add_user("test1", "test1@test.com", "password", "/tmp/", USER_ROLE)
        # Then the user list is displayed with an error message.
        self.assertStatus(200)
        self.assertInBody("User test1 already exists.")

    def test_add_user_with_invalid_root_directory(self):
        """
        Verify failure to add a user with invalid root directory.
        """
        try:
            self._delete_user("test5")
        except Exception:
            pass
        self._add_user("test5", "test1@test.com", "password", "/var/invalid/", USER_ROLE)
        self.assertInBody("User added successfully.")
        self.assertInBody("User&#39;s root directory /var/invalid/ is not accessible!")

    def test_add_without_email(self):
        #  Add user to be listed
        self._add_user("test2", None, "password", "/tmp/", USER_ROLE)
        self.assertInBody("User added successfully.")

    def test_add_without_user_root(self):
        #  Add user to be listed
        self._add_user("test6", None, "password", None, USER_ROLE)
        self.assertInBody("User added successfully.")

        user = self.app.store.get_user('test6')
        self.assertEqual('', user.user_root)

    def test_add_with_username_too_long(self):
        # Given a too long username
        username = "test2" * 52
        # When trying to create the user
        self._add_user(username, None, "password", "/tmp/", USER_ROLE)
        # Then an error is raised
        self.assertStatus(200)
        self.assertInBody("Username too long.")

    def test_add_with_email_too_long(self):
        # Given a too long username
        email = ("test2" * 50) + "@test.com"
        # When trying to create the user
        self._add_user("test2", email, "password", "/tmp/", USER_ROLE)
        # Then an error is raised
        self.assertStatus(200)
        self.assertInBody("Email too long.")

    def test_add_with_user_root_too_long(self):
        # Given a too long user root
        user_root = "/temp/" * 50
        # When trying to create the user
        self._add_user("test2", "test@test,com", "password", user_root, USER_ROLE)
        # Then an error is raised
        self.assertStatus(200)
        self.assertInBody("Root directory too long.")

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
        self._add_user('admin2', '', 'password', '', ADMIN_ROLE)
        self.getPage("/logout/")
        self._login('admin2', 'password')

        # Try deleting admin user
        self._delete_user(self.USERNAME)
        self.assertStatus(200)
        self.assertInBody("can&#39;t delete admin user")

    def test_delete_user_method_get(self):
        # Given a user
        self.app.store.add_user('newuser')
        # When trying to delete this user using method GET
        self.getPage("/admin/users/?action=delete&username=newuser", method='GET')
        # Then page return without error
        self.assertStatus(200)
        # Then user is not deleted
        self.assertIsNotNone(self.app.store.get_user('newuser'))

    def test_change_password_with_too_short(self):
        self._edit_user(self.USERNAME, password='short')
        self.assertInBody("Password must have between 8 and 128 characters.")

    def test_change_password_with_too_long(self):
        new_password = 'a' * 129
        self._edit_user(self.USERNAME, password=new_password)
        self.assertInBody("Password must have between 8 and 128 characters.")

    def test_change_admin_password(self):
        # Given rdiffweb is configured with admin-password option
        self.app.cfg.admin_password = 'hardcoded'
        try:
            # When trying to update admin password
            self._edit_user('admin', password='new-password')
            # Then the form is refused with 200 OK with an error message.
            self.assertStatus(200)
            self.assertInBody("can&#39;t update admin-password defined in configuration file")
        finally:
            self.app.cfg.admin_password = None

    def test_edit_user_with_invalid_path(self):
        """
        Verify failure trying to update user with invalid path.
        """
        self.app.store.add_user('test1')
        self._edit_user("test1", "test1@test.com", "password", "/var/invalid/", USER_ROLE)
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
        # Given an invalid username
        username = 'invalid'
        # When trying to edit the user
        self._edit_user(username, "test1@test.com", "test", "/var/invalid/", USER_ROLE)
        # Then the user list is displayed with an error message
        self.assertStatus(200)
        self.assertInBody("Cannot edit user `invalid`: user doesn&#39;t exists")

    def test_criteria(self):
        """
        Check if admin criteria is working.
        """
        self.app.store.add_user('test1')
        self.getPage("/admin/users/?criteria=admins")
        self.assertNotInBody("test1")

    def test_search(self):
        """
        Check if user search is working.
        """
        self.app.store.add_user('test1')
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
        self.listener.get_disk_quota.side_effect = None
        self.listener.get_disk_quota.return_value = 654321
        # When querying the user list
        self.getPage("/admin/users/?criteria=admins")
        self.assertStatus(200)
        # Then get_disk_quota listenre is called
        self.listener.get_disk_quota.assert_called()
        # Then the quota value is displayed in human readable format
        self.assertInBody("638.99 KiB")
        self.assertStatus(200)

    def test_set_quota(self):
        # When updating user quota.
        self._edit_user("admin", disk_quota='8765432')
        # Then listenr get called
        self.listener.set_disk_quota.assert_called_once_with(ANY, 8765432)
        # Then a success message is displayed
        self.assertInBody("User information modified successfully.")
        self.assertStatus(200)

    def test_set_quota_as_gib(self):
        # When updating user quota
        self._edit_user("admin", disk_quota='1GiB')
        # Then listern get called
        self.listener.set_disk_quota.assert_called_once_with(ANY, 1073741824)
        # Then a success message is displayed
        self.assertInBody("User information modified successfully.")
        self.assertStatus(200)

    def test_set_quota_as_with_comma(self):
        # When updating quota with comma value
        self._edit_user("admin", disk_quota='1,5 GiB')
        # Then listner get called
        self.listener.set_disk_quota.assert_called_once_with(ANY, 1610612736)
        # Then a success message is displayed
        self.assertInBody("User information modified successfully.")
        self.assertStatus(200)

    def test_set_quota_as_with_leading_dot(self):
        # When updating quota with leading dot
        self._edit_user("admin", disk_quota='.5 GiB')
        # Then listener get called
        self.listener.set_disk_quota.assert_called_once_with(ANY, 536870912)
        # Then a success message is displayed
        self.assertInBody("User information modified successfully.")
        self.assertStatus(200)

    def test_set_quota_empty(self):
        # When quota is not defined
        self._edit_user("admin", disk_quota='')
        # Then listener is not called.
        self.listener.set_disk_quota.assert_not_called()
        # Then message is not displayed
        self.assertStatus(200)

    def test_set_quota_same_value(self):
        # Given an exiting quota
        self.listener.get_disk_quota.side_effect = None
        self.listener.get_disk_quota.return_value = 1234567890
        # When setting the quota value to the same value
        self._edit_user("admin", disk_quota='1.15 GiB')
        #  Then listener is not called
        self.listener.set_disk_quota.assert_not_called()
        # Then message is not displayed
        self.assertStatus(200)

    def test_set_quota_unsupported(self):
        # Given setting quota is not supported
        self.listener.set_disk_quota.side_effect = None
        self.listener.set_disk_quota.return_value = None
        # When updating the quota
        self._edit_user("admin", disk_quota='8765432')
        # Then
        self.listener.set_disk_quota.assert_called_once_with(ANY, 8765432)
        self.assertInBody("Setting user&#39;s quota is not supported")
        self.assertStatus(200)


class AdminUsersAsUserTest(AbstractAdminTest):
    """Integration test for page_admin"""

    def setUp(self):
        super().setUp()
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


class AdminWithNoLogsTest(rdiffweb.test.WebCase):

    login = True

    def test_logs(self):
        self.getPage("/admin/logs/")
        self.assertStatus(200)
        self.assertInBody("No log files")


class AdminWithLogsTest(rdiffweb.test.WebCase):

    login = True
    default_config = {'logfile': '/tmp/rdiffweb.log', 'logaccessfile': '/tmp/rdiffweb-access.log'}

    def test_logs(self):
        with open('/tmp/rdiffweb.log', 'w') as f:
            f.write("content of log file")
        with open('/tmp/rdiffweb-access.log', 'w') as f:
            f.write("content of log file")
        try:
            self.getPage("/admin/logs/")
            self.assertStatus(200)
            self.assertInBody("rdiffweb.log")
            self.assertInBody("content of log file")
            self.assertInBody("rdiffweb-access.log")
            self.assertNotInBody("Error getting file content")
        finally:
            os.remove('/tmp/rdiffweb.log')
            os.remove('/tmp/rdiffweb-access.log')


class AdminWithLogMissingTest(rdiffweb.test.WebCase):

    login = True
    default_config = {'logfile': './rdiffweb.log', 'logaccessfile': './rdiffweb-access.log'}

    def test_logs_with_no_file(self):
        self.getPage("/admin/logs/")
        self.assertStatus(200)
        self.assertInBody("rdiffweb.log")
        self.assertInBody("Error getting file content")

    def test_logs_with_invalid_file(self):
        self.getPage("/admin/logs/invalid")
        self.assertStatus(404)


class AdminReposTest(rdiffweb.test.WebCase):

    login = True

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


class AdminSysinfoTest(rdiffweb.test.WebCase):

    login = True

    def test_sysinfo(self):
        self.getPage("/admin/sysinfo")
        self.assertStatus(200)
        self.assertInBody("Operating System Info")
        self.assertInBody("Python Info")
