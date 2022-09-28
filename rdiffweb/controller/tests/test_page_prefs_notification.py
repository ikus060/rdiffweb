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


import rdiffweb.test
from rdiffweb.core.model import RepoObject


class PagePrefNotificationTest(rdiffweb.test.WebCase):

    login = True

    def test_get_page(self):
        # When querying the age
        self.getPage("/prefs/notification", method='GET')
        # Then the page is returned successfully
        self.assertStatus(200)
        self.assertInBody("Notification")

    def test_update_notification(self):
        # Given a user with a repository
        # When updating the notification settings
        self.getPage("/prefs/notification", method='POST', body={'action': 'set_notification_info', 'testcases': '7'})
        # Then the page return successfully with the modification
        self.assertStatus(200)
        self.assertInBody('Notification settings updated successfully.')
        self.assertInBody('<option selected value="7">')
        # Then database is updated too
        repo_obj = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        self.assertEqual(7, repo_obj.maxage)

    def test_update_notification_method_get(self):
        # Given a user with repositories
        # When trying to update notification with GET method
        self.getPage("/prefs/notification?action=set_notification_info&testcases=7")
        # Then page return with success
        self.assertStatus(200)
        self.assertNotInBody('<option selected value="7">')
        # Then page doesn't update values
        self.assertNotInBody('Notification settings updated successfully.')
        # Then database is not updated
        repo_obj = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        self.assertEqual(0, repo_obj.maxage)

    def test_update_notification_with_invalid_string(self):
        # Given a user with a repository
        # When updating the notification settings
        self.getPage(
            "/prefs/notification", method='POST', body={'action': 'set_notification_info', 'testcases': 'invalid'}
        )
        # Then the page return successfully with the modification
        self.assertStatus(200)
        self.assertInBody('Invalid Choice:')
        self.assertNotInBody('Notification settings updated successfully.')
        # Then database is not updated
        repo_obj = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        self.assertEqual(0, repo_obj.maxage)

    def test_update_notification_with_invalid_number(self):
        # Given a user with a repository
        # When updating the notification settings
        self.getPage("/prefs/notification", method='POST', body={'action': 'set_notification_info', 'testcases': '365'})
        # Then the page return successfully with the modification
        self.assertStatus(200)
        self.assertInBody('Not a valid choice')
        self.assertNotInBody('Notification settings updated successfully.')
        # Then database is not updated
        repo_obj = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        self.assertEqual(0, repo_obj.maxage)
