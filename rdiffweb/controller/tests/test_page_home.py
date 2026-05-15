# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

import rdiffweb.test
from rdiffweb.core.model import RepoObject, UserObject


class TestPagehome(rdiffweb.test.WebCase):
    login = True

    def test_redirection_from_index(self):
        # Given an authenticated user
        # When querying the index
        self.getPage("/")
        # Then user get redirected to it's own home page.
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', f'{self.baseurl}/home/{self.USERNAME}')

    def test_redirection_from_home(self):
        # Given an authenticated user
        # When querying the index
        self.getPage("/home/")
        self.assertStatus(303)
        # Then user get redirected to it's own home page.
        self.assertHeaderItemValue('Location', f'{self.baseurl}/home/{self.USERNAME}')

    def test_get_page(self):
        # Given an authenticated user
        # When querying the home page
        self.getPage(f"/home/{self.USERNAME}")
        # Then home page is return without error.
        self.assertStatus(200)
        self.assertInBody('My Repositories')

    def test_with_broken_tree(self):
        # Given a user with invalid repo
        userobj = UserObject.get_user(self.USERNAME)
        RepoObject(user=userobj, repopath='testcases/broker-repo').add().commit()
        RepoObject(user=userobj, repopath='testcases/testcases').add().commit()
        # When querying the home page
        self.getPage(f"/home/{self.USERNAME}")
        # Then home page is return without error.
        self.assertStatus(200)
        self.assertInBody('My Repositories')
        # Then page include the broken repo
        self.assertInBody('testcases/broker-repo')

    def test_with_single_repo(self):
        """
        Verify if browsing '/home/' for a single repository is working.
        """
        # Change the user setting to match single repo.
        user = UserObject.get_user(self.USERNAME)
        user.user_root = os.path.join(self.testcases, 'testcases')
        user.refresh_repos()
        user.commit()
        self.assertEqual(['', 'broker-repo', 'testcases'], [r.name for r in user.repo_objs])
        # Check if listing locations is working
        self.getPage(f"/home/{self.USERNAME}")
        self.assertStatus('200 OK')
        self.assertInBody('testcases')

    def test_with_no_repo(self):
        """
        Verify if browsing '/home/' when user doesn'T have any repo.
        """
        # Given a user without repos
        user = UserObject.get_user(self.USERNAME)
        RepoObject.query.filter(RepoObject.user == user).delete()
        user.commit()
        self.assertEqual([], user.repo_objs)
        # Check if listing locations is working
        self.getPage(f"/home/{self.USERNAME}")
        self.assertStatus('200 OK')
        self.assertInBody('testcases')
