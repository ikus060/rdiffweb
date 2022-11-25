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
Created on Apr 10, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import os
from unittest.case import skipIf

from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.librdiff import rdiff_backup_version
from rdiffweb.core.model import UserObject


class DeleteRepoTest(rdiffweb.test.WebCase):

    login = True

    def _delete(self, user, repo, confirm):
        body = {}
        if confirm is not None:
            body.update({'confirm': confirm})
        self.getPage("/delete/" + user + "/" + repo + "/", method="POST", body=body)

    @parameterized.expand(
        [
            ("with_dir", 'admin', '/testcases/Revisions', 'Revisions', 303, 404, '/browse/admin/testcases'),
            ("with_dir_wrong_confirmation", 'admin', '/testcases/Revisions', 'invalid', 400, 200),
            ("with_file", 'admin', '/testcases/Revisions/Data', 'Data', 303, 404, '/browse/admin/testcases/Revisions'),
            ("with_file_wrong_confirmation", 'admin', '/testcases/Revisions/Data', 'invalid', 400, 200),
            ("with_invalid", 'admin', '/testcases/invalid', 'invalid', 404, 404),
            (
                "with_broken_symlink",
                'admin',
                '/testcases/BrokenSymlink',
                'BrokenSymlink',
                303,
                404,
                '/browse/admin/testcases',
            ),
            (
                "with_utf8",
                'admin',
                '/testcases/R%C3%A9pertoire%20Existant',
                'Répertoire Existant',
                303,
                404,
                '/browse/admin/testcases',
            ),
            ("with_rdiff_backup_data", 'admin', '/testcases/rdiff-backup-data', 'rdiff-backup-data', 404, 404),
            (
                "with_quoted_path",
                'admin',
                '/testcases/Char%20%3B090%20to%20quote',
                'Char Z to quote',
                303,
                404,
                '/browse/admin/testcases',
            ),
        ]
    )
    @skipIf(rdiff_backup_version() < (2, 0, 1), "rdiff-backup-delete is available since 2.0.1")
    def test_delete_path(
        self, unused, username, path, confirmation, expected_status, expected_history_status, expected_redirect=None
    ):
        # When trying to delete a file or a folder with a confirmation
        self._delete(username, path, confirmation)
        # Then a status is returned
        self.assertStatus(expected_status)
        if expected_redirect:
            self.assertHeaderItemValue('Location', self.baseurl + expected_redirect)
        # Check filesystem
        self.wait_for_tasks()
        self.getPage("/history/" + username + "/" + path)
        self.assertStatus(expected_history_status)

    def test_delete_repo(self):
        """
        Check to delete a repo.
        """
        # Check initial list of repo
        userobj = UserObject.get_user('admin')
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in userobj.repo_objs])
        # Delete repo
        self._delete(self.USERNAME, self.REPO, 'testcases')
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/')
        # Check filesystem
        self.wait_for_tasks()
        userobj.expire()
        self.assertEqual(['broker-repo'], [r.name for r in userobj.repo_objs])
        self.assertFalse(os.path.isdir(os.path.join(self.testcases, 'testcases')))

    def test_delete_repo_with_slash(self):
        # Check initial list of repo
        userobj = UserObject.get_user('admin')
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in userobj.repo_objs])
        # Then delete it.
        self._delete(self.USERNAME, self.REPO, 'testcases')
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/')
        # Check filesystem
        self.wait_for_tasks()
        userobj.expire()
        self.assertEqual(['broker-repo'], [r.name for r in userobj.repo_objs])
        self.assertFalse(os.path.isdir(os.path.join(self.testcases, 'testcases')))

    def test_delete_repo_wrong_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        # Check initial list of repo
        userobj = UserObject.get_user('admin')
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in userobj.repo_objs])
        # Delete repo with wrong confirmation.
        self._delete(self.USERNAME, self.REPO, 'wrong')
        # TODO Make sure the repository is not delete
        userobj.expire()
        self.assertStatus(400)
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in userobj.repo_objs])

    def test_delete_repo_without_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        # Check initial list of repo
        userobj = UserObject.get_user('admin')
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in userobj.repo_objs])
        # Delete repo without confirmation.
        self._delete(self.USERNAME, self.REPO, None)
        # Make sure the repository is not delete
        self.assertStatus(400)
        self.assertInBody('Confirmation: This field is required')
        userobj.expire()
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in userobj.repo_objs])

    def test_delete_repo_as_admin(self):
        # Create a another user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in user_obj.repo_objs])

        self._delete('anotheruser', 'testcases', 'testcases')
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/')

        # Check filesystem
        self.wait_for_tasks()
        user_obj.expire()
        self.assertEqual(['broker-repo'], [r.name for r in user_obj.repo_objs])
        self.assertFalse(os.path.isdir(os.path.join(self.testcases, 'testcases')))

    def test_delete_repo_as_maintainer(self):
        self.assertTrue(os.path.isdir(self.testcases))

        # Create a another user with maintainer right
        user_obj = UserObject.add_user('maintainer', 'password')
        user_obj.user_root = self.testcases
        user_obj.role = UserObject.MAINTAINER_ROLE
        user_obj.refresh_repos()
        user_obj.commit()
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in user_obj.repo_objs])

        # Login as maintainer
        self._login('maintainer', 'password')

        # Try to delete your own repo
        self._delete('maintainer', 'testcases', 'testcases')
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/')

        # Check filesystem
        self.wait_for_tasks()
        user_obj.expire()
        self.assertEqual(['broker-repo'], [r.name for r in user_obj.repo_objs])
        self.assertFalse(os.path.isdir(os.path.join(self.testcases, 'testcases')))

    def test_delete_repo_as_user(self):
        # Create a another user with maintainer right
        user_obj = UserObject.add_user('user', 'password')
        user_obj.user_root = self.testcases
        user_obj.role = UserObject.USER_ROLE
        user_obj.refresh_repos()
        user_obj.commit()
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in user_obj.repo_objs])

        # Login as maintainer
        self._login('user', 'password')

        # Try to delete own own repo
        self._delete('user', 'testcases', 'testcases')
        self.assertStatus(403)

        # Check database don't change
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in user_obj.repo_objs])
        self.assertTrue(os.path.isdir(os.path.join(self.testcases, 'testcases')))

    def test_delete_repo_does_not_exists(self):
        # Given an invalid repo
        repo = 'invalid'
        # When trying to delete this repo
        self._delete(self.USERNAME, repo, repo)
        # Then a 404 is return to the user
        self.assertStatus(404)

    def test_delete_method_get(self):
        # Given a user with repo
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in UserObject.get_user('admin').repo_objs])
        # When trying to deleted repo with GET method
        self.getPage("/delete/" + self.USERNAME + "/" + self.REPO + "/?confirm=" + self.REPO, method="GET")
        # Then An error is returned
        self.assertStatus(405)
        # Then repo still exists
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in UserObject.get_user('admin').repo_objs])
