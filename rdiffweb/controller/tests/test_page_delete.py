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
import os
from time import sleep
import unittest
from unittest.case import skipIf

from rdiffweb.core.librdiff import DoesNotExistError, rdiff_backup_version
from rdiffweb.core.store import MAINTAINER_ROLE, USER_ROLE
from rdiffweb.test import WebCase


RDIFF_BACKUP_VERSION = rdiff_backup_version()


class DeleteRepoTest(WebCase):

    login = True

    def _delete(self, user, repo, confirm, **kwargs):
        body = {}
        if confirm is not None:
            body.update({'confirm': confirm})
        if kwargs:
            body.update(kwargs)
        self.getPage("/delete/" + user + "/" + repo + "/", method="POST", body=body)

    @skipIf(RDIFF_BACKUP_VERSION < (2, 0, 1), "rdiff-backup-delete is available since 2.0.1")
    def test_delete_path(self):
        """
        Check to delete a directory.
        """
        # Check directory exists
        admin = self.app.store.get_user('admin')
        self.app.store.get_repo_path('admin/testcases/Revisions', as_user=admin)
        # Delete directory
        self._delete(self.USERNAME, 'testcases/Revisions', 'Revisions')
        self.assertStatus(303)
        # Check filesystem
        sleep(1)
        with self.assertRaises(DoesNotExistError):
            self.app.store.get_repo_path('admin/testcases/Revisions', as_user=admin)

    @skipIf(RDIFF_BACKUP_VERSION < (2, 0, 1), "rdiff-backup-delete is available since 2.0.1")
    def test_delete_path_with_wrong_confirm(self):
        # Check directory exists
        admin = self.app.store.get_user('admin')
        self.app.store.get_repo_path('admin/testcases/Revisions', as_user=admin)
        # Delete directory
        self._delete(self.USERNAME, 'testcases/Revisions', 'invalid')
        self.assertStatus(400)
        # Check filesystem
        sleep(1)
        self.app.store.get_repo_path('admin/testcases/Revisions', as_user=admin)

    def test_delete_repo(self):
        """
        Check to delete a repo.
        """
        self._delete(self.USERNAME, self.REPO, 'testcases')
        self.assertStatus(303)
        # Check filesystem
        sleep(1)
        self.assertEqual([], self.app.store.get_user('admin').repos)
        self.assertFalse(os.path.isdir(os.path.join(self.app.testcases, 'testcases')))

    def test_delete_repo_with_slash(self):
        # Make sure the repo exists.
        self.assertEqual(['testcases'], self.app.store.get_user('admin').repos)
        # Then delete it.
        self._delete(self.USERNAME, self.REPO, 'testcases')
        self.assertStatus(303)
        self.assertEqual([], self.app.store.get_user('admin').repos)
        # Check filesystem
        sleep(1)
        self.assertFalse(os.path.isdir(os.path.join(self.app.testcases, 'testcases')))

    def test_delete_repo_wrong_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        self._delete(self.USERNAME, self.REPO, 'wrong')
        # TODO Make sure the repository is not delete
        self.assertStatus(400)
        self.assertEqual(['testcases'], self.app.store.get_user('admin').repos)

    def test_delete_repo_without_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        self._delete(self.USERNAME, self.REPO, None)
        # TODO Make sure the repository is not delete
        self.assertStatus(400)
        self.assertEqual(['testcases'], self.app.store.get_user('admin').repos)

    def test_delete_repo_as_admin(self):
        # Create a another user with admin right
        user_obj = self.app.store.add_user('anotheruser', 'password')
        user_obj.user_root = self.app.testcases
        user_obj.add_repo('testcases')

        self._delete('anotheruser', 'testcases', 'testcases', redirect='/admin/repos/')
        self.assertStatus(303)
        location = self.assertHeader('Location')
        self.assertTrue(location.endswith('/admin/repos/'))

        # Check filesystem
        sleep(1)
        self.assertEqual([], user_obj.repos)
        self.assertFalse(os.path.isdir(os.path.join(self.app.testcases, 'testcases')))

    def test_delete_repo_as_maintainer(self):
        self.assertTrue(os.path.isdir(self.app.testcases))

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

        # Check filesystem
        sleep(1)
        self.assertEqual([], user_obj.repos)
        self.assertFalse(os.path.isdir(os.path.join(self.app.testcases, 'testcases')))

    def test_delete_repo_as_user(self):
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

        # Check database don't change
        self.assertEqual(['testcases'], user_obj.repos)
        self.assertTrue(os.path.isdir(os.path.join(self.app.testcases, 'testcases')))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
