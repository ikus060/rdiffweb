#!/usr/bin/python
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

@author: Patrik Dufresne <info@patrikdufresne.com>
"""

from __future__ import unicode_literals

import logging
from mock import MagicMock
from rdiffweb.core import librdiff
from rdiffweb.test import WebCase
import unittest

import cherrypy

from rdiffweb.core.rdw_deamon import RemoveOlder


class RemoveOlderTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    def _settings(self, repo):
        self.getPage("/settings/" + repo + "/")

    def _remove_older(self, repo, value):
        self.getPage("/api/remove-older/" + repo + "/", method="POST",
                     body={'keepdays': value})

    def test_page_set_keepdays(self):
        """
        Set keepdays.
        """
        self._remove_older(self.REPO, '1')
        self.assertStatus(200)
        # Make sure the right value is selected.
        self._settings(self.REPO)
        self.assertInBody('<option selected value="1">')
        # Also check if the value is updated in database
        user = self.app.userdb.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        keepdays = repo.keepdays
        self.assertEqual(1, keepdays)

    def test_remove_older(self):
        """
        Run remove older on testcases repository.
        """
        self._remove_older(self.REPO, '1')
        self.assertStatus(200)
        # Get current user
        user = self.app.userdb.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        # Run the job.
        p = RemoveOlder(cherrypy.engine, self.app)
        p._remove_older(user, repo, 30)
        # Check number of history.
        r = librdiff.RdiffRepo(user.user_root, repo.name)
        self.assertEqual(2, len(r.get_history_entries()))

    def test_remove_older_with_unicode(self):
        """
        Test if exception is raised when calling _remove_oler with a keepdays
        as unicode value.
        """
        # Get current user
        user = self.app.userdb.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        # Run the job.
        with self.assertRaises(AssertionError):
            RemoveOlder(cherrypy.engine, self.app)._remove_older(user, repo, '30')


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
        # Call the job.
        p.job_run()
        # Check if _remove_older was called
        p._remove_older.assert_not_called()

    def test_job_run_with_keepdays(self):
        """
        Test execution of job run.
        """
        # Mock the call to _remove_older to make verification.
        p = RemoveOlder(cherrypy.engine, self.app)
        p._remove_older = MagicMock()
        # Set a keepdays
        user = self.app.userdb.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        repo.keepdays = 30
        # Call the job.
        p.job_run()
        # Check if _remove_older was called
        p._remove_older.assert_called_once_with(user, repo, 30)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
