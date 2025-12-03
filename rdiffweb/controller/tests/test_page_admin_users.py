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
import json
import os
from base64 import b64encode
from unittest.mock import ANY, MagicMock

import cherrypy
from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.model import UserObject


class AdminTest(rdiffweb.test.WebCase):
    login = True

    def setUp(self):
        super().setUp()
        self._quota = {}
        self.listener = MagicMock()
        cherrypy.engine.subscribe('user_added', self.listener.user_added, priority=50)
        cherrypy.engine.subscribe('user_updated', self.listener.user_updated, priority=50)
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
        cherrypy.engine.unsubscribe('user_updated', self.listener.user_updated)
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

    def _add_user(self, username=None, email=None, password=None, user_root=None, role=None, mfa=None, fullname=None):
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
        if mfa is not None:
            b['mfa'] = str(mfa)
        if fullname is not None:
            b['fullname'] = str(fullname)
        self.getPage("/admin/users/new", method='POST', body=b)

    def _edit_user(
        self,
        username=None,
        email=None,
        password=None,
        user_root=None,
        role=None,
        disk_quota=None,
        mfa=None,
        lang=None,
        report_time_range=None,
        disabled=None,
    ):
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
        if mfa is not None:
            b['mfa'] = str(mfa)
        if lang is not None:
            b['lang'] = str(lang)
        if report_time_range is not None:
            b['report_time_range'] = str(report_time_range)
        if disabled is not None:
            b['disabled'] = str(disabled)
        self.getPage("/admin/users/edit/" + username, method='POST', body=b)

    def _delete_user(self, username, confirm=None, delete_data=None):
        body = {'username': username}
        if confirm is not None:
            body['confirm'] = confirm
        if delete_data is not None:
            body['delete_data'] = str(delete_data)
        self.getPage("/admin/users/delete", method='POST', body=body)

    def test_add_user_with_role_admin(self):
        # When trying to create a new user with role admin
        self._add_user("admin_role", "admin_role@test.com", "pr3j5Dwi", "/home/", UserObject.ADMIN_ROLE)
        # Then page return success
        self.assertStatus(303)
        # Then database is updated
        userobj = UserObject.get_user('admin_role')
        self.assertEqual(UserObject.ADMIN_ROLE, userobj.role)
        # Then notification was raised
        self.listener.user_added.assert_called_once_with(userobj)

    def test_add_user_with_role_maintainer(self):
        self._add_user("maintainer_role", "maintainer_role@test.com", "pr3j5Dwi", "/home/", UserObject.MAINTAINER_ROLE)
        self.assertStatus(303)
        self.assertEqual(UserObject.MAINTAINER_ROLE, UserObject.get_user('maintainer_role').role)

    def test_add_user_with_role_user(self):
        self._add_user("user_role", "user_role@test.com", "pr3j5Dwi", "/home/", UserObject.USER_ROLE)
        self.assertStatus(303)
        self.assertEqual(UserObject.USER_ROLE, UserObject.get_user('user_role').role)

    def test_add_user_with_invalid_role(self):
        # When trying to create a new user with an invalid role
        self._add_user("invalid", "invalid@test.com", "pr3j5Dwi", "/home/", 'invalid')
        # Then an error message is displayed to the user
        self.assertStatus(200)
        self.assertInBody('Role: Invalid Choice: could not coerce')
        # Then listener are not called
        self.listener.user_added.assert_not_called()

        # When trying to create a new user with an invalid role (-1)
        self._add_user("invalid", "invalid@test.com", "pr3j5Dwi", "/home/", -1)
        # Then an error message is displayed to the user
        self.assertStatus(200)
        self.assertInBody('User Role: Not a valid choice')
        # Then listener are not called
        self.listener.user_added.assert_not_called()

    def test_add_edit_delete(self):
        #  Add user to be listed
        self.listener.user_password_changed.reset_mock()
        self._add_user(
            "test2", "test2@test.com", "pr3j5Dwi", "/home/", UserObject.USER_ROLE, mfa=UserObject.DISABLED_MFA
        )
        self.assertStatus(303)
        self.getPage('/admin/users/')
        self.assertInBody("User added successfully.")
        self.assertInBody("test2")
        self.assertInBody("test2@test.com")
        self.listener.user_added.assert_called_once()
        self.listener.user_password_changed.reset_mock()
        #  Update user
        self._edit_user(
            "test2", "chaned@test.com", "new-password", "/tmp/", UserObject.ADMIN_ROLE, mfa=UserObject.ENABLED_MFA
        )
        self.assertStatus(303)
        self.getPage('/admin/users/')
        self.listener.user_updated.assert_called()
        self.listener.user_password_changed.assert_called_once()
        self.assertInBody("User information modified successfully.")
        self.assertInBody("test2")
        self.assertInBody("chaned@test.com")
        self.assertNotInBody("/home/")
        self.assertInBody("/tmp/")

        self._delete_user("test2", confirm="test2")
        cherrypy.scheduler.wait_for_jobs()
        self.listener.user_deleted.assert_called()
        self.assertStatus(303)
        self.getPage('/admin/users/')
        self.assertInBody("User account removed.")
        self.assertNotInBody("test2")

    @parameterized.expand(
        [
            # Invalid
            ('evil.com', False),
            ('http://test', False),
            ('email@test.test', False),
            ('/test/', False),
            # Valid
            ('My fullname', True),
            ('Test Test', True),
            ('Éric Terrien-Pascal', True),
            ("Tel'c", True),
        ]
    )
    def test_edit_fullname_with_special_character(self, new_fullname, expected_valid):
        # Given an existing user
        # When updating the user's fullname
        self.getPage(
            "/admin/users/edit/" + self.USERNAME,
            method='POST',
            body={'action': 'edit', 'username': self.USERNAME, 'fullname': new_fullname},
        )
        if expected_valid:
            self.assertStatus(303)
            self.getPage('/admin/users/')
            self.assertInBody("User information modified successfully.")
            self.assertNotInBody("Fullname: Must not contain any special characters.")
        else:
            self.assertStatus(200)
            self.assertNotInBody("User information modified successfully.")
            self.assertInBody("Fullname: Must not contain any special characters.")

    def test_edit_wrong_username(self):
        # Given a new user
        UserObject(username='newuser').add().commit()
        # When trying to edit a user object with wrong username in path vs form
        self.getPage(
            "/admin/users/edit/" + self.USERNAME,
            method='POST',
            body={'action': 'edit', 'username': 'newuser'},
        )
        # Then an error is raised
        self.assertStatus(200)
        self.assertInBody('Cannot change username of and existing user.')

    def test_edit_enable_mfa_without_email(self):
        # Given a new user
        newuser = UserObject(username='newuser').add().commit()
        # When trying to enable mfa without user's email
        self.getPage(
            "/admin/users/edit/newuser",
            method='POST',
            body={'action': 'edit', 'username': 'newuser', 'mfa': '1'},
        )
        # Then error message is displayed.
        self.assertStatus(200)
        self.assertInBody('User email is required to enabled Two-Factor Authentication')
        # Then change is not saved
        newuser.expire()
        self.assertEqual(0, newuser.mfa)

    @parameterized.expand(
        [
            # Invalid
            ('http://username', False),
            ('username@test.test', False),
            ('/username/', False),
            ('123456', False),
            ('1foo', False),
            ('foo bar', False),
            ('foo@', False),
            ('foo#', False),
            ('foo!', False),
            # Valid
            ('username.com', True),
            ('admin_user', True),
            ('test.test', True),
            ('test-test', True),
        ]
    )
    def test_add_user_with_special_character(self, new_username, expected_valid):
        self._add_user(new_username, "eric@test.com", "pr3j5Dwi", "/home/", UserObject.USER_ROLE)
        if expected_valid:
            self.assertStatus(303)
            self.getPage('/admin/users/')
            self.assertInBody("User added successfully.")
            self.assertNotInBody("Username: Must not contain any special characters.")
        else:
            self.assertStatus(200)
            self.assertNotInBody("User added successfully.")
            self.assertInBody(
                "Username: Must start with a letter and contain only letters, numbers, underscores (_), hyphens (-), or periods (.)."
            )

    def test_add_user_with_empty_username(self):
        """
        Verify failure trying to create user without username.
        """
        self._add_user("", "test1@test.com", "pr3j5Dwi", "/tmp/", UserObject.USER_ROLE)
        self.assertStatus(200)
        self.assertInBody("Username: This field is required.")

    def test_add_user_with_existing_username(self):
        """
        Verify failure trying to add the same user.
        """
        # Given a user named `test1`
        self._add_user("test1", "test1@test.com", "pr3j5Dwi", "/tmp/", UserObject.USER_ROLE)
        # When trying to create a new user with the same name
        self._add_user("test1", "test1@test.com", "pr3j5Dwi", "/tmp/", UserObject.USER_ROLE)
        # Then the user list is displayed with an error message.
        self.assertStatus(200)
        self.assertInBody("A user with this username address already exists.")

    def test_add_user_with_invalid_root_directory(self):
        """
        Verify failure to add a user with invalid root directory.
        """
        try:
            self._delete_user("test5", confirm="test5")
        except Exception:
            pass
        self._add_user("test5", "test1@test.com", "pr3j5Dwi", "/var/invalid/", UserObject.USER_ROLE)
        self.assertStatus(303)
        self.getPage("/admin/users/")
        self.assertInBody("User added successfully.")
        self.assertInBody("User&#39;s root directory /var/invalid/ is not accessible!")

    def test_add_without_email(self):
        # When adding a user without email address
        self._add_user("test2", None, "pr3j5Dwi", "/tmp/", UserObject.USER_ROLE)
        self.assertStatus(303)
        # Then user get added.
        self.getPage("/admin/users/")
        self.assertInBody("User added successfully.")

    def test_add_without_user_root(self):
        # When adding user without user_root
        self._add_user("test6", None, "pr3j5Dwi", None, UserObject.USER_ROLE)
        self.assertStatus(303)
        # Then user get added
        self.getPage("/admin/users/")
        self.assertInBody("User added successfully.")
        user = UserObject.get_user('test6')
        self.assertEqual('', user.user_root)

    def test_add_with_username_too_long(self):
        # Given a too long username
        username = "test2" * 52
        # When trying to create the user
        self._add_user(username, None, "pr3j5Dwi", "/tmp/", UserObject.USER_ROLE)
        # Then an error is raised
        self.assertStatus(200)
        self.assertInBody("Username too long.")

    def test_add_with_email_too_long(self):
        # Given a too long username
        email = ("test2" * 50) + "@test.com"
        # When trying to create the user
        self._add_user("test2", email, "pr3j5Dwi", "/tmp/", UserObject.USER_ROLE)
        # Then an error is raised
        self.assertStatus(200)
        self.assertInBody("Email too long.")

    def test_add_with_user_root_too_long(self):
        # Given a too long user root
        user_root = "/temp/" * 50
        # When trying to create the user
        self._add_user("test2", "test@test,com", "pr3j5Dwi", user_root, UserObject.USER_ROLE)
        # Then an error is raised
        self.assertStatus(200)
        self.assertInBody("Root directory too long.")

    def test_add_with_fullname_too_long(self):
        # Given a too long user root
        fullname = "fullname" * 50
        # When trying to create the user
        self._add_user("test2", "test@test,com", "pr3j5Dwi", "/tmp/", UserObject.USER_ROLE, fullname=fullname)
        # Then an error is raised
        self.assertStatus(200)
        self.assertInBody("Fullname too long.")

    def test_delete_user_with_delete_data(self):
        # Given a user with data
        admin = UserObject.get_user(self.USERNAME)
        self._add_user('my-user', user_root=admin.user_root)
        myuser = UserObject.get_user('my-user')
        self.assertTrue(myuser.repo_objs)
        self.assertTrue(os.listdir(admin.user_root))
        # When deleting the user with data
        self._delete_user('my-user', confirm='my-user', delete_data=1)
        cherrypy.scheduler.wait_for_jobs()
        # Then the user is deleted
        myuser = UserObject.get_user('my-user')
        self.assertIsNone(myuser)
        # Then the data is also deleted
        self.assertFalse(os.listdir(admin.user_root))

    def test_delete_user_with_not_existing_username(self):
        # When trying to delete an invalid user
        self._delete_user("test3", confirm="test3")
        # Then an error is returned
        self.assertStatus(400)
        self.assertInBody("User test3 doesn&#39;t exists")

    def test_delete_our_self(self):
        # When trying to delete your self
        self._delete_user(self.USERNAME, confirm=self.USERNAME)
        # Then user is redirected.
        self.assertStatus(303)
        self.getPage('/admin/users/')
        # Then and error is returned
        self.assertStatus(200)
        self.assertInBody("You cannot remove your own account!")

    def test_delete_user_admin(self):
        # Create another admin user
        self._add_user('admin2', '', 'pr3j5Dwi', '', UserObject.ADMIN_ROLE)
        self.getPage("/logout", method="POST")
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/')
        self._login('admin2', 'pr3j5Dwi')

        # When trying to delete admin user
        self._delete_user(self.USERNAME, confirm=self.USERNAME)
        # Then an error is returned
        self.assertStatus(303)
        self.getPage('/admin/users/')
        self.assertInBody("can&#39;t delete admin user")

    def test_delete_user_method_get(self):
        # Given a user
        user = UserObject.add_user('newuser')
        user.commit()
        # When trying to delete this user using method GET
        self.getPage("/admin/users/delete?username=newuser", method='GET')
        # Then page return without error
        self.assertStatus(405)
        # Then user is not deleted
        self.assertIsNotNone(UserObject.get_user('newuser'))

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
        # Given an existing user.
        userobj = UserObject.add_user('test1')
        userobj.commit()
        # When updating user oot with invalid path
        self._edit_user("test1", "test1@test.com", "pr3j5Dwi", "/var/invalid/", UserObject.USER_ROLE)
        # Then user is updated
        self.assertStatus(303)
        self.getPage("/admin/users/")
        self.assertNotInBody("User added successfully.")
        # Then an error message is displayed.
        self.assertInBody("User&#39;s root directory /var/invalid/ is not accessible!")

    def test_list(self):
        self.getPage("/admin/users/")
        self.assertInBody("Users")
        self.assertInBody("User management")
        self.assertInBody("Add user")

    def test_edit_user_with_not_existing_username(self):
        # Given an invalid username
        username = 'invalid'
        # When trying to edit the user
        self._edit_user(username, "test1@test.com", "test", "/var/invalid/", UserObject.USER_ROLE)
        # Then the user list is displayed with an error message
        self.assertStatus(400)
        self.assertInBody("User invalid doesn&#39;t exists")

    def test_user_invalid_root(self):
        # Change the user's root
        user = UserObject.get_user(self.USERNAME)
        user.user_root = "/invalid"
        user.commit()
        self.getPage("/admin/users/")
        self.assertInBody("Root directory not accessible!")

        # Query the page by default
        user = UserObject.get_user('admin')
        user.user_root = "/tmp/"
        user.commit()
        self.getPage("/admin/users/")
        self.assertNotInBody("Root directory not accessible!")

    def test_get_quota(self):
        # Mock a quota.
        self.listener.get_disk_quota.side_effect = None
        self.listener.get_disk_quota.return_value = 654321
        # When edigint users
        self.getPage("/admin/users/edit/admin")
        self.assertStatus(200)
        # Then get_disk_quota listenre is called
        self.listener.get_disk_quota.assert_called()
        # Then the quota value is displayed in human readable format
        self.assertInBody("638.99 KiB")
        self.assertStatus(200)

    @parameterized.expand(
        [
            ('8765432', 8765432),
            ('1GiB', 1073741824),
            ('1,5 GiB', 1610612736),
            ('1.5 GiB', 1610612736),
            ('.5 GiB', 536870912),
        ]
    )
    def test_set_quota(self, form_value, expected_value):
        # When updating user quota.
        self._edit_user("admin", disk_quota=form_value)
        self.assertStatus(303)
        # Then listenr get called
        self.listener.set_disk_quota.assert_called_once_with(ANY, expected_value)
        # Then a success message is displayed
        self.getPage("/admin/users/")
        self.assertInBody("User information modified successfully.")

    def test_set_quota_empty(self):
        # When quota is not defined
        self._edit_user("admin", disk_quota='')
        self.assertStatus(303)
        # Then listener is not called.
        self.listener.set_disk_quota.assert_not_called()

    def test_set_quota_same_value(self):
        # Given an exiting quota
        self.listener.get_disk_quota.side_effect = None
        self.listener.get_disk_quota.return_value = 1234567890
        # When setting the quota value to the same value
        self._edit_user("admin", disk_quota='1.15 GiB')
        self.assertStatus(303)
        #  Then listener is not called
        self.listener.set_disk_quota.assert_not_called()

    def test_set_quota_unsupported(self):
        # Given setting quota is not supported
        self.listener.set_disk_quota.side_effect = None
        self.listener.set_disk_quota.return_value = None
        # When updating the quota
        self._edit_user("admin", disk_quota='8765432')
        self.assertStatus(303)
        # Then error message is displayed
        self.listener.set_disk_quota.assert_called_once_with(ANY, 8765432)
        self.getPage("/admin/users/")
        self.assertInBody("Setting user&#39;s quota is not supported")

    def test_edit_own_role(self):
        # Given an administrator
        # When trygin to update your own role
        self._edit_user(username=self.USERNAME, role=UserObject.MAINTAINER_ROLE)
        # Then an error is returned
        self.assertStatus(200)
        self.assertInBody("Cannot edit your own role.")

    def test_edit_own_mfa(self):
        # Given an administrator
        # When trygin to update your own role
        self._edit_user(username=self.USERNAME, mfa=UserObject.ENABLED_MFA)
        # Then an error is returned
        self.assertStatus(200)
        self.assertInBody("Cannot change your own two-factor authentication settings.")

    def test_edit_report_time_range(self):
        # Given a user
        # When editing the report_time_range
        self._edit_user(username=self.USERNAME, report_time_range=7)
        # Then report_time_range is updated
        userobj = UserObject.get_user(self.USERNAME)
        self.assertEqual(7, userobj.report_time_range)

    def test_edit_lang(self):
        # Given a user
        # When editing the lang
        self._edit_user(username=self.USERNAME, lang='fr')
        # Then lang is updated
        userobj = UserObject.get_user(self.USERNAME)
        self.assertEqual('fr', userobj.lang)

    def test_disable_user(self):
        # Given a user
        user = UserObject.add_user('newuser')
        user.commit()
        # When editing the lang
        self._edit_user(username=user.username, disabled='checked')
        self.assertStatus(303)
        # Then lang is updated
        user.expire()
        self.assertTrue(user.disabled)
        self.assertEqual(user.status, UserObject.STATUS_DISABLED)

    def test_disable_admin_user(self):
        # Given an admin user
        # When editing the lang
        self._edit_user(username=self.USERNAME, disabled='checked')
        self.assertStatus(200)
        # Then an error is raised.
        self.assertInBody("can&#39;t delete or disable admin user")
        user = UserObject.get_user(self.USERNAME)
        self.assertFalse(user.disabled)
        self.assertEqual(user.status, '')


class AdminTestWithoutQuota(rdiffweb.test.WebCase):
    login = True

    def test_edit(self):
        # When editing user
        self.getPage("/admin/users/edit/admin")
        # Then quota field is readonly
        self.assertStatus(200)
        self.assertInBody('<input class="form-control" disabled name="disk_quota" readonly')


class AdminApiUsersTest(rdiffweb.test.WebCase):

    auth = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]

    @parameterized.expand(
        [
            ('with_userid', 0),
            ('with_userid', 1),
            ('with_username', 0),
            ('with_username', 1),
        ]
    )
    def test_delete(self, query, with_data):
        # Given a new user with repositories
        user_obj = (
            UserObject(username='newuser', fullname='New User', email='test@example.com', lang='fr', mfa=1)
            .add()
            .commit()
        )

        # When deleting the user
        if query == 'with_userid':
            self.getPage(
                f'/api/users/{user_obj.id}',
                headers=self.auth,
                method='DELETE',
                body={'delete_data': str(with_data)},
            )
        else:
            self.getPage(
                f'/api/users/{user_obj.username}',
                headers=self.auth,
                method='DELETE',
                body={'delete_data': str(with_data)},
            )
        # Then page return with success
        self.assertStatus('200 OK')

        # Then user get deleted from database
        self.assertIsNone(UserObject.get_user('newuser'))

    @parameterized.expand(
        [
            ('with_id'),
            ('with_username'),
        ]
    )
    def test_get(self, query):
        # Given a new user
        user_obj = (
            UserObject(username='newuser', fullname='New User', email='test@example.com', lang='fr', mfa=1)
            .add()
            .commit()
        )

        # When querying our user with Id.
        if query == 'with_id':
            data = self.getJson(
                f'/api/users/{user_obj.id}',
                headers=self.auth,
                method='GET',
            )
        elif query == 'with_username':
            data = self.getJson(
                f'/api/users/{user_obj.username}',
                headers=self.auth,
                method='GET',
            )
        # Then page return with success with sshkey
        self.assertStatus('200 OK')
        self.assertEqual(
            data,
            {
                'id': 2,
                'username': 'newuser',
                'fullname': 'New User',
                'email': 'test@example.com',
                'lang': 'fr',
                'mfa': 1,
                'role': 'user',
                'report_time_range': 0,
                'repos': [],
                'disk_quota': 0,
                'disk_usage': 0,
            },
        )

    def test_get_invalid(self):
        # When querying invalid user
        self.getPage(
            '/api/users/invalid',
            headers=self.auth,
            method='GET',
        )
        # Then page return NotFound
        self.assertStatus(404)

    def test_list(self):
        # Given a new user
        UserObject(username='newuser', fullname='New User', email='test@example.com', lang='fr', mfa=1).add().commit()

        # When querying the list of user.
        data = self.getJson(
            '/api/users',
            headers=self.auth,
            method='GET',
        )
        # Then page return with success with sshkey
        self.assertStatus('200 OK')
        self.assertEqual(
            data,
            [
                {
                    'id': 1,
                    'username': 'admin',
                    'fullname': '',
                    'email': '',
                    'lang': '',
                    'mfa': 0,
                    'role': 'admin',
                    'report_time_range': 0,
                },
                {
                    'id': 2,
                    'username': 'newuser',
                    'fullname': 'New User',
                    'email': 'test@example.com',
                    'lang': 'fr',
                    'mfa': 1,
                    'role': 'user',
                    'report_time_range': 0,
                },
            ],
        )

    @parameterized.expand(
        [
            ('as_json', [('Content-Type', 'application/json')], {'username': 'newuser', 'fullname': "My Fullname"}),
            (
                'as_form',
                [],  # Default to 'application/x-www-form-urlencoded'
                {'username': 'newuser', 'fullname': "My Fullname"},
            ),
            (
                'admin_role_as_int',
                [('Content-Type', 'application/json')],
                {'username': 'newuser', 'fullname': "My Fullname", 'role': '0'},
            ),
            (
                'admin_role_as_string',
                [('Content-Type', 'application/json')],
                {'username': 'newuser', 'fullname': "My Fullname", 'role': 'admin'},
            ),
            (
                'maintainer_role_as_int',
                [('Content-Type', 'application/json')],
                {'username': 'newuser', 'fullname': "My Fullname", 'role': '5'},
            ),
            (
                'maintainer_role_as_string',
                [('Content-Type', 'application/json')],
                {'username': 'newuser', 'fullname': "My Fullname", 'role': 'maintainer'},
            ),
            (
                'user_role_as_int',
                [('Content-Type', 'application/json')],
                {'username': 'newuser', 'fullname': "My Fullname", 'role': '10'},
            ),
            (
                'user_role_as_string',
                [('Content-Type', 'application/json')],
                {'username': 'newuser', 'fullname': "My Fullname", 'role': 'user'},
            ),
        ]
    )
    def test_post(self, unused, content_type, body):
        # When creating a user
        data = self.getJson(
            '/api/users',
            headers=self.auth + content_type,
            method='POST',
            body=body,
        )
        # Then user object is returned
        self.assertEqual("My Fullname", data['fullname'])
        # Then user obj is created
        self.assertTrue(UserObject.query.filter(UserObject.id == data['id']))
        # Then location of object is returned
        self.assertHeaderItemValue('Location', f'{self.baseurl}/api/users/{data["id"]}')

    def test_post_duplicate(self):
        # Given a new user
        UserObject(username='newuser', fullname='New User', email='test@example.com', lang='fr', mfa=1).add().commit()

        # When creating a user with existing username
        self.getPage(
            '/api/users',
            headers=self.auth,
            method='POST',
            body={'username': 'newuser', 'fullname': "My duplicate user"},
        )
        # Then page return error
        self.assertStatus(400)
        # Check if exception return json data.
        self.assertEqual(
            json.loads(self.body.decode('utf8')),
            {"message": "A user with this username address already exists.", "status": "400 Bad Request"},
        )

    @parameterized.expand(
        [
            ('all', True),
            ('admin_write_users', True),
            ('admin_read_users', False),
            (None, False),
        ]
    )
    def test_post_with_access_token_scope(self, scope, success):
        # Given a user with an access token
        user = UserObject.get_user('admin')
        token = user.add_access_token(name='test', scope=scope)
        user.commit()
        headers = [("Authorization", "Basic " + b64encode(f"admin:{token}".encode('ascii')).decode('ascii'))]
        # When adding a ssh key
        self.getPage(
            '/api/users',
            headers=headers,
            method='POST',
            body={'username': 'newuser', 'fullname': "My new user"},
        )
        # Then sh get added or permissions is refused
        if success:
            self.assertStatus(200)
            self.assertIsNotNone(UserObject.get_user('newuser'))
        else:
            self.assertStatus(403)
            self.assertIsNone(UserObject.get_user('newuser'))

    @parameterized.expand(
        [
            ('with_id'),
            ('with_username'),
        ]
    )
    def test_post_update(self, query):
        # Given a new user
        user_obj = (
            UserObject(username='newuser', fullname='New User', email='test@example.com', lang='fr', mfa=1)
            .add()
            .commit()
        )

        # When deleting the user
        if query == 'with_id':
            data = self.getJson(
                f'/api/users/{user_obj.id}',
                headers=self.auth,
                method='POST',
                body={'fullname': "Updated fullname"},
            )
        elif query == 'with_username':
            data = self.getJson(
                f'/api/users/{user_obj.username}',
                headers=self.auth,
                method='POST',
                body={'fullname': "Updated fullname"},
            )
        # Then user get update
        user_obj.expire()
        self.assertEqual("Updated fullname", user_obj.fullname)
        self.assertEqual("Updated fullname", data['fullname'])
