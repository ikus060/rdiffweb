# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 Patrik Dufresne Service Logiciel
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
from time import sleep
"""
Created on Feb 13, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

from unittest.mock import MagicMock, ANY, patch
import unittest

from rdiffweb.core.notification import html2plaintext, NotificationPlugin, NotificationJob, \
    EmailClient
from rdiffweb.test import AppTestCase, WebCase


class NotificationJobTest(AppTestCase):

    def test_run_with_notification(self):
        """
        Run the notification and check if mails are sent
        """
        # Set user config
        user = self.app.store.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.get_repo(self.REPO).maxage = 1

        # Get ref to notification plugin
        n = NotificationJob(app=self.app)
        self.assertIsNotNone(n)
        n.send_mail = MagicMock()

        # Call notification.
        n.job_run()

        # Expect it to be called.
        n.send_mail.assert_called_once_with(user, 'Notification', 'email_notification.html', repos=[ANY], user=user)

    def test_run_without_notification(self):
        """
        Run the notification and check if mails are sent
        """
        # Set user config
        user = self.app.store.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.get_repo(self.REPO).maxage = -1

        # Get ref to notification plugin
        n = NotificationJob(self.app)
        self.assertIsNotNone(n)
        n.send_mail = MagicMock()

        # Call notification.
        n.job_run()

        # Expect it to be called.
        n.send_mail.assert_not_called()


class EmailClientTest(AppTestCase):

    default_config = {
        'EmailHost': 'smtp.gmail.com:587',
        'EmailUsername': 'test@test.com',
        'EmailPassword': 'test1234',
        'EmailEncryption': 'starttls'
    }

    def test_send_mail(self):
        """
        Check email template generation.
        """
        with patch('rdiffweb.core.notification.smtplib'):
            # Set user config
            user = self.app.store.get_user(self.USERNAME)
            user.email = 'test@test.com'

            # Get ref to notification plugin
            n = EmailClient(self.app)
            self.assertIsNotNone(n)
            n.send_mail(user, 'subject', 'email_notification.html')

    def test_async_send_mail(self):
        """
        Check email template generation.
        """
        self.assertEquals(0, len(self.app.scheduler.list_tasks()))

        # Set user config
        user = self.app.store.get_user(self.USERNAME)
        user.email = 'test@test.com'

        # Get ref to notification plugin
        n = EmailClient(self.app)
        n.send_mail = MagicMock()
        self.assertIsNotNone(n)
        n.async_send_mail(user, 'subject', 'email_notification.html')

        # Check task scheduled
        self.assertEquals(1, len(self.app.scheduler.list_tasks()))

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


class NotificationPluginTest(WebCase):

    default_config = {'emailsendchangednotification': True}

    def test_email_changed(self):
        # Get ref to notification plugin
        n = self.app.notification
        self.assertIsNotNone(n)
        n.async_send_mail = MagicMock()

        # Set user config
        user = self.app.store.get_user(self.USERNAME)
        user.email = 'test@test.com'

        # Expect it to be called.
        sleep(1)
        n.async_send_mail.assert_called_once_with(ANY, ANY, 'email_changed.html')

    def test_password_change_notification(self):
        # Set user config
        user = self.app.store.get_user(self.USERNAME)
        user.email = 'test@test.com'

        # Get ref to notification plugin
        n = NotificationPlugin(app=self.app)
        self.assertIsNotNone(n)
        n.async_send_mail = MagicMock()

        # Change password
        user.set_password('new_password')

        # Expect it to be called.
        sleep(1)
        n.async_send_mail.assert_called_once_with(ANY, ANY, 'password_changed.html')

    def test_async_send_mail(self):

        with patch('rdiffweb.core.notification.smtplib'):
            # Set user config
            user = self.app.store.get_user(self.USERNAME)
            user.email = 'test@test.com'

            # Get ref to notification plugin
            n = EmailClient(self.app)
            n.send_mail = MagicMock()
            self.assertIsNotNone(n)
            n.async_send_mail(user, 'subject', 'email_notification.html')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
