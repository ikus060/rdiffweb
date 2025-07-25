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

import rdiffweb.test
from rdiffweb.core.model import UserObject
from rdiffweb.core.rdw_templating import url_for


class StatsTest(rdiffweb.test.WebCase):
    login = True

    def test_stats_index(self):
        self.getPage(url_for('stats', self.USERNAME, self.REPO, ''))
        self.assertStatus('200 OK')
        self.assertInBody('No File Statistics Selected')

    def test_stats_date(self):
        self.getPage(url_for('stats', self.USERNAME, self.REPO, date=1454448640, limit=10))
        self.assertStatus('200 OK')
        # Then a table is displayed
        self.assertInBody('<table')
        self.assertNotInBody('No File Statistics Selected')

    def test_stats_data_json(self):
        self.getPage(url_for('stats', 'data.json', self.USERNAME, self.REPO, date=1454448640, limit=10))
        self.assertStatus('200 OK')

    def test_stats_date_selenium(self):
        with self.selenium() as driver:
            # When browsing graph
            driver.get(url_for('stats', self.USERNAME, self.REPO, date=1454448640, limit=10))
            # Then page load without error
            self.assertFalse(driver.get_log('browser'))

    def test_as_another_user(self):
        # Create another user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()

        self.getPage("/stats/anotheruser/testcases/")
        self.assertStatus('200 OK')
        self.assertInBody("No File Statistics Selected")

        # Remove admin role
        admin = UserObject.get_user('admin')
        admin.role = UserObject.USER_ROLE
        admin.commit()

        # Browse admin's repos
        self.getPage("/stats/anotheruser/testcases/")
        self.assertStatus('403 Forbidden')

    def test_does_not_exists(self):
        # Given an invalid repo
        repo = 'invalid'
        # When trying to get graphs of it
        self.getPage("/stats/" + self.USERNAME + "/" + repo + "/")
        # Then a 404 error is return
        self.assertStatus(404)

    def test_browser_with_failed_repo(self):
        # Given a failed repo
        admin = UserObject.get_user('admin')
        admin.user_root = 'invalid'
        admin.commit()
        # When querying the logs
        self.getPage("/stats/" + self.USERNAME + "/" + self.REPO + "/")
        # Then the page is return with an error message
        self.assertStatus(200)
        self.assertInBody('The repository cannot be found or is badly damaged.')
