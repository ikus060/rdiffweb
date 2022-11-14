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
Created on Dec 26, 2015

@author: Patrik Dufresne
"""

import os

import rdiffweb.test
from rdiffweb.core.model import RepoObject, UserObject


class BrowsePageTest(rdiffweb.test.WebCase):
    """Basic python call to page_browse"""

    login = True

    def tearDown(self):
        super().tearDown()

    def _browse(self, user, repo, path):
        url = "/browse/" + user + "/" + repo + "/" + path
        self.getPage(url)

    def test_locations(self):
        """
        Check page_locations
        """
        self.getPage("/")
        self.assertInBody(self.REPO)
        self.assertInBody('testcases')

    def test_locations_with_broken_tree(self):
        userobj = UserObject.get_user(self.USERNAME)
        RepoObject(userid=userobj.userid, repopath='testcases/broker-repo').add().commit()
        RepoObject(userid=userobj.userid, repopath='testcases/testcases').add().commit()
        self.getPage("/")

    def test_WithRelativePath(self):
        """
        Check if relative path are resolved.
        """
        self._browse(
            self.USERNAME,
            self.REPO,
            "../%s/Revisions/../../%s/"
            % (
                self.REPO,
                self.REPO,
            ),
        )
        self.assertInBody("")

    def test_root(self):
        """
        Browse repository root.
        """
        self._browse(self.USERNAME, self.REPO, "")
        #  Fichier @ <root>
        self.assertInBody("Fichier @ &lt;root&gt;")
        self.assertInBody("/Fichier%20%40%20%3Croot%3E?date=")
        #  Répertoire (@vec) {càraçt#èrë} $épêcial
        self.assertInBody("Répertoire (@vec) {càraçt#èrë} $épêcial")
        self.assertInBody(
            "/R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial"
        )
        #  test\test
        self.assertInBody("test\\test")
        self.assertInBody("/test%5Ctest")
        #  <F!chïer> (@vec) {càraçt#èrë} $épêcial
        self.assertInBody("&lt;F!chïer&gt; (@vec) {càraçt#èrë} $épêcial")
        self.assertInBody(
            "/%3CF%21ch%C3%AFer%3E%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial?date="
        )
        #  Répertoire Existant
        self.assertInBody("Répertoire Existant")
        self.assertInBody("/R%C3%A9pertoire%20Existant")
        #  Répertoire Supprimé
        self.assertInBody("Répertoire Supprimé")
        self.assertInBody("/R%C3%A9pertoire%20Supprim%C3%A9")
        #  Quoted folder
        self.assertInBody("Char Z to quote")
        self.assertInBody("/Char%20%3B090%20to%20quote")
        #  Invalid encoding
        self.assertInBody("Fichier avec non asci char �velyne M�re.txt")
        self.assertInBody("/Fichier%20avec%20non%20asci%20char%20%C9velyne%20M%E8re.txt")
        #  Make sure "rdiff-backup-data" is not listed
        self.assertNotInBody("rdiff-backup-data")

    def test_loop_symlink(self):
        """
        Browse a symlink.
        """
        self._browse(self.USERNAME, self.REPO, "Subdirectory/LoopSymlink")
        self.assertStatus(200)
        self.assertInBody("LoopSymlink")
        self.assertInBody("Foldèr with éncodïng")
        self._browse(self.USERNAME, self.REPO, "Subdirectory/LoopSymlink/LoopSymlink/")
        self.assertStatus(200)
        self.assertInBody("LoopSymlink")
        self.assertInBody("Foldèr with éncodïng")
        self._browse(self.USERNAME, self.REPO, "Subdirectory/LoopSymlink/LoopSymlink/LoopSymlink")
        self.assertStatus(200)
        self.assertInBody("LoopSymlink")
        self.assertInBody("Foldèr with éncodïng")

    def test_subdir_symlink(self):
        self._browse(self.USERNAME, self.REPO, "SymlinkToSubdirectory")
        self.assertStatus(200)
        self.assertInBody("LoopSymlink")
        self.assertInBody("Foldèr with éncodïng")
        self._browse(self.USERNAME, self.REPO, "SymlinkToSubdirectory/LoopSymlink")
        self.assertStatus(200)
        self.assertInBody("LoopSymlink")
        self.assertInBody("Foldèr with éncodïng")

    def test_sub_directory_deleted(self):
        """
        Browse to a sub directory being deleted.
        """
        self._browse(self.USERNAME, self.REPO, "R%C3%A9pertoire%20Supprim%C3%A9/")
        self.assertStatus(200)
        self.assertInBody("Untitled Empty Text File")
        self.assertInBody("Untitled Empty Text File 2")
        self.assertInBody("Untitled Empty Text File 3")
        #  Also check if the filesize are properly retrieve.
        self.assertInBody(
            "The size of deleted files is available in the file history using the `Show more...` function."
        )
        #  Also check dates
        self.assertInBody("data-order=\"1414871475\"")

    def test_sub_directory_exists(self):
        """
        Browse to a sub directory.
        """
        self._browse(self.USERNAME, self.REPO, "R%C3%A9pertoire%20Existant/")
        self.assertStatus(200)
        self.assertInBody("Fichier supprimé")
        self.assertInBody("Untitled Empty Text File")
        self.assertInBody("Untitled Empty Text File 2")

    def test_sub_directory_with_special_chars(self):
        """
        Browse to a sub directory containing special chars.
        """
        self._browse(
            self.USERNAME,
            self.REPO,
            "R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial/",
        )
        self.assertStatus(200)
        self.assertInBody("Untitled Testcase.doc")

    def test_sub_directory_with_encoding(self):
        """
        Browse to sub directory with non-ascii.
        """
        self._browse(self.USERNAME, self.REPO, "R%C3%A9pertoire%20Existant/")
        self.assertStatus(200)
        self.assertInBody("Répertoire Existant")

    def test_quoted_path(self):
        """
        Browse to a directory with quoted path ';090'.
        """
        #  Char ;090 to quote
        #  Char Z to quote
        self._browse(self.USERNAME, self.REPO, "Char%20%3B090%20to%20quote/")
        self.assertStatus(200)
        #  browser location
        self.assertInBody("Char Z to quote")
        #  Content of the folder
        self.assertInBody("Untitled Testcase.doc")
        self.assertInBody("Data")
        #  Check size
        self.assertInBody(
            "The size of deleted files is available in the file history using the `Show more...` function."
        )

    def test_invalid_repo(self):
        """
        Browse to an invalid repository.
        """
        self.getPage('/browse/invalid')
        self.assertStatus(404)

        self.getPage('/browse/invalid/')
        self.assertStatus(404)

        self.getPage('/browse/admin/invalid/')
        self.assertStatus(404)

    def test_invalid_path(self):
        """
        Browse to an invalid path.
        """
        self._browse(self.USERNAME, self.REPO, "invalid/")
        self.assertStatus(404)

    def test_with_rdiffbackupdata(self):
        """
        Verify if rdiff-backup-data is not accessible.
        """
        self._browse(self.USERNAME, self.REPO, "rdiff-backup-data/")
        self.assertStatus(404)

    def test_with_single_repo(self):
        """
        Verify if browsing '/browse/' for a single repository is working.
        """
        # Change the user setting to match single repo.
        user = UserObject.get_user(self.USERNAME)
        user.user_root = os.path.join(self.testcases, 'testcases')
        user.refresh_repos()
        user.commit()
        self.assertEqual(['', 'broker-repo', 'testcases'], [r.name for r in user.repo_objs])
        # Check if listing locations is working
        self.getPage('/')
        self.assertStatus('200 OK')
        self.assertInBody('testcases')
        # Check if browsing is working.
        self.getPage('/browse/admin')
        self.assertStatus('200 OK')
        self.assertInBody('Files')
        # Check sub directory browsing
        self.getPage('/browse/admin/Revisions/')
        self.assertStatus('200 OK')
        self.assertInBody('Files')

    def test_browse_with_permissions(self):
        # Create an another user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()
        self.getPage('/browse/admin')
        self.assertStatus('404 Not Found')

        # Browse other user's repos
        self.getPage('/browse/anotheruser')
        self.assertStatus('404 Not Found')
        self.getPage('/browse/anotheruser/testcases')
        self.assertStatus('200 OK')
        self.getPage('/browse/anotheruser/testcases/Revisions/')
        self.assertStatus('200 OK')

    def test_browse_without_permissions(self):
        # Remove admin role.
        admin = UserObject.get_user('admin')
        admin.role = UserObject.USER_ROLE
        admin.refresh_repos()
        admin.commit()

        # Browse other user's repos
        self.getPage('/browse/anotheruser/testcases')
        self.assertStatus('403 Forbidden')
        self.getPage('/browse/anotheruser/testcases/Revisions/')
        self.assertStatus('403 Forbidden')

    def test_browser_with_failed_repo(self):
        # Given a failed repo
        admin = UserObject.get_user('admin')
        admin.user_root = 'invalid'
        admin.commit()
        # When querying the logs
        self._browse(self.USERNAME, self.REPO, '')
        # Then the page is return with an error message
        self.assertStatus(200)
        self.assertInBody('The repository cannot be found or is badly damaged.')
