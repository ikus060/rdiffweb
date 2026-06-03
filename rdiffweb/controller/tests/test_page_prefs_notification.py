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

from unittest.mock import ANY, MagicMock

import cherrypy

import rdiffweb.test
from rdiffweb.core.model import UserObject


class PagePrefNotificationTest(rdiffweb.test.WebCase):
    login = True

    def setUp(self):
        self.listener = MagicMock()
        cherrypy.engine.subscribe('queue_mail', self.listener.queue_email, priority=50)
        return super().setUp()

    def tearDown(self):
        cherrypy.engine.unsubscribe('queue_mail', self.listener.queue_email)
        return super().tearDown()

    def test_get_page(self):
        # When querying the age
        self.getPage("/prefs/notification", method='GET')
        # Then the page is returned successfully
        self.assertStatus(200)
        self.assertInBody("Notification")

    def test_update_report_time_range(self):
        # Given a user withotu report time range
        userobj = UserObject.get_user(self.USERNAME)
        self.assertEqual(0, userobj.report_time_range)
        # When updating the report time range settings
        self.getPage("/prefs/notification", method='POST', body={'action': 'set_report_info', 'report_time_range': '7'})
        # Then the page return successfully with the modification
        self.assertStatus(303)
        self.getPage("/prefs/notification")
        self.assertInBody('Report settings updated successfully.')
        self.assertMatchesBody('name="report_time_range"\\s+value="7"\\s+checked>')
        # Then database is updated too
        userobj.expire()
        self.assertEqual(7, userobj.report_time_range)

    def test_update_report_time_range_with_invalid(self):
        # Given a user without report time range
        userobj = UserObject.get_user(self.USERNAME)
        self.assertEqual(0, userobj.report_time_range)
        # When updating the report time range settings
        self.getPage(
            "/prefs/notification", method='POST', body={'action': 'set_report_info', 'report_time_range': '300'}
        )
        # Then the page return successfully with the modification
        self.assertStatus(200)
        self.assertInBody('Send me a backup status report: Not a valid choice')
        # Then value is un-changed
        userobj.expire()
        self.assertEqual(0, userobj.report_time_range)

    def test_send_report(self):
        # Given a user without email
        userobj = UserObject.get_user(self.USERNAME)
        userobj.email = 'test@test.com'
        userobj.report_time_range = 7
        userobj.add().commit()
        # When sending a report
        self.getPage("/prefs/notification", method='POST', body={'action': 'set_report_info', 'send_report': '1'})
        self.assertStatus(303)
        # Then page display a sucess
        self.getPage("/prefs/notification")
        self.assertStatus(200)
        self.assertInBody('Report sent successfully.')
        # Then report is sent by email.
        self.listener.queue_email.assert_called_once_with(
            to='test@test.com',
            subject='Weekly Backup Report',
            message=ANY,
        )

    def test_send_report_without_report_time_range(self):
        # Given a user without report time range
        userobj = UserObject.get_user(self.USERNAME)
        userobj.email = 'test@test.com'
        userobj.report_time_range = 0
        userobj.add().commit()
        # When sending a report
        self.getPage("/prefs/notification", method='POST', body={'action': 'set_report_info', 'send_report': '1'})
        # Then the page return error
        self.assertStatus(200)
        self.assertInBody('You must select a time range and save changes before sending a report.')

    def test_send_report_without_email(self):
        # Given a user without email
        userobj = UserObject.get_user(self.USERNAME)
        userobj.email = ''
        userobj.report_time_range = 7
        userobj.add().commit()
        # When sending a report
        self.getPage("/prefs/notification", method='POST', body={'action': 'set_report_info', 'send_report': '1'})
        # Then the page return error
        self.assertStatus(200)
        self.assertInBody('Could not send report to user without configured email.')
