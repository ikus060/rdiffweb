# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2026 rdiffweb contributors
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


class RepoActivityTest(rdiffweb.test.WebCase):
    login = True

    def test_get_activity(self):
        # Given an application with log file
        # When getting the system log page
        self.getPage(f"/activity/{self.USERNAME}/{self.REPO}")
        # Then the page return without error
        self.assertStatus(200)
        # Then an ajax table is displayed
        self.assertInBody(f'data-ajax="http://127.0.0.1:{self.PORT}/activity/data.json/{self.USERNAME}/{self.REPO}"')

    def test_get_activity_selenium(self):
        # Given a USERNAME browsing the system logs.
        with self.selenium() as driver:
            # When getting web page.
            driver.get(f'{self.baseurl}/activity/{self.USERNAME}/{self.REPO}')
            # Then the web page contain a datatable
            driver.find_element('css selector', 'table[data-ajax]')
            # Then the web page is loaded without error.
            self.assertFalse(driver.get_log('browser'))
            # Then page contains system activity
            driver.implicitly_wait(10)
            driver.find_element('xpath', "//*[contains(text(), 'Created')]")

    def test_data_json(self):
        # Given a database with system activity
        # When getting data.json
        data = self.getJson(f"/activity/data.json/{self.USERNAME}/{self.REPO}")
        # Then it contains activity data.
        self.assertTrue(len(data['data']) > 0)
