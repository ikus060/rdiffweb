# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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
Created on Jan 1, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""


import logging
import unittest

from rdiffweb.core.store import DEFAULT_REPO_ENCODING, USER_ROLE
from rdiffweb.test import WebCase


class SetEncodingTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    def _settings(self, user, repo):
        self.getPage("/settings/" + user + "/" + repo + "/")

    def _set_encoding(self, user, repo, encoding):
        self.getPage("/settings/" + user + "/" + repo + "/", method="POST",
                     body={'new_encoding': encoding})

    def test_check_default_encoding(self):
        # Default encoding for testcases is utf-8 because 'rdiffweb' file enforce the value.
        self._settings('admin', 'testcases')
        self.assertInBody("Character encoding")
        self.assertInBody('selected value="utf-8"')
        # Default encoding for broker-repo is the default system encoding.
        user = self.app.store.get_user(self.USERNAME)
        user.add_repo('broker-repo')
        self._settings('admin', 'broker-repo')
        self.assertInBody("Character encoding")
        self.assertInBody('selected value="%s"' % DEFAULT_REPO_ENCODING)

    def test_api_set_encoding(self):
        """
        Check if /api/set-encoding/ is still working.
        """
        self.getPage("/api/set-encoding/admin/testcases/", method="POST", body={'new_encoding': 'cp1252'})
        self.assertStatus(200)
        # Check results
        user = self.app.store.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        self.assertEqual('cp1252', repo.encoding)

    def test_set_encoding(self):
        """
        Check to update the encoding with cp1252.
        """
        self._set_encoding('admin', 'testcases', 'cp1252')
        self.assertStatus(200)
        self.assertInBody("Updated")
        self.assertEquals('cp1252', self.app.store.get_user(self.USERNAME).get_repo(self.REPO).encoding)
        # Get back encoding.
        self._settings('admin', 'testcases')
        self.assertInBody('selected value="cp1252"')

    def test_set_encoding_capital_case(self):
        """
        Check to update the encoding with US-ASCII.
        """
        self._set_encoding('admin', 'testcases', 'US-ASCII')
        self.assertStatus(200)
        self.assertInBody("Updated")
        self.assertEquals('ascii', self.app.store.get_user(self.USERNAME).get_repo(self.REPO).encoding)
        # Get back encoding.
        self._settings('admin', 'testcases')
        self.assertInBody('selected value="ascii"')

    def test_set_encoding_invalid(self):
        """
        Check to update the encoding with invalid value.
        """
        self._set_encoding('admin', 'testcases', 'invalid')
        self.assertStatus(400)
        self.assertInBody("invalid encoding value")

    def test_set_encoding_windows_1252(self):
        """
        Check to update the encoding with windows 1252.
        """
        # Update encoding
        self._set_encoding('admin', 'testcases', 'windows_1252')
        self.assertStatus(200)
        self.assertInBody("Updated")
        # Get back encoding.
        self._settings('admin', 'testcases')
        self.assertInBody('selected value="cp1252"')
        self.assertEquals('cp1252', self.app.store.get_user(self.USERNAME).get_repo(self.REPO).encoding)

    def test_as_another_user(self):
        # Create a nother user with admin right
        user_obj = self.app.store.add_user('anotheruser', 'password')
        user_obj.user_root = self.app.testcases
        user_obj.add_repo('testcases')

        self._set_encoding('anotheruser', 'testcases', 'cp1252')
        self.assertStatus('200 OK')
        self.assertEquals('cp1252', user_obj.get_repo('testcases').encoding)

        # Remove admin right
        admin = self.app.store.get_user('admin')
        admin.role = USER_ROLE

        # Browse admin's repos
        self._set_encoding('anotheruser', 'testcases', 'utf-8')
        self.assertStatus('403 Forbidden')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
