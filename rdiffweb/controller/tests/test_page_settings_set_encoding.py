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
Created on Jan 1, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""


import rdiffweb.test
from rdiffweb.core.model import RepoObject, UserObject


class SetEncodingTest(rdiffweb.test.WebCase):

    login = True

    def _settings(self, user, repo):
        self.getPage("/settings/" + user + "/" + repo + "/")

    def _set_encoding(self, user, repo, encoding):
        self.getPage("/settings/" + user + "/" + repo + "/", method="POST", body={'new_encoding': encoding})

    def test_check_default_encoding(self):
        # Default encoding for broker-repo is the default system encoding.
        self._settings('admin', 'broker-repo')
        self.assertInBody("Character encoding")
        self.assertInBody('selected value="%s"' % RepoObject.DEFAULT_REPO_ENCODING)

    def test_set_encoding(self):
        """
        Check to update the encoding with cp1252.
        """
        self._set_encoding('admin', 'testcases', 'cp1252')
        self.assertStatus(200)
        self.assertInBody("Updated")
        repo = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        self.assertEqual('cp1252', repo.encoding)
        # Get back encoding.
        self._settings('admin', 'testcases')
        self.assertInBody('selected value="cp1252"')

    def test_set_encoding_capital_case(self):
        """
        Check to update the encoding with US-ASCII.
        """
        self._set_encoding('admin', 'testcases', 'US-ASCII')
        self.assertStatus(200)
        self.assertInBody("Updated")
        repo = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        self.assertEqual('ascii', repo.encoding)
        # Get back encoding.
        self._settings('admin', 'testcases')
        self.assertInBody('selected value="ascii"')

    def test_set_encoding_invalid(self):
        """
        Check to update the encoding with invalid value.
        """
        self._set_encoding('admin', 'testcases', 'invalid')
        self.assertStatus(400)
        self.assertInBody("invalid encoding value")

    def test_set_encoding_windows_1252(self):
        """
        Check to update the encoding with windows 1252.
        """
        # Update encoding
        self._set_encoding('admin', 'testcases', 'windows_1252')
        self.assertStatus(200)
        self.assertInBody("Updated")
        # Get back encoding.
        self._settings('admin', 'testcases')
        self.assertInBody('selected value="cp1252"')
        repo = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        self.assertEqual('cp1252', repo.encoding)

    def test_as_another_user(self):
        # Create another user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()
        self._set_encoding('anotheruser', 'testcases', 'cp1252')
        self.assertStatus('200 OK')
        repo = RepoObject.query.filter(RepoObject.user == user_obj, RepoObject.repopath == self.REPO).first()
        self.assertEqual('cp1252', repo.encoding)

        # Remove admin right
        admin = UserObject.get_user('admin')
        admin.role = UserObject.USER_ROLE
        admin.commit()

        # Browse admin's repos
        self._set_encoding('anotheruser', 'testcases', 'utf-8')
        self.assertStatus('403 Forbidden')

    def test_set_encoding_method_get(self):
        # When trying to update encoding with method GET
        self.getPage("/settings/admin/testcases/?new_encoding=cp1252")
        # Then page return without error
        self.assertStatus(200)
        # Then database is not updated
        user_obj = UserObject.get_user(self.USERNAME)
        repo = RepoObject.query.filter(RepoObject.user == user_obj, RepoObject.repopath == self.REPO).first()
        self.assertEqual('utf-8', repo.encoding)
