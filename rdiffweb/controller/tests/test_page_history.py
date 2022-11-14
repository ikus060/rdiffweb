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
Created on Dec 29, 2015

@author: Patrik Dufresne
"""


import rdiffweb.test
from rdiffweb.core.model import UserObject


class HistoryPageTest(rdiffweb.test.WebCase):

    login = True

    def _history(self, user, path, limit=None):
        url = "/history/" + user + "/" + path + "/"
        if limit:
            url += "?limit=%s" % limit
        self.getPage(url)
        self.assertStatus('200 OK')

    def test_history_with_root(self):
        self._history(self.USERNAME, self.REPO)
        # Check revisions
        self.assertInBody("2016-02-02T16:30:40-05:00")
        self.assertInBody("2014-11-02T09:50:53-05:00")
        # Check show more button get displayed
        self.assertInBody("Show more")
        # Check download buttont
        self.assertInBody("Download")
        self.assertInBody("/restore/" + self.USERNAME + "/" + self.REPO + "?date=1415221507")

    def test_history_with_path(self):
        self._history(self.USERNAME, 'testcases/Subdirectory')
        self.assertInBody("2016-02-02T16:30:40-05:00")
        self.assertInBody("2016-01-20T10:42:21-05:00")
        self.assertNotInBody("Show more")

    def test_history_with_deleted_path(self):
        self._history(self.USERNAME, "testcases/R%C3%A9pertoire%20Supprim%C3%A9/")
        self.assertStatus(200)
        self.assertInBody("Download")
        self.assertInBody("ZIP")
        self.assertInBody("TAR.GZ")
        self.assertInBody("2014-11-01T15:51:15-04:00")
        self.assertInBody(
            "/restore/" + self.USERNAME + "/" + self.REPO + "/R%C3%A9pertoire%20Supprim%C3%A9?date=1414871475"
        )

    def test_history_with_deleted_file(self):
        self._history(self.USERNAME, "testcases/R%C3%A9pertoire%20Supprim%C3%A9/Untitled%20Empty%20Text%20File")
        self.assertStatus(200)
        self.assertInBody("Download")
        self.assertNotInBody("ZIP")
        self.assertNotInBody("TAR.GZ")
        self.assertInBody("2014-11-01T15:51:15-04:00")
        self.assertInBody(
            "/restore/"
            + self.USERNAME
            + "/"
            + self.REPO
            + "/R%C3%A9pertoire%20Supprim%C3%A9/Untitled%20Empty%20Text%20File?date=1414871475"
        )
        self.assertInBody("21 bytes")
        self.assertInBody("0 byte")

    def test_history_with_limit(self):
        self._history(self.USERNAME, self.REPO, 10)
        self.assertInBody("Show more")
        self._history(self.USERNAME, self.REPO, 50)
        self.assertNotInBody("Show more")

    def test_as_another_user(self):
        # Create a nother user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()
        self.getPage("/history/anotheruser/testcases")
        self.assertStatus('200 OK')

        # Remove admin right
        admin = UserObject.get_user('admin')
        admin.role = UserObject.USER_ROLE
        admin.commit()

        # Browse admin's repos
        self.getPage("/history/anotheruser/testcases")
        self.assertStatus('403 Forbidden')

    def test_history_does_not_exists(self):
        # Given an invalid repo
        repo = 'invalid'
        # When trying to browse the history
        self.getPage("/history/" + self.USERNAME + "/" + repo)
        # Then a 404 error is return to the user
        self.assertStatus(404)

    def test_browser_with_failed_repo(self):
        # Given a failed repo
        admin = UserObject.get_user('admin')
        admin.user_root = 'invalid'
        admin.commit()
        # When querying the logs
        self.getPage("/history/" + self.USERNAME + "/" + self.REPO)
        # Then the page is return with an error message
        self.assertStatus(200)
        self.assertInBody('The repository cannot be found or is badly damaged.')
