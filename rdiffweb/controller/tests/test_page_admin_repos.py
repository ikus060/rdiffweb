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


import rdiffweb.test
from rdiffweb.core.model import RepoObject, UserObject


class AdminReposTest(rdiffweb.test.WebCase):
    login = True

    def test_repos(self):
        # Given an admin user with repos
        repos = (
            RepoObject.query.join(UserObject, RepoObject.userid == UserObject.userid)
            .filter(UserObject.username == self.USERNAME)
            .all()
        )
        # When querying the repository page
        self.getPage("/admin/repos/")
        self.assertStatus(200)
        # Then the page contains our repos.
        for repo in repos:
            self.assertInBody(repo.name)

    def test_repos_with_maxage(self):
        # Given an admin user with repos
        repos = (
            RepoObject.query.join(UserObject, RepoObject.userid == UserObject.userid)
            .filter(UserObject.username == self.USERNAME)
            .all()
        )
        # Given a repo with maxage
        repos[0].maxage = 3
        repos[0].commit()
        # When querying the repository page
        self.getPage("/admin/repos/")
        self.assertStatus(200)
        # Then the page contains "3 days".
        self.assertInBody("3 days")

    def test_repos_with_keepdays(self):
        # Given an admin user with repos
        repos = (
            RepoObject.query.join(UserObject, RepoObject.userid == UserObject.userid)
            .filter(UserObject.username == self.USERNAME)
            .all()
        )
        # Given a repo with maxage
        repos[0].keepdays = 6
        repos[0].commit()
        # When querying the repository page
        self.getPage("/admin/repos/")
        self.assertStatus(200)
        # Then the page contains "3 days".
        self.assertInBody("6 days")
