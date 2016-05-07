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
        self.getPage("/remove-older/" + repo + "/", method="POST",
                     body={'keepdays': value})

    # FIXME This testcases doesn't work for unknown reason.
    # def test_check_delete(self):
    #    self._settings(self.REPO)
    #    self.assertInBody("Delete")

    def test_remove_older(self):
        """
        Check to delete a repo.
        """
        self._remove_older(self.REPO, '1')
        self.assertStatus(200)
        # Make sure the right value is selected.
        self._settings(self.REPO)
        self.assertInBody('<option selected value="1">')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
