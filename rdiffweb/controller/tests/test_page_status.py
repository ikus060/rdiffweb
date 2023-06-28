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
Created on Aug 30, 2019

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import RepoObject, UserObject


class StatusTest(rdiffweb.test.WebCase):
    login = True

    @parameterized.expand(
        [
            ('/status/invalid/', 404),
            ('/status/invalid/per-days.json', 404),
            ('/status/invalid/age.json', 404),
            ('/status/invalid/disk-usage.json', 404),
            ('/status/invalid/elapsetime.json', 404),
            ('/status/invalid/activities.json', 404),
            ('/status/admin', 301),
            ('/status/admin/'),
            ('/status/admin/per-days.json'),
            ('/status/admin/per-days.json?days=1'),
            ('/status/admin/per-days.json?days=60'),
            ('/status/admin/per-days.json?days=61', 400),
            ('/status/admin/per-days.json?days=0', 400),
            ('/status/admin/age.json'),
            ('/status/admin/age.json?count=1'),
            ('/status/admin/age.json?count=20'),
            ('/status/admin/age.json?count=21', 400),
            ('/status/admin/age.json?count=0', 400),
            ('/status/admin/disk-usage.json'),
            ('/status/admin/elapsetime.json'),
            ('/status/admin/elapsetime.json?days=1&count=1'),
            ('/status/admin/elapsetime.json?days=60&count=20'),
            ('/status/admin/elapsetime.json?days=61&count=21', 400),
            ('/status/admin/elapsetime.json?days=0&count=0', 400),
            ('/status/admin/activities.json'),
            ('/status/admin/activities.json?days=1&count=1'),
            ('/status/admin/activities.json?days=60&count=20'),
            ('/status/admin/activities.json?days=61&count=21', 400),
            ('/status/admin/activities.json?days=0&count=0', 400),
        ]
    )
    def test_get_page(self, url, expected_status=200):
        self.getPage(url)
        self.assertStatus(expected_status)

    def test_age_json(self):
        # Given a user with repositories
        # When queyring age.json
        data = self.getJson('/status/admin/age.json')
        # Then json data is returned
        userobj = UserObject.query.filter(UserObject.username == self.USERNAME).one()
        repo = RepoObject.get_repo('admin/testcases', userobj)
        delta = (RdiffTime().epoch - repo.last_backup_date.epoch) / 60 / 60
        self.assertEqual(
            data,
            [
                {
                    "name": "Hours since last backup",
                    "data": {
                        "testcases": float("%.2g" % delta),
                    },
                }
            ],
        )

    def test_disk_usage(self):
        # Given a user with repositories
        # When queyring age.json
        data = self.getJson('/status/admin/disk-usage.json')
        # Then json data is returned
        self.assertEqual(
            data,
            [['testcases', 3.5], ['broker-repo', 0]],
        )

    @parameterized.expand(
        [
            ('/status/anotheruser/'),
            ('/status/anotheruser/per-days.json'),
            ('/status/anotheruser/age.json'),
            ('/status/anotheruser/disk-usage.json'),
            ('/status/anotheruser/elapsetime.json'),
            ('/status/anotheruser/activities.json'),
        ]
    )
    def test_as_another_user(self, url):
        # Create a nother user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()
        self.getPage(url)
        self.assertStatus('200 OK')

        # Remove admin right
        admin = UserObject.get_user('admin')
        admin.role = UserObject.USER_ROLE
        admin.commit()

        # Browse admin's repos
        self.getPage(url)
        self.assertStatus(404)

    def test_with_invalid_username(self):
        # Given an invalid repo
        repo = 'invalid'
        # When trying to browse the history
        self.getPage("/history/" + self.USERNAME + "/" + repo)
        # Then a 404 error is return to the user
        self.assertStatus(404)
