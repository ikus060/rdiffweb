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

    def test_check_schedule(self):
        # Given the application is started
        # Then remove_older job should be schedule
        self.assertEqual(1, len([job for job in cherrypy.scheduler.list_jobs() if job.name == 'notification_job']))

    def test_notification_job(self):
        """
        Run the notification and check if mails are sent
        """
        # Given a user with an email address and a repository with a maxage
        # Set user config
        user = UserObject.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.commit()
        repo = RepoObject.query.filter(RepoObject.user == user, RepoObject.repopath == self.REPO).first()
        repo.maxage = 1
        repo.commit()
        # When running notification_job
        cherrypy.notification.notification_job()

        # Then an email is queue for this user
        self.listener.queue_email.assert_called_once_with(
            to='test@test.com',
            subject='Notification',
            message="<html>\n  <head></head>\n  <body>\n    <p>\n      <a>Hey admin,</a>\n    </p>\n    <p>\n      You are receiving this email to notify you about your backups. The\n      following repositories are inactive for some time. We invite you to have a look\n      at your last backup schedule.\n    </p>\n    <ul>\n      \n        <li>\n          <a>testcases</a>\n        </li>\n      \n    </ul>\n    <p>If you don't want to be notify about this. You need to review your user preferences.</p>\n  </body>\n</html>",
        )

    def test_notification_job_undefined_last_backup_date(self):
        # Given a valid user with a repository configured for notification
        user = UserObject.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.add().commit()
        # Given a repo with last_backup_date None
        repo = RepoObject.query.filter(RepoObject.user == user, RepoObject.repopath == 'broker-repo').first()
        repo.maxage = 1
        repo.add().commit()
        self.assertIsNone(repo.last_backup_date)

        # When Notification job is running
        cherrypy.notification.notification_job()

        # Then a notification is sent to the user.
        self.listener.queue_email.assert_called_once_with(
            to='test@test.com',
            subject='Notification',
            message="<html>\n  <head></head>\n  <body>\n    <p>\n      <a>Hey admin,</a>\n    </p>\n    <p>\n      You are receiving this email to notify you about your backups. The\n      following repositories are inactive for some time. We invite you to have a look\n      at your last backup schedule.\n    </p>\n    <ul>\n      \n        <li>\n          <a>broker-repo</a>\n        </li>\n      \n    </ul>\n    <p>If you don't want to be notify about this. You need to review your user preferences.</p>\n  </body>\n</html>",
        )

    def test_notification_job_without_notification(self):
        # Given a valid user with a repository configured without notification (-1)
        user = UserObject.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.add().commit()
        repo = RepoObject.query.filter(RepoObject.user == user, RepoObject.repopath == self.REPO).first()
        repo.maxage = -1
        repo.add().commit()

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
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When updating the user's email
        user = UserObject.get_user(self.USERNAME)
        user.email = 'email_changed@test.com'
        user.add().commit()

        # Then a email is queue to notify the user.
        self.listener.queue_email.assert_called_once_with(
            to='original_email@test.com',
            subject='Email address changed',
            message='<html>\n  <head></head>\n  <body>\n    <p>\n      <a>Hey admin,</a>\n    </p>\n    <p>\n      <a>You recently changed the email address associated with your Rdiffweb account.</a>\n    </p>\n    <p>\n      If you did not make this change and believe your account has been compromised, please contact your administrator.\n    </p>\n  </body>\n</html>',
        )

    def test_email_updated_with_same_value(self):
        # Given a user with an email
        user = UserObject.get_user(self.USERNAME)
        user.email = 'email_changed@test.com'
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When updating the user's email with the same value
        user.email = 'email_changed@test.com'
        user.add().commit()

        # Then no email are sent to the user
        self.listener.queue_email.assert_not_called()

    def test_password_change_notification(self):
        # Given a user with a email.
        user = UserObject.get_user(self.USERNAME)
        user.email = 'password_change@test.com'
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When updating the user password
        user.set_password('new_password')
        user.add().commit()

        # Then a email is send to the user
        self.listener.queue_email.assert_called_once_with(
            to='password_change@test.com',
            subject='Password changed',
            message='<html>\n  <head></head>\n  <body>\n    <p>\n      <a>Hey admin,</a>\n    </p>\n    <p>You recently changed the password associated with your Rdiffweb account.</p>\n    <p>\n      If you did not make this change and believe your account has been compromised, please contact your administrator.\n    </p>\n  </body>\n</html>',
        )

    def test_password_change_with_same_value(self):
        # Given a user with a email.
        user = UserObject.get_user(self.USERNAME)
        user.email = 'password_change@test.com'
        user.set_password('new_password')
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When updating the user password with the same value
        user.set_password('new_password')
        user.add().commit()

        # Then an email is sent to the user
        self.listener.queue_email.assert_called_once_with(
            to='password_change@test.com',
            subject='Password changed',
            message='<html>\n  <head></head>\n  <body>\n    <p>\n      <a>Hey admin,</a>\n    </p>\n    <p>You recently changed the password associated with your Rdiffweb account.</p>\n    <p>\n      If you did not make this change and believe your account has been compromised, please contact your administrator.\n    </p>\n  </body>\n</html>',
        )

    def test_access_token_added(self):
        # Given a user with a email.
        user = UserObject.get_user(self.USERNAME)
        user.email = 'password_change@test.com'
        user.set_password('new_password')
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When adding a new access token
        user.add_access_token('TEST')

        # Then a notification is sent to the user
        self.listener.queue_email.assert_called_once_with(
            to='password_change@test.com',
            subject='A new access token has been created',
            message='<html>\n  <head></head>\n  <body>\n    <p>\n      <a>Hey admin,</a>\n    </p>\n    <p>\n      <a>A new access token, named "TEST", has been created.</a>\n    </p>\n    <p>\n      If you did not make this change and believe your account has been compromised, please contact your administrator.\n    </p>\n  </body>\n</html>',
        )

    def test_authorizedkey_added(self):
        # Given a user with a email.
        user = UserObject.get_user(self.USERNAME)
        user.email = 'password_change@test.com'
        user.set_password('new_password')
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When adding a new access token
        user.add_authorizedkey(
            key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
            comment="test@mysshkey",
        )

        # Then a notification is sent to the user
        self.listener.queue_email.assert_called_once_with(
            to='password_change@test.com',
            subject='A new SSH Key has been added',
            message='<html>\n  <head></head>\n  <body>\n    <p>\n      <a>Hey admin,</a>\n    </p>\n    <p>\n      <a>A new SSH Key, titled "test@mysshkey" with fingerprint "4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91" has been created in your account.</a>\n    </p>\n    <p>\n      If you did not make this change and believe your account has been compromised, please contact your administrator.\n    </p>\n  </body>\n</html>',
        )
