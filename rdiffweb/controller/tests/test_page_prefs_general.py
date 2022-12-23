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
Created on Dec 26, 2015

@author: Patrik Dufresne
"""

from unittest.mock import MagicMock

import cherrypy
from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.model import RepoObject, SessionObject, UserObject


class PagePrefGeneralTest(rdiffweb.test.WebCase):

    PREFS = "/prefs/general"

    login = True

    def setUp(self):
        self.listener = MagicMock()
        cherrypy.engine.subscribe('user_password_changed', self.listener.user_password_changed, priority=50)
        return super().setUp()

    def tearDown(self):
        cherrypy.engine.unsubscribe('user_password_changed', self.listener.user_password_changed)
        return super().tearDown()

    def _set_password(
        self,
        current,
        new_password,
        confirm,
    ):
        b = {
            'action': 'set_password',
            'current': current,
            'new': new_password,
            'confirm': confirm,
        }
        return self.getPage(self.PREFS, method='POST', body=b)

    def _set_profile_info(self, email, fullname=None):
        b = {
            'action': 'set_profile_info',
            'email': email,
        }
        if fullname:
            b['fullname'] = fullname
        return self.getPage(self.PREFS, method='POST', body=b)

    def test_get_page(self):
        # When querying the page
        self.getPage(self.PREFS)
        # Then the page is returned
        self.assertStatus(200)
        self.assertInBody('User profile')

    def test_change_username_noop(self):
        # Given an authenticated user
        # When updating the username
        self.getPage(
            self.PREFS,
            method='POST',
            body={'action': 'set_profile_info', 'email': 'test@test.com', 'username': 'test'},
        )
        self.assertStatus(303)
        self.getPage(self.PREFS)
        self.assertInBody("Profile updated successfully.")
        # Then database is not updated with new username.
        user = UserObject.get_user(self.USERNAME)
        self.assertIsNotNone(user)
        self.assertEqual("test@test.com", user.email)

    @parameterized.expand(
        [
            # Invalid
            ('@test.com', False),
            ('test.com', False),
            ('test@te_st.com', False),
            ('test@test.com, test2@test.com', False),
            # Valid
            ('test', True),
            ('My Fullname', True),
        ]
    )
    def test_change_fullname(self, new_fullname, expected_valid):
        # Given an authenticated user
        # When update the fullname
        self._set_profile_info("test@test.com", new_fullname)
        if expected_valid:
            self.assertStatus(303)
            self.getPage(self.PREFS)
            self.assertInBody("Profile updated successfully.")
            # Then database is updated with fullname
            self.assertInBody(new_fullname)
            user = UserObject.get_user(self.USERNAME)
            self.assertEqual(new_fullname, user.fullname)
        else:
            self.assertStatus(200)
            self.assertNotInBody("Profile updated successfully.")

    def test_change_fullname_method_get(self):
        # Given an authenticated user
        # When trying to update full name using GET method
        self.getPage(self.PREFS + '?action=set_profile_info&email=test@test.com')
        # Then nothing happen
        self.assertStatus(200)
        self.assertNotInBody("Profile updated successfully.")
        user = UserObject.get_user(self.USERNAME)
        self.assertEqual("", user.fullname)

    def test_change_fullname_too_long(self):
        # Given an authenticated user
        # When update the fullname
        self._set_profile_info("test@test.com", "Fullname" * 50)
        # Then page return with error message
        self.assertStatus(200)
        self.assertNotInBody("Profile updated successfully.")
        self.assertInBody("Fullname too long.")
        # Then database is not updated
        user = UserObject.get_user(self.USERNAME)
        self.assertEqual("", user.fullname)

    def test_change_email(self):
        self._set_profile_info("test@test.com")
        self.assertStatus(303)
        self.getPage(self.PREFS)
        self.assertInBody("Profile updated successfully.")

    @parameterized.expand(
        [
            # Invalid
            ('@test.com', False),
            ('test.com', False),
            ('test', False),
            ('test@te_st.com', False),
            ('test@test.com, test2@test.com', False),
            # Valid
            ('test@test.com', True),
        ]
    )
    def test_change_email_with_invalid_email(self, new_email, expected_valid):
        self._set_profile_info(new_email)
        if expected_valid:
            self.assertStatus(303)
            self.getPage(self.PREFS)
            self.assertInBody("Profile updated successfully.")
            self.assertNotInBody("Must be a valid email address.")
        else:
            self.assertStatus(200)
            self.assertNotInBody("Profile updated successfully.")
            self.assertInBody("Must be a valid email address.")

    def test_change_email_with_too_long(self):
        self._set_profile_info(("test1" * 50) + "@test.com")
        self.assertInBody("Email too long.")

    def test_change_password(self):
        # Given a user with 3 active sessions
        self.cookies = None
        self._login(self.USERNAME, self.PASSWORD)
        self.cookies = None
        self._login(self.USERNAME, self.PASSWORD)
        self.assertEqual(3, SessionObject.query.count())
        # When udating user's password
        self.listener.user_password_changed.reset_mock()
        self._set_password(self.PASSWORD, "pr3j5Dwi", "pr3j5Dwi")
        # Then user is redirect to same page
        self.assertStatus(303)
        # Then the page return success message.
        self.getPage(self.PREFS)
        self.assertInBody("Password updated successfully.")
        # Then a notification is raised
        self.listener.user_password_changed.assert_called_once()
        # Then all users session get deleted except our own session.
        self.assertEqual(1, SessionObject.query.count())
        self.assertEqual(self.session_id, SessionObject.query.first().id)

    def test_change_password_with_wrong_confirmation(self):
        self._set_password(self.PASSWORD, "t", "a")
        self.assertInBody("The new password and its confirmation do not match.")

    def test_change_password_with_wrong_password(self):
        self._set_password("oups", "pr3j5Dwi", "pr3j5Dwi")
        self.assertInBody("Wrong current password")

    def test_change_password_with_too_short(self):
        self._set_password(self.PASSWORD, "short", "short")
        self.assertInBody("Password must have between 8 and 128 characters.")

    def test_change_password_with_too_long(self):
        new_password = 'a' * 129
        self._set_password(self.PASSWORD, new_password, new_password)
        self.assertInBody("Password must have between 8 and 128 characters.")

    def test_change_password_with_same_value(self):
        # Given a user with a password
        self._set_password(self.PASSWORD, "pr3j5Dwi", "pr3j5Dwi")
        self.assertStatus(303)
        # When updating the pasword with the same password
        self._set_password("pr3j5Dwi", "pr3j5Dwi", "pr3j5Dwi")
        self.assertStatus(200)
        # Then an error should be displayed
        self.assertInBody("The new password must be different from the current password.")

    def test_change_password_method_get(self):
        # Given an authenticated user
        # Trying to update password with GET method
        self.getPage(self.PREFS + '?action=set_password&new=pr3j5Dwi&confirm=pr3j5Dwi&current=' + self.PASSWORD)
        # Then nothing happen
        self.assertStatus(200)
        self.assertNotInBody("Password updated successfully.")

    def test_invalid_pref(self):
        """
        Check if invalid prefs url is 404 Not Found.
        """
        self.getPage("/prefs/invalid/")
        self.assertStatus(404)

    def test_update_repos(self):
        # Given a user with invalid repositories
        userobj = UserObject.get_user(self.USERNAME)
        RepoObject(userid=userobj.userid, repopath='invalid').add().commit()
        self.assertEqual(['broker-repo', 'invalid', 'testcases'], sorted([r.name for r in userobj.repo_objs]))
        # When updating the repository list
        self.getPage(self.PREFS, method='POST', body={'action': 'update_repos'})
        self.assertStatus(200)
        # Then a success message is displayed
        self.assertInBody('Repositories successfully updated')
        # Then the list is free of inexisting repos.
        userobj.expire()
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in userobj.repo_objs]))


class PagePrefGeneralRateLimitTest(rdiffweb.test.WebCase):
    login = True

    default_config = {'rate-limit': 5}

    def test_change_password_too_many_attemps(self):
        # When udating user's password with wrong current password 5 times
        for _i in range(1, 5):
            self.getPage(
                '/prefs/general',
                method='POST',
                body={'action': 'set_password', 'current': 'wrong', 'new': 'pr3j5Dwi', 'confirm': 'pr3j5Dwi'},
            )
            self.assertStatus(200)
            self.assertInBody("Wrong current password.")
        # Then user session is cleared and user is redirect to login page
        self.getPage(
            '/prefs/general',
            method='POST',
            body={'action': 'set_password', 'current': 'wrong', 'new': 'pr3j5Dwi', 'confirm': 'pr3j5Dwi'},
        )
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/')
        # Then a warning message is displayed on login page
        self.getPage('/login/')
        self.assertStatus(200)
