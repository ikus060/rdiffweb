#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 Patrik Dufresne Service Logiciel
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
Created on Feb 13, 2016

@author: ikus060
"""

from __future__ import unicode_literals

from mock import MagicMock, ANY, patch
import unittest

from rdiffweb.plugins.notification import html2plaintext
from rdiffweb.test import AppTestCase


class NotificationTest(AppTestCase):

    enabled_plugins = ['SQLite', 'EmailNotification']

    USERNAME = 'admin'

    PASSWORD = 'admin'

    reset_app = True

    reset_testcases = True

    def test_run_with_notification(self):
        """
        Run the notification and check if mails are sent
        """
        # Set user config
        user = self.app.userdb.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.get_repo(self.REPO).maxage = 1

        # Get ref to notification plugin
        n = self.app.plugins.get_plugin_by_name('NotificationPlugin')
        self.assertIsNotNone(n)
        n.send_mail = MagicMock()

        # Call notification.
        n.send_notifications()

        # Expect it to be called.
        n.send_mail.assert_called_once_with(user, 'Notification', 'email_notification.html', repos=[ANY], user=user)

    def test_run_without_notification(self):
        """
        Run the notification and check if mails are sent
        """
        # Set user config
        user = self.app.userdb.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.get_repo(self.REPO).maxage = -1

        # Get ref to notification plugin
        n = self.app.plugins.get_plugin_by_name('NotificationPlugin')
        self.assertIsNotNone(n)
        n.send_mail = MagicMock()

        # Call notification.
        n.send_notifications()

        # Expect it to be called.
        n.send_mail.assert_not_called()

    def test_send_mail(self):
        """
        Check email template generation.
        """
        with patch('rdiffweb.plugins.notification.smtplib') as patcher:
            # Set user config
            user = self.app.userdb.get_user(self.USERNAME)
            user.email = 'test@test.com'

            # Set email config
            self.app.cfg.set_config('EmailHost', 'smtp.gmail.com:587')
            self.app.cfg.set_config('EmailUsername', 'test@test.com')
            self.app.cfg.set_config('EmailPassword', 'test1234')
            self.app.cfg.set_config('EmailEncryption', 'starttls')

            # Get ref to notification plugin
            n = self.app.plugins.get_plugin_by_name('NotificationPlugin')
            self.assertIsNotNone(n)
            n.send_mail(user, 'subject', 'email_notification.html')

    def test_html2plaintext(self):
        """
        Check if this convertion is working fine.
        """

        html = """<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
       Here is the <a href="https://www.python.org">link</a> you wanted.
    </p>
  </body>
</html>
"""

        expected = """Hi!
How are you?
Here is the link you wanted."""
        self.assertEqual(expected, html2plaintext(html))

    def test_email_changed(self):
        # Get ref to notification plugin
        n = self.app.plugins.get_plugin_by_name('NotificationPlugin')
        self.assertIsNotNone(n)
        n.send_mail = MagicMock()

        # Set user config
        user = self.app.userdb.get_user(self.USERNAME)
        user.email = 'test@test.com'

        # Expect it to be called.
        n.send_mail.assert_called_once_with(ANY, 'Email address changed', 'email_changed.html')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
