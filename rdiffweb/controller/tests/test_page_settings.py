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


class SettingsTest(rdiffweb.test.WebCase):

    login = True

    def test_page(self):
        self.getPage("/settings/" + self.USERNAME + "/" + self.REPO)
        self.assertInBody("Character encoding")
        self.assertStatus(200)

    def test_as_another_user(self):
        # Create a nother user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()
        self.getPage("/settings/anotheruser/testcases")
        self.assertInBody("Character encoding")
        self.assertStatus('200 OK')

        # Remove admin right
        admin = UserObject.get_user('admin')
        admin.role = UserObject.USER_ROLE
        admin.commit()

        # Browse admin's repos
        self.getPage("/settings/anotheruser/testcases")
        self.assertStatus('403 Forbidden')

    def test_set_maxage(self):
        self.getPage("/settings/" + self.USERNAME + "/" + self.REPO + "/", method="POST", body={'maxage': '4'})
        self.assertStatus(200)
        # Check database update
        repo_obj = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        self.assertEqual(4, repo_obj.maxage)

    def test_set_maxage_method_get(self):
        # When trying to update maxage with GET method
        self.getPage("/settings/" + self.USERNAME + "/" + self.REPO + "/?maxage=4")
        # Then page return without error
        self.assertStatus(200)
        # Then database is not updated
        repo_obj = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        self.assertEqual(0, repo_obj.maxage)

    def test_does_not_exists(self):
        # Given an invalid repo
        repo = 'invalid'
        # When trying to get settings from it
        self.getPage("/settings/" + self.USERNAME + "/" + repo)
        # Then a 404 error is return
        self.assertStatus(404)

    def test_browser_with_failed_repo(self):
        # Given a failed repo
        admin = UserObject.get_user('admin')
        admin.user_root = '/invalid/'
        admin.commit()
        # When querying the logs
        self.getPage("/settings/" + self.USERNAME + "/" + self.REPO)
        # Then the page is return with an error message
        self.assertStatus(200)
        self.assertInBody('The repository cannot be found or is badly damaged.')
