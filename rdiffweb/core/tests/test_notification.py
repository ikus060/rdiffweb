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
from unittest.mock import MagicMock

import cherrypy

import rdiffweb.core.notification
import rdiffweb.test
from rdiffweb.core.model import RepoObject, UserObject


class NotificationJobTest(rdiffweb.test.WebCase):
    def setUp(self):
        self.listener = MagicMock()
        cherrypy.engine.subscribe('queue_mail', self.listener.queue_email, priority=50)
        return super().setUp()

    def tearDown(self):
        cherrypy.engine.unsubscribe('queue_mail', self.listener.queue_email)
        return super().tearDown()

    def test_notification_job(self):
        """
        Run the notification and check if mails are sent
        """
        # Given a user with an email address and a repository with a maxage
        # Set user config
        user = UserObject.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.add()
        repo = RepoObject.query.filter(RepoObject.user == user, RepoObject.repopath == self.REPO).first()
        repo.maxage = 1
        repo.add()
        # When running notification_job
        cherrypy.notification.notification_job()

        # Then an email is queue for this user
        self.listener.queue_email.assert_called_once_with(
            to='test@test.com',
            subject='Notification',
            message="<html>\n  <head></head>\n  <body>\n    Hey admin,\n    <p>\n      You are receiving this email to notify you about your backups. The\n      following repositories are inactive for some time. We invite you to have a look\n      at your last backup schedule.\n    </p>\n    <ul>\n      <li>testcases</li>\n    </ul>\n    <p>\n      If you don't want to be notify about this. You need to review your\n      user preferences.\n    </p>\n  </body>\n</html>",
        )

    def test_notification_job_undefined_last_backup_date(self):
        # Given a valid user with a repository configured for notification
        user = UserObject.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.add()
        # Given a repo with last_backup_date None
        repo = RepoObject.query.filter(RepoObject.user == user, RepoObject.repopath == 'broker-repo').first()
        repo.maxage = 1
        repo.add()
        self.assertIsNone(repo.last_backup_date)

        # When Notification job is running
        cherrypy.notification.notification_job()

        # Then a notification is sent to the user.
        self.listener.queue_email.assert_called_once_with(
            to='test@test.com',
            subject='Notification',
            message="<html>\n  <head></head>\n  <body>\n    Hey admin,\n    <p>\n      You are receiving this email to notify you about your backups. The\n      following repositories are inactive for some time. We invite you to have a look\n      at your last backup schedule.\n    </p>\n    <ul>\n      <li>broker-repo</li>\n    </ul>\n    <p>\n      If you don't want to be notify about this. You need to review your\n      user preferences.\n    </p>\n  </body>\n</html>",
        )

    def test_notification_job_without_notification(self):
        # Given a valid user with a repository configured without notification (-1)
        user = UserObject.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.add()
        repo = RepoObject.query.filter(RepoObject.user == user, RepoObject.repopath == self.REPO).first()
        repo.maxage = -1
        repo.add()

        # Call notification.
        cherrypy.notification.notification_job()

        # Expect it to be called.
        self.listener.queue_email.assert_not_called()


class NotificationPluginTest(rdiffweb.test.WebCase):

    default_config = {
        'email-send-changed-notification': True,
    }

    def setUp(self):
        self.listener = MagicMock()
        cherrypy.engine.subscribe('queue_mail', self.listener.queue_email, priority=50)
        return super().setUp()

    def tearDown(self):
        cherrypy.engine.unsubscribe('queue_mail', self.listener.queue_email)
        return super().tearDown()

    def test_email_changed(self):
        # Given a user with an email address
        user = UserObject.get_user(self.USERNAME)
        user.email = 'original_email@test.com'
        user.add()
        self.listener.queue_email.reset_mock()

        # When updating the user's email
        user = UserObject.get_user(self.USERNAME)
        user.email = 'email_changed@test.com'
        user.add()

        # Then a email is queue to notify the user.
        self.listener.queue_email.assert_called_once_with(
            to='original_email@test.com',
            subject='Email address changed',
            message='<html>\n  <head></head>\n  <body>\n    Hey admin,\n    <p>You recently changed the email address associated with your Rdiffweb account.</p>\n    <p>\n      If you did not make this change and believe your account has been compromised, please contact your administrator.\n    </p>\n  </body>\n</html>',
        )

    def test_email_updated_with_same_value(self):
        # Given a user with an email
        user = UserObject.get_user(self.USERNAME)
        user.email = 'email_changed@test.com'
        self.listener.queue_email.reset_mock()

        # When updating the user's email with the same value
        user.email = 'email_changed@test.com'

        # Then no email are sent to the user
        self.listener.queue_email.assert_not_called()

    def test_password_change_notification(self):
        # Given a user with a email.
        user = UserObject.get_user(self.USERNAME)
        user.email = 'password_change@test.com'
        self.listener.queue_email.reset_mock()

        # When updating the user password
        user.set_password('new_password')

        # Then a email is send to the user
        self.listener.queue_email.assert_called_once_with(
            to='password_change@test.com',
            subject='Password changed',
            message='<html>\n  <head></head>\n  <body>\n    Hey admin,\n    <p>You recently changed the password associated with your Rdiffweb account.</p>\n    <p>\n      If you did not make this change and believe your account has been compromised, please contact your administrator.\n    </p>\n  </body>\n</html>',
        )

    def test_password_change_with_same_value(self):
        # Given a user with a email.
        user = UserObject.get_user(self.USERNAME)
        user.email = 'password_change@test.com'
        user.set_password('new_password')
        self.listener.queue_email.reset_mock()

        # When updating the user password with the same value
        user.set_password('new_password')

        # Then an email is sent to the user
        self.listener.queue_email.assert_called_once_with(
            to='password_change@test.com',
            subject='Password changed',
            message='<html>\n  <head></head>\n  <body>\n    Hey admin,\n    <p>You recently changed the password associated with your Rdiffweb account.</p>\n    <p>\n      If you did not make this change and believe your account has been compromised, please contact your administrator.\n    </p>\n  </body>\n</html>',
        )
