# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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

from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.model import RepoObject, UserObject
from rdiffweb.core.rdw_templating import url_for

_matrix = [
    (
        'root',
        '',
        [
            "Fichier @ <root>",
            "Répertoire (@vec) {càraçt#èrë} $épêcial",
            "test\\test",
            "<F!chïer> (@vec) {càraçt#èrë} $épêcial",
            "Répertoire Existant",
            "Répertoire Supprimé",
            "Char Z to quote",
            "Fichier avec non asci char �velyne M�re.txt",
        ],
    ),
    ('loop_symlink', 'Subdirectory/LoopSymlink', ['LoopSymlink', 'Foldèr with éncodïng']),
    ('loop_loop_symlink', 'Subdirectory/LoopSymlink/LoopSymlink/', ['LoopSymlink', 'Foldèr with éncodïng']),
    (
        'loop_loop_symlink',
        'Subdirectory/LoopSymlink/LoopSymlink/LoopSymlink/',
        ['LoopSymlink', 'Foldèr with éncodïng'],
    ),
    (
        'subdir_symlink',
        'SymlinkToSubdirectory/LoopSymlink',
        [
            'LoopSymlink',
            'Foldèr with éncodïng',
        ],
    ),
    (
        'sub_directory_deleted',
        'R%C3%A9pertoire%20Supprim%C3%A9/',
        [
            'Untitled Empty Text File',
            'Untitled Empty Text File 2',
            'Untitled Empty Text File 3',
        ],
    ),
    (
        'sub_directory_exists',
        'R%C3%A9pertoire%20Existant/',
        [
            'Fichier supprim',
            'Untitled Empty Text File',
            'Untitled Empty Text File 2',
        ],
    ),
    (
        'sub_directory_with_special_chars',
        'R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial/',
        [
            'Untitled Testcase.doc',
        ],
    ),
    (
        'quoted_path',
        'Char%20%3B090%20to%20quote/',
        [
            'Untitled Testcase.doc',
            'Data',
        ],
    ),
]


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

    @parameterized.expand(_matrix)
    def test_browse(self, unused, path, expected_in_body):
        # Given a repository
        # When brwosing the path
        self.getPage(url_for('browse', self.USERNAME, self.REPO, path))
        # Then page return without error
        self.assertStatus(200)
        # Then is contains our expected data
        for value in expected_in_body:
            self.assertInBody(value.replace('<', '&lt;').replace('>', '&gt;'))

    @parameterized.expand(_matrix)
    def test_browse_with_selenim(self, unused, path, expected_in_body):
        """
        Browse repository root.
        """
        # Given a repository
        with self.selenium() as driver:
            # When browsing repository
            driver.get(url_for('browse', self.USERNAME, self.REPO, path))
            # Then page load without error
            self.assertFalse(driver.get_log('browser'))
            # Then page contains expected strings.
            text = driver.find_element('css selector', "#table1").text
            for value in expected_in_body:
                self.assertIn(value, text)

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

    def test_browse_with_failed_repo(self):
        # Given a failed repo
        admin = UserObject.get_user('admin')
        admin.user_root = 'invalid'
        admin.commit()
        # When querying the logs
        self._browse(self.USERNAME, self.REPO, '')
        # Then the page is return with an error message
        self.assertStatus(200)
        self.assertInBody('The repository cannot be found or is badly damaged.')
        self.assertInBody('The displayed data may be inconsistent')

    def test_browse_with_interupted_repo(self):
        # Given a failed repo
        # When querying the repo
        self._browse(self.USERNAME, 'broker-repo', '')
        # Then the page is return with an error message
        self.assertStatus(200)
        self.assertInBody('Initial backup in progress.')
        self.assertInBody('The displayed data may be inconsistent')
