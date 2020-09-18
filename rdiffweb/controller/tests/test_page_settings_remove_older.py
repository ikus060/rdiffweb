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
Created on May 2, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""


import logging
import unittest

import cherrypy
from mock import MagicMock

from rdiffweb.core.rdw_deamon import RemoveOlder
from rdiffweb.core.store import USER_ROLE
from rdiffweb.test import WebCase


class RemoveOlderTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

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
        p = RemoveOlder(cherrypy.engine, self.app)
        p._remove_older(repo)
        # Check number of history.
        repo = user.get_repo(self.REPO)
        self.assertEqual(2, len(repo.get_history_entries()))

    def test_as_another_user(self):
        # Create a nother user with admin right
        user_obj = self.app.store.add_user('anotheruser', 'password')
        user_obj.user_root = self.app.testcases
        user_obj.add_repo('testcases')

        self._remove_older('anotheruser', 'testcases', '1')
        self.assertStatus('200 OK')
        self.assertEquals(1, user_obj.get_repo('testcases').keepdays)

        # Remove admin right
        admin = self.app.store.get_user('admin')
        admin.role = USER_ROLE

        # Browse admin's repos
        self._remove_older('anotheruser', 'testcases', '2')
        self.assertStatus('403 Forbidden')


class RemoveOlderTestWithMock(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    def test_job_run_without_keepdays(self):
        """
        Test execution of job run.
        """
        # Mock the call to _remove_older to make verification.
        p = RemoveOlder(cherrypy.engine, self.app)
        p._remove_older = MagicMock()
        # Set a keepdays
        user = self.app.store.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        repo.keepdays = 0
        # Call the job.
        p.job_run()
        # Check if _remove_older was called
        p._remove_older.assert_called_once_with(repo)

    def test_job_run_with_keepdays(self):
        """
        Test execution of job run.
        """
        # Mock the call to _remove_older to make verification.
        p = RemoveOlder(cherrypy.engine, self.app)
        p._remove_older = MagicMock()
        # Set a keepdays
        user = self.app.store.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        repo.keepdays = 30
        # Call the job.
        p.job_run()
        # Check if _remove_older was called
        p._remove_older.assert_called_once_with(repo)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
