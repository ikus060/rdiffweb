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
Created on Jan 1, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""


from base64 import b64encode

from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.model import RepoObject, UserObject


class SettingsTest(rdiffweb.test.WebCase):
    login = True

    def test_page(self):
        self.getPage("/settings/" + self.USERNAME + "/" + self.REPO)
        self.assertInBody("General Settings")
        self.assertStatus(200)

    def test_page_encoding_none(self):
        # Given a repo where encoding is not defined.
        RepoObject.query.update({RepoObject.encoding: None})
        repo = RepoObject.query.first()
        repo.commit()
        # When browsing settings pages
        self.getPage("/settings/" + self.USERNAME + "/" + self.REPO)
        # Then not error is report.
        self.assertStatus(200)

    def test_as_another_user(self):
        # Create a nother user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()
        self.getPage("/settings/anotheruser/testcases")
        self.assertInBody("General Settings")
        self.assertStatus('200 OK')

        # Remove admin right
        admin = UserObject.get_user('admin')
        admin.role = UserObject.USER_ROLE
        admin.commit()

        # Browse admin's repos
        self.getPage("/settings/anotheruser/testcases")
        self.assertStatus('403 Forbidden')

    def test_set_maxage(self):
        # When updating maxage
        self.getPage("/settings/" + self.USERNAME + "/" + self.REPO + "/", method="POST", body={'maxage': '4'})
        self.assertStatus(303)
        # Then a succes message is displayed to user
        self.getPage("/settings/" + self.USERNAME + "/" + self.REPO + "/")
        self.assertStatus(200)
        self.assertInBody("Settings modified successfully.")
        # Then repo get updated
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


class ApiReposTest(rdiffweb.test.WebCase):
    auth = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]

    def test_list_repos(self):
        # Given a user with repos
        user = UserObject.get_user('admin')
        self.assertEqual(2, len(user.repo_objs))
        # When querying the list of repos
        data = self.getJson('/api/currentuser/repos', headers=self.auth)

        # Then the list is returned
        self.assertEqual(2, len(data))
        self.assertEqual(
            data,
            [
                {
                    'repoid': user.repo_objs[0].repoid,
                    'name': 'broker-repo',
                    'maxage': 0,
                    'keepdays': -1,
                    'ignore_weekday': [],
                    'display_name': 'broker-repo',
                    'last_backup_date': None,
                    'status': 'in_progress',
                    'encoding': 'utf-8',
                },
                {
                    'repoid': user.repo_objs[1].repoid,
                    'name': 'testcases',
                    'maxage': 0,
                    'keepdays': -1,
                    'ignore_weekday': [],
                    'display_name': 'testcases',
                    'last_backup_date': '2016-02-02T16:30:40-05:00',
                    'status': 'ok',
                    'encoding': 'utf-8',
                },
            ],
        )

    @parameterized.expand(
        [
            ('all', True),
            ('write_user', True),
            ('read_user', True),
            (None, False),
        ]
    )
    def test_list_repos_with_access_token(self, scope, success):
        # Given a user with repos & access token
        user = UserObject.get_user('admin')
        self.assertEqual(2, len(user.repo_objs))
        token = user.add_access_token(name='test', scope=scope)
        user.commit()
        auth = [("Authorization", "Basic " + b64encode(f"admin:{token}".encode('ascii')).decode('ascii'))]

        # When querying the list of repos
        self.getPage('/api/currentuser/repos', headers=auth)

        # Then the list is returned
        if success:
            self.assertStatus(200)
        else:
            self.assertStatus(403)

    def test_get_repo_with_id(self):
        # Given a user with repos
        user = UserObject.get_user('admin')
        self.assertEqual(2, len(user.repo_objs))
        # When querying repos settings with repoid
        repo = user.repo_objs[0]
        data = self.getJson('/api/currentuser/repos/%s' % repo.repoid, headers=self.auth)

        # Then the list is returned
        self.assertEqual(
            data,
            {
                'repoid': repo.repoid,
                'name': repo.name,
                'maxage': repo.maxage,
                'keepdays': repo.keepdays,
                'ignore_weekday': [],
                'display_name': repo.display_name,
                'last_backup_date': repo.last_backup_date,
                'status': repo.status[0],
                'encoding': 'utf-8',
            },
        )

    def test_get_repo_with_name(self):
        # Given a user with repos
        user = UserObject.get_user('admin')
        self.assertEqual(2, len(user.repo_objs))
        # When querying repos settings with repoid
        data = self.getJson('/api/currentuser/repos/testcases', headers=self.auth)
        repo = RepoObject.get_repo('admin/testcases', as_user=user)

        # Then the list is returned
        self.assertEqual(
            data,
            {
                'repoid': repo.repoid,
                'name': 'testcases',
                'maxage': 0,
                'keepdays': -1,
                'ignore_weekday': [],
                'display_name': 'testcases',
                'last_backup_date': '2016-02-02T16:30:40-05:00',
                'status': 'ok',
                'encoding': 'utf-8',
            },
        )

    @parameterized.expand(
        [
            ('all', True),
            ('write_user', True),
            ('read_user', True),
            (None, False),
        ]
    )
    def test_get_repo_with_access_token(self, scope, success):
        # Given a user with repos
        user = UserObject.get_user('admin')
        self.assertEqual(2, len(user.repo_objs))
        token = user.add_access_token(name='test', scope=scope)
        user.commit()
        auth = [("Authorization", "Basic " + b64encode(f"admin:{token}".encode('ascii')).decode('ascii'))]
        # When querying repos settings with repoid
        self.getPage('/api/currentuser/repos/%s' % user.repo_objs[0].repoid, headers=auth)

        # Then the list is returned
        if success:
            self.assertStatus(200)
        else:
            self.assertStatus(403)

    @parameterized.expand(
        [
            # Not working
            ('repoid', '4', False),
            ('name', 'newrepo', False),
            ('display_name', 'newrepo', False),
            ('last_backup_date', '2024-02-02T16:30:40-05:00', False),
            ('status', '2024-02-02T16:30:40-05:00', False),
            # Working
            ('maxage', '7', True),
            ('keepdays', '30', True),
            ('ignore_weekday', '6', True, '[6]'),
            ('encoding', 'latin_1', True, 'iso8859-1'),
        ]
    )
    def test_post_repo(self, field, new_value, success, expected_value=None):
        # Given a user with repos
        user = UserObject.get_user('admin')
        repo = RepoObject.get_repo('admin/testcases', as_user=user)
        self.assertEqual(repo.name, 'testcases')

        # When updating repo settings
        self.getPage(
            '/api/currentuser/repos/testcases',
            headers=self.auth,
            method='POST',
            body={
                field: new_value,
            },
        )

        # Then it's working or not
        repo.expire()
        if success:
            self.assertStatus(200, 'BODY: %s' % self.body)
            self.assertEqual(str(getattr(repo, field)), new_value if expected_value is None else expected_value)
        else:
            self.assertStatus(400)
            self.assertNotEqual(str(getattr(repo, field)), new_value if expected_value is None else expected_value)

    def test_post_repo_json(self):
        # Given a user with repos
        user = UserObject.get_user('admin')
        repo = RepoObject.get_repo('admin/testcases', as_user=user)
        self.assertEqual(repo.name, 'testcases')

        # When updating repo settings
        self.getPage(
            '/api/currentuser/repos/testcases',
            headers=self.auth + [('Content-Type', 'application/json')],
            method='POST',
            body={
                'maxage': '7',
            },
        )

        # Then it's working or not
        repo.expire()
        self.assertStatus(200)
        self.assertEqual(repo.maxage, 7)
