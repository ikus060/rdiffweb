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
Created on Apr 10, 2016

@author: Patrik Dufresne <info@patrikdufresne.com>
"""
from __future__ import unicode_literals

import logging
import unittest

from rdiffweb.test import WebCase


class DeleteRepoTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    def _settings(self, repo):
        self.getPage("/settings/" + repo + "/")

    def _delete(self, repo, confirm_name):
        body = {}
        if confirm_name is not None:
            body.update({'confirm_name': confirm_name})
        self.getPage("/delete/" + repo + "/", method="POST",
                     body=body)

    # FIXME This testcases doesn't work for unknown reason.
    # def test_check_delete(self):
    #    self._settings(self.REPO)
    #    self.assertInBody("Delete")

    def test_delete(self):
        """
        Check to delete a repo.
        """
        self._delete(self.REPO, self.REPO)
        self.assertStatus(303)

    def test_delete_wrong_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        self._delete(self.REPO, 'wrong')
        # TODO Make sure the repository is not delete
        self.assertStatus(400)

    def test_delete_without_confirm(self):
        """
        Check failure to delete a repo with wrong confirmation.
        """
        self._delete(self.REPO, None)
        # TODO Make sure the repository is not delete
        self.assertStatus(400)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
