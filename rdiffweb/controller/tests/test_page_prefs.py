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
Created on Dec 26, 2015

@author: Patrik Dufresne
"""


import logging
import unittest

from rdiffweb.test import WebCase


class PrefsTest(WebCase):

    PREFS = "/prefs/"

    login = True

    reset_app = True
    
    reset_testcases = True

    def _set_password(self, current, new_password, confirm):
        b = {'action': 'set_password',
             'current': current,
             'new': new_password,
             'confirm': confirm}
        return self.getPage(self.PREFS, method='POST', body=b)

    def _set_profile_info(self, email):
        b = {'action': 'set_profile_info',
             'email': email}
        return self.getPage(self.PREFS, method='POST', body=b)

    def test_change_email(self):
        self._set_profile_info("test@test.com")
        self.assertInBody("Profile updated successfully.")

    def test_change_email_with_invalid_email(self):
        self._set_profile_info("@test.com")
        self.assertInBody("Invalid email")

        self._set_profile_info("test.com")
        self.assertInBody("Invalid email")

        self._set_profile_info("test")
        self.assertInBody("Invalid email")

        self._set_profile_info("test@te_st.com")
        self.assertInBody("Invalid email")

        self._set_profile_info("test@test.com, test2@test.com")
        self.assertInBody("Invalid email")

    def test_change_password(self):
        self._set_password(self.PASSWORD, "newpass", "newpass")
        self.assertInBody("Password updated successfully.")
        # Change it back
        self._set_password("newpass", self.PASSWORD, self.PASSWORD)
        self.assertInBody("Password updated successfully.")

    def test_change_password_with_wrong_confirmation(self):
        self._set_password(self.PASSWORD, "t", "a")
        self.assertInBody("The new password and its confirmation do not match.")

    def test_change_password_with_wrong_password(self):
        self._set_password("oups", "t", "t")
        self.assertInBody("Wrong password")

    def test_invalid_pref(self):
        """
        Check if invalid prefs url is 404 Not Found.
        """
        self.getPage("/prefs/invalid/")
        self.assertStatus(404)

    def test_update_repos(self):
        
        user_obj = self.app.store.get_user(self.USERNAME)
        self.app.store._database.delete('repos')
        self.assertEqual(0, len(user_obj.repos))
        
        self.getPage(self.PREFS, method='POST', body={'action': 'update_repos'})
        self.assertStatus(200)
        # Check database update.
        self.assertInBody("Repositories successfully updated.")
        
        self.assertEqual(2, len(user_obj.repos))
        self.assertIn('testcases', user_obj.repos)
        self.assertIn('broker-repo', user_obj.repos)
        
    def test_update_notification(self):
        self.getPage("/prefs/notification/", method='POST', body={'action':'set_notification_info', 'testcases':'7'})
        self.assertStatus(200)
        # Check database update
        repo_obj = self.app.store.get_user(self.USERNAME).get_repo(self.REPO)
        self.assertEqual(7, repo_obj.maxage)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
