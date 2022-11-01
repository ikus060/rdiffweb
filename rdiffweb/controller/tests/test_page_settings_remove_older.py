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


import rdiffweb.test
from rdiffweb.core.model import RepoObject, UserObject


class RemoveOlderTest(rdiffweb.test.WebCase):

    login = True

    def _settings(self, user, repo):
        self.getPage("/settings/" + user + "/" + repo + "/")

    def _remove_older(self, user, repo, value):
        self.getPage("/settings/" + user + "/" + repo + "/", method="POST", body={'keepdays': value})

    def test_page_set_keepdays(self):
        self._remove_older(self.USERNAME, self.REPO, '1')
        self.assertStatus(200)
        # Make sure the right value is selected.
        self._settings(self.USERNAME, self.REPO)
        self.assertStatus(200)
        self.assertInBody('<option selected value="1">')
        # Also check if the value is updated in database
        repo = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        keepdays = repo.keepdays
        self.assertEqual(1, keepdays)

    def test_as_another_user(self):
        # Create another user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()
        self._remove_older('anotheruser', 'testcases', '1')
        self.assertStatus('200 OK')
        repo = RepoObject.query.filter(RepoObject.user == user_obj, RepoObject.repopath == self.REPO).first()
        self.assertEqual(1, repo.keepdays)

        # Remove admin right
        admin = UserObject.get_user('admin')
        admin.role = UserObject.USER_ROLE
        admin.commit()

        # Browse admin's repos
        self._remove_older('anotheruser', 'testcases', '2')
        self.assertStatus('403 Forbidden')

    def test_set_keepdays_method_get(self):
        # When trying update keepdays with method GET
        self.getPage("/settings/" + self.USERNAME + "/" + self.REPO + "/?keepdays=4")
        # Then pge return without error
        self.assertStatus(200)
        # Then database is not updated
        user_obj = UserObject.get_user(self.USERNAME)
        repo = RepoObject.query.filter(RepoObject.user == user_obj, RepoObject.repopath == self.REPO).first()
        self.assertEqual(-1, repo.keepdays)
