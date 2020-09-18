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
Created on Apr 10, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import logging
import unittest

from rdiffweb.core.store import MAINTAINER_ROLE, USER_ROLE
from rdiffweb.test import WebCase


class DeleteRepoTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    def _settings(self, repo):
        self.getPage("/settings/" + repo + "/")

    def _delete(self, user, repo, confirm, **kwargs):
        body = {}
        body.update({'action': 'delete'})
        if confirm is not None:
            body.update({'confirm': confirm})
        if kwargs:
            body.update(kwargs)
        self.getPage("/settings/" + user + "/" + repo + "/", method="POST", body=body)

    def test_delete(self):
        """
        Check to delete a repo.
        """
        self._delete(self.USERNAME, self.REPO, 'testcases')
        self.assertStatus(303)
        self.assertEqual([], self.app.store.get_user('admin').repos)

    def test_delete_with_slash(self):
        # Make sure the repo exists.
        self.assertEqual(['testcases'], self.app.store.get_user('admin').repos)
        # Then delete it.
        self._delete(self.USERNAME, self.REPO, 'testcases')
        self.assertStatus(303)
        self.assertEqual([], self.app.store.get_user('admin').repos)

    def test_delete_wrong_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        self._delete(self.USERNAME, self.REPO, 'wrong')
        # TODO Make sure the repository is not delete
        self.assertStatus(400)
        self.assertEqual(['testcases'], self.app.store.get_user('admin').repos)

    def test_delete_without_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        self._delete(self.USERNAME, self.REPO, None)
        # TODO Make sure the repository is not delete
        self.assertStatus(400)
        self.assertEqual(['testcases'], self.app.store.get_user('admin').repos)

    def test_delete_as_admin(self):
        # Create a another user with admin right
        user_obj = self.app.store.add_user('anotheruser', 'password')
        user_obj.user_root = self.app.testcases
        user_obj.add_repo('testcases')

        self._delete('anotheruser', 'testcases', 'testcases', redirect='/admin/repos/')
        self.assertStatus(303)
        location = self.assertHeader('Location')
        self.assertTrue(location.endswith('/admin/repos/'))

        # Check database update
        self.assertEqual([], user_obj.repos)

    def test_delete_as_maintainer(self):
        # Create a another user with maintainer right
        user_obj = self.app.store.add_user('maintainer', 'password')
        user_obj.user_root = self.app.testcases
        user_obj.add_repo('testcases')
        user_obj.role = MAINTAINER_ROLE
        
        # Login as maintainer
        self._login('maintainer', 'password')
        
        # Try to delete own own repo
        self._delete('maintainer', 'testcases', 'testcases', redirect='/admin/repos/')
        self.assertStatus(303)
        location = self.assertHeader('Location')
        self.assertTrue(location.endswith('/admin/repos/'))

        # Check database update
        self.assertEqual([], user_obj.repos)

    def test_delete_as_user(self):
        # Create a another user with maintainer right
        user_obj = self.app.store.add_user('user', 'password')
        user_obj.user_root = self.app.testcases
        user_obj.add_repo('testcases')
        user_obj.role = USER_ROLE

        # Login as maintainer
        self._login('user', 'password')
        
        # Try to delete own own repo
        self._delete('user', 'testcases', 'testcases', redirect='/admin/repos/')
        self.assertStatus(403)

        # Check database update
        self.assertEqual(['testcases'], user_obj.repos)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
