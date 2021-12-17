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
Created on Feb 13, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

from time import sleep
from unittest.mock import ANY, MagicMock, patch

import rdiffweb.test
from rdiffweb.core.notification import (EmailClient, NotificationJob, html2plaintext)


class NotificationJobTest(rdiffweb.test.AppTestCase):

    default_config = {
        'email-host': 'example.com'
    }

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
        n.send_mail.assert_called_once_with(
            user, 'Notification', 'email_notification.html', repos=[ANY], user=user)

    def test_run_with_undefined_last_backup_date(self):
        # Given a valid user with a repository configured for notification
        user = self.app.store.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.get_repo('broker-repo').maxage = 1
        self.assertIsNone(user.get_repo('broker-repo').last_backup_date)

        # When Notification job is running
        n = NotificationJob(app=self.app)
        self.assertIsNotNone(n)
        n.send_mail = MagicMock()
        n.job_run()

        # Then a notification is sent to the user.
        n.send_mail.assert_called_once_with(
            user, 'Notification', 'email_notification.html', repos=[ANY], user=user)

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

    def test_run_without_email_host(self):
        self.app.cfg.email_host = None

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

        # Expect no call
        n.send_mail.assert_not_called()


class EmailClientTest(rdiffweb.test.AppTestCase):

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

    def test_send_email_host_without_port(self):
        """
        Check email template generation.
        """
        self.app.cfg.email_host = 'example.com'
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
        self.assertEqual(0, len(self.app.scheduler.list_tasks()))

        # Set user config
        user = self.app.store.get_user(self.USERNAME)
        user.email = 'test@test.com'

        # Get ref to notification plugin
        n = EmailClient(self.app)
        n.send_mail = MagicMock()
        self.assertIsNotNone(n)
        n.async_send_mail(user, 'subject', 'email_notification.html')

        # Check task scheduled
        self.assertEqual(1, len(self.app.scheduler.list_tasks()))

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


class NotificationPluginTest(rdiffweb.test.WebCase):

    default_config = {
        'emailsendchangednotification': True,
        'email-host': 'example.com'
    }

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
        n.async_send_mail.reset_mock()

        # Change email again for same value
        user.email = 'test@test.com'
        n.async_send_mail.assert_not_called()

    def test_password_change_notification(self):
        # Get ref to notification plugin
        n = self.app.notification
        self.assertIsNotNone(n)
        n.async_send_mail = MagicMock()

        # Set user config
        user = self.app.store.get_user(self.USERNAME)
        user.email = 'test@test.com'
        n.async_send_mail.reset_mock()

        # Change password
        user.set_password('new_password')

        # Expect it to be called.
        sleep(1)
        n.async_send_mail.assert_called_once_with(ANY, ANY, 'password_changed.html')
        n.async_send_mail.reset_mock()

        # Change password again for same value. Check if notificatiom is sent.
        user.set_password('new_password')
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


class NotificationPluginTestWithoutEmailHost(rdiffweb.test.WebCase):

    default_config = {
        'emailsendchangednotification': True,
    }

    def test_email_changed_without_email_host(self):
        # Get ref to notification plugin
        n = self.app.notification
        self.assertIsNotNone(n)
        n.async_send_mail = MagicMock()

        # Set user config
        user = self.app.store.get_user(self.USERNAME)
        user.email = 'test@test.com'

        # Expect it to be called.
        sleep(1)
        n.async_send_mail.assert_not_called()
