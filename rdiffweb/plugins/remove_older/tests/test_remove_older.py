#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

@author: ikus060
"""

from __future__ import unicode_literals

import logging
import unittest

from rdiffweb import librdiff
from rdiffweb.test import WebCase


class RemoveOlderTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    @classmethod
    def setup_server(cls):
        WebCase.setup_server(enabled_plugins=['SQLite', 'RemoveOlder'])

    def _settings(self, repo):
        self.getPage("/settings/" + repo + "/")

    def _remove_older(self, repo, value):
        self.getPage("/ajax/remove-older/" + repo + "/", method="POST",
                     body={'keepdays': value})

    def test_page_set_keepdays(self):
        """
        Check to delete a repo.
        """
        self._remove_older(self.REPO, '1')
        self.assertStatus(200)
        # Make sure the right value is selected.
        self._settings(self.REPO)
        self.assertInBody('<option selected value="1">')

    def test_remove_older(self):
        """
        Run remove older on testcases repository.
        """
        # Set keep one day.
        self._remove_older(self.REPO, '1')
        self.assertStatus(200)
        # Get current user
        user = self.app.userdb.get_user(self.USERNAME)
        repo = user.get_repo(self.REPO)
        # Run the job.
        p = self.app.plugins.get_plugin_by_name('RemoveOlderPlugin')
        p._remove_older(user, repo, 30)
        # Check number of history.
        r = librdiff.RdiffRepo(user.user_root, repo.name)
        self.assertEqual(2, len(r.get_history_entries()))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
