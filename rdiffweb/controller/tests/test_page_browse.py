#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 Patrik Dufresne Service Logiciel
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
Created on Dec 26, 2015

@author: Patrik Dufresne
"""

from __future__ import unicode_literals

import logging
import os
import unittest

from rdiffweb.test import WebCase


class BrowsePageTest(WebCase):
    """Basic python call to page_browse"""

    reset_app = True

    reset_testcases = True

    login = True

    def tearDown(self):
        WebCase.tearDown(self)

    def _browse(self, repo, path, restore=False):
        url = "/browse/" + repo + "/" + path
        if restore:
            url = url + "?restore=T"
        self.getPage(url)

    def test_locations(self):
        """
        Check page_locations
        """
        self.getPage("/")
        self.assertInBody(self.REPO)
        self.assertInBody('<meta itemprop="name" content="testcases" />')

    def test_WithRelativePath(self):
        """
        Check if relative path are resolved.
        """
        self._browse(self.REPO, "../%s/Revisions/../../%s/" % (self.REPO, self.REPO,))
        self.assertInBody("")

    def test_root(self):
        """
        Browse repository root.
        """
        self._browse(self.REPO, "")
        #  Fichier @ <root>
        self.assertInBody("Fichier @ &lt;root&gt;")
        self.assertInBody("/Fichier%20%40%20%3Croot%3E?date=")
        #  Répertoire (@vec) {càraçt#èrë} $épêcial
        self.assertInBody("Répertoire (@vec) {càraçt#èrë} $épêcial")
        self.assertInBody("/R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial/")
        #  test\test
        self.assertInBody("test\\test")
        self.assertInBody("/test%5Ctest/")
        #  <F!chïer> (@vec) {càraçt#èrë} $épêcial
        self.assertInBody("&lt;F!chïer&gt; (@vec) {càraçt#èrë} $épêcial")
        self.assertInBody("/%3CF%21ch%C3%AFer%3E%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial?date=")
        #  Répertoire Existant
        self.assertInBody("Répertoire Existant")
        self.assertInBody("/R%C3%A9pertoire%20Existant/")
        #  Répertoire Supprimé
        self.assertInBody("Répertoire Supprimé")
        self.assertInBody("/R%C3%A9pertoire%20Supprim%C3%A9/")
        #  Quoted folder
        self.assertInBody("Char Z to quote")
        self.assertInBody("/Char%20%3B090%20to%20quote")
        #  Invalid encoding
        self.assertInBody("Fichier avec non asci char �velyne M�re.txt")
        self.assertInBody("/Fichier%20avec%20non%20asci%20char%20%C9velyne%20M%E8re.txt")
        #  Make sure "rdiff-backup-data" is not listed
        self.assertNotInBody("rdiff-backup-data")

    def test_root_restore(self):
        """
        Browse root restore page.
        """
        self._browse(self.REPO, "", True)
        self.assertInBody("Download")
        self.assertInBody("2016-02-02 16:30")
        self.assertInBody("/restore/" + self.REPO + "?date=1415221507")
        self.assertInBody("Show more")

    def test_sub_directory_deleted(self):
        """
        Browse to a sub directory being deleted.
        """
        self._browse(self.REPO, "R%C3%A9pertoire%20Supprim%C3%A9/")
        self.assertInBody("Untitled Empty Text File")
        self.assertInBody("Untitled Empty Text File 2")
        self.assertInBody("Untitled Empty Text File 3")
        #  Also check if the filesize are properly retrieve.
        self.assertInBody("21 Bytes")
        self.assertInBody("14 Bytes")
        self.assertInBody("0 Bytes")
        #  Also check dates
        self.assertInBody("data-value=\"1414871475\"")

    def test_sub_directory_deleted_restore(self):
        """
        Browse to restore page of a deleted directory.
        """
        self._browse(self.REPO, "R%C3%A9pertoire%20Supprim%C3%A9/", True)
        self.assertInBody("Download")
        self.assertInBody("ZIP")
        self.assertInBody("TAR.GZ")
        self.assertInBody("2014-11-01 15:51")
        self.assertInBody("/restore/" + self.REPO + "/R%C3%A9pertoire%20Supprim%C3%A9?date=1414871475")

    def test_sub_directory_exists(self):
        """
        Browse to a sub directory.
        """
        self._browse(self.REPO, "R%C3%A9pertoire%20Existant/")
        self.assertInBody("Fichier supprimé")
        self.assertInBody("Untitled Empty Text File")
        self.assertInBody("Untitled Empty Text File 2")

    def test_sub_directory_with_special_chars(self):
        """
        Browse to a sub directory containing special chars.
        """
        self._browse(self.REPO, "R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial/")
        self.assertInBody("Untitled Testcase.doc")

    def test_sub_directory_with_special_chars_restore(self):
        """
        Browse to restore page of a sub directory containing special chars.
        """
        self._browse(self.REPO, "R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial/", True)
        self.assertInBody("Download")
        self.assertInBody("ZIP")
        self.assertInBody("TAR.GZ")
        self.assertInBody("2016-02-02 16:30")

    def test_sub_directory_with_encoding(self):
        """
        Browse to sub directory with non-ascii.
        """
        self._browse(self.REPO, "R%C3%A9pertoire%20Existant/")
        self.assertInBody("Répertoire Existant")

    def test_quoted_path(self):
        """
        Browse to a directory with quoted path ';090'.
        """
        #  Char ;090 to quote
        #  Char Z to quote
        self._browse(self.REPO, "Char%20%3B090%20to%20quote/")
        #  browser location
        self.assertInBody("Char Z to quote")
        #  Content of the folder
        self.assertInBody("Untitled Testcase.doc")
        self.assertInBody("Data")
        #  Check size
        self.assertInBody("21 Bytes")
        self.assertInBody("14.5 KiB")

    def test_invalid_repo(self):
        """
        Browse to an invalid repository.
        """
        self._browse("/invalid/", "")
        self.assertStatus(404)
        self.assertInBody("Not Found")

        self._browse("invalid/", "")
        self.assertStatus(404)
        self.assertInBody("Not Found")

    def test_invalid_path(self):
        """
        Browse to an invalid path.
        """
        self._browse(self.REPO, "invalid/")
        self.assertStatus(404)

    def test_with_rdiffbackupdata(self):
        """
        Verify if rdiff-backup-data is not accessible.
        """
        self._browse(self.REPO, "rdiff-backup-data/")
        self.assertStatus(404)
        self.assertInBody("Not Found")

    def test_with_single_repo(self):
        """
        Verify if browsing '/browse/' for a single repository is working.
        """
        # Change the user setting to match single repo.
        user = self.app.userdb.get_user(self.USERNAME)
        user.user_root = os.path.join(self.app.testcases, self.REPO)
        user.repos = ['']
        # Check if listing locations is working
        self.getPage('/')
        self.assertStatus('200 OK')
        self.assertInBody(self.REPO)
        # Check if browsing is working.
        self.getPage('/browse/')
        self.assertStatus('200 OK')
        self.assertInBody('Files')
        # Check sub directory browsing
        self.getPage('/browse/Revisions/')
        self.assertStatus('200 OK')
        self.assertInBody('Files')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
