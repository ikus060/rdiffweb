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
from rdiffweb.core.store import USER_ROLE


class SettingsTest(rdiffweb.test.WebCase):

    login = True

    def test_activities(self):
        self.getPage("/graphs/activities/" + self.USERNAME + "/" + self.REPO + "/")
        self.assertStatus('200 OK')

    def test_errors(self):
        self.getPage("/graphs/errors/" + self.USERNAME + "/" + self.REPO + "/")
        self.assertStatus('200 OK')

    def test_files(self):
        self.getPage("/graphs/files/" + self.USERNAME + "/" + self.REPO + "/")
        self.assertStatus('200 OK')

    def test_sizes(self):
        self.getPage("/graphs/sizes/" + self.USERNAME + "/" + self.REPO + "/")
        self.assertStatus('200 OK')

    def test_times(self):
        self.getPage("/graphs/times/" + self.USERNAME + "/" + self.REPO + "/")
        self.assertStatus('200 OK')

    def test_as_another_user(self):
        # Create a nother user with admin right
        user_obj = self.app.store.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases

        self.getPage("/graphs/activities/anotheruser/testcases")
        self.assertStatus('200 OK')
        self.assertInBody("Activities")

        # Remove admin role
        admin = self.app.store.get_user('admin')
        admin.role = USER_ROLE

        # Browse admin's repos
        self.getPage("/graphs/activities/anotheruser/testcases")
        self.assertStatus('403 Forbidden')

    def test_chartkick_js(self):
        self.getPage("/static/js/chart.min.js")
        self.assertStatus('200 OK')
        self.assertInBody("Chart")

    def test_chart_js(self):
        self.getPage("/static/js/chartkick.min.js")
        self.assertStatus('200 OK')
        self.assertInBody("Chartkick")

    def test_does_not_exists(self):
        # Given an invalid repo
        repo = 'invalid'
        # When trying to get graphs of it
        self.getPage("/graphs/activities/" + self.USERNAME + "/" + repo + "/")
        # Then a 404 error is return
        self.assertStatus(404)
