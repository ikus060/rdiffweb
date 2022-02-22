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
Created on May 2, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

from unittest.mock import MagicMock
from rdiffweb.core.librdiff import RdiffTime

import rdiffweb.test
from rdiffweb.core.removeolder import remove_older_job
from rdiffweb.core.store import USER_ROLE


class RemoveOlderTest(rdiffweb.test.WebCase):

    login = True

    def _settings(self, user, repo):
        self.getPage("/settings/" + user + "/" + repo + "/")

    def _remove_older(self, user, repo, value):
        self.getPage("/settings/" + user + "/" + repo + "/", method="POST", body={'keepdays': value})

    def test_page_api_set_remove_older(self):
        """
        Check if /api/remove-older/ is still working.
        """
        self.getPage("/api/remove-older/" + self.USERNAME + "/" + self.REPO + "/", method="POST", body={'keepdays': '4'})
        self.assertStatus(200)
        # Check results
        user = self.app.store.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        self.assertEqual(4, repo.keepdays)

    def test_page_set_keepdays(self):
        self._remove_older(self.USERNAME, self.REPO, '1')
        self.assertStatus(200)
        # Make sure the right value is selected.
        self._settings(self.USERNAME, self.REPO)
        self.assertStatus(200)
        self.assertInBody('<option selected value="1">')
        # Also check if the value is updated in database
        user = self.app.store.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        keepdays = repo.keepdays
        self.assertEqual(1, keepdays)

    def test_remove_older(self):
        """
        Run remove older on testcases repository.
        """
        self._remove_older('admin', 'testcases', '1')
        self.assertStatus(200)
        # Get current user
        user = self.app.store.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        repo.keepdays = 30
        # Run the job.
        remove_older_job(self.app)
        # Check number of history.
        repo = user.get_repo(self.REPO)
        self.assertEqual(2, len(repo.mirror_metadata))

    def test_as_another_user(self):
        # Create a nother user with admin right
        user_obj = self.app.store.add_user('anotheruser', 'password')
        user_obj.user_root = self.app.testcases

        self._remove_older('anotheruser', 'testcases', '1')
        self.assertStatus('200 OK')
        self.assertEqual(1, user_obj.get_repo('testcases').keepdays)

        # Remove admin right
        admin = self.app.store.get_user('admin')
        admin.role = USER_ROLE

        # Browse admin's repos
        self._remove_older('anotheruser', 'testcases', '2')
        self.assertStatus('403 Forbidden')


class RemoveOlderTestWithMock(rdiffweb.test.WebCase):

    def test_remove_older_job_without_keepdays(self):
        # Given a store with repos
        repo = MagicMock()
        repo.keepdays = 0
        repo.last_backup_date = RdiffTime('2014-11-02T17:23:41-05:00')
        self.app.store.repos = MagicMock()
        self.app.store.repos.return_value = [repo]
        # When the job is running.
        remove_older_job(self.app)
        # Then remove_older function get called on the repo.
        self.app.store.repos.assert_called()
        repo.remove_older.assert_not_called()

    def test_remove_older_job_with_keepdays(self):
        # Given a store with repos
        repo = MagicMock()
        repo.keepdays = 30
        repo.last_backup_date = RdiffTime('2014-11-02T17:23:41-05:00')
        self.app.store.repos = MagicMock()
        self.app.store.repos.return_value = [repo]
        # When the job is running.
        remove_older_job(self.app)
        # Then remove_older function get called on the repo.
        self.app.store.repos.assert_called()
        repo.remove_older.assert_called()
