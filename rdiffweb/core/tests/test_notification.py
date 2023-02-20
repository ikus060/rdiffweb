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
from unittest.mock import ANY, MagicMock

import cherrypy

import rdiffweb.core.notification
import rdiffweb.test
from rdiffweb.core.model import RepoObject, UserObject


class AbstractNotificationTest(rdiffweb.test.WebCase):
    def setUp(self):
        self.listener = MagicMock()
        cherrypy.engine.subscribe('queue_mail', self.listener.queue_email, priority=50)
        return super().setUp()

    def tearDown(self):
        cherrypy.engine.unsubscribe('queue_mail', self.listener.queue_email)
        return super().tearDown()


class NotificationJobTest(AbstractNotificationTest):
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
        self.listener.queue_email.reset_mock()
        # When running notification_job
        cherrypy.notification.notification_job()

        # Then an email is queue for this user
        self.listener.queue_email.assert_called_once_with(
            to='test@test.com',
            subject='Notification',
            message=ANY,
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
        self.listener.queue_email.reset_mock()
        # When Notification job is running
        cherrypy.notification.notification_job()

        # Then a notification is sent to the user.
        self.listener.queue_email.assert_called_once_with(
            to='test@test.com',
            subject='Notification',
            message=ANY,
        )

    def test_notification_job_without_notification(self):
        # Given a valid user with a repository configured without notification (-1)
        user = UserObject.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.add().commit()
        repo = RepoObject.query.filter(RepoObject.user == user, RepoObject.repopath == self.REPO).first()
        repo.maxage = -1
        repo.add().commit()
        self.listener.queue_email.reset_mock()

        # Call notification.
        cherrypy.notification.notification_job()

        # Mail should not be queue.
        self.listener.queue_email.assert_not_called()


class NotificationPluginTest(AbstractNotificationTest):

    default_config = {
        'email-send-changed-notification': True,
    }

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
            message=ANY,
        )

    def test_email_updated_with_same_value(self):
        # Given a user with an email
        user = UserObject.get_user(self.USERNAME)
        user.email = 'email_changed@test.com'
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When updating the user's email with the same value
        user = UserObject.get_user(self.USERNAME)
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
            message=ANY,
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
            message=ANY,
        )

    def test_access_token_added(self):
        # Given a user with a email.
        user = UserObject.get_user(self.USERNAME)
        user.email = 'myemail@test.com'
        user.set_password('new_password')
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When adding a new access token
        user.add_access_token('TEST')
        user.commit()

        # Then a notification is sent to the user
        self.listener.queue_email.assert_called_once_with(
            to='myemail@test.com',
            subject='A new access token has been created',
            message=ANY,
        )

    def test_authorizedkey_added(self):
        # Given a user with a email.
        user = UserObject.get_user(self.USERNAME)
        user.email = 'myemail@test.com'
        user.set_password('new_password')
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When adding a new access token
        user.add_authorizedkey(
            key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
            comment="test@mysshkey",
        )
        user.commit()

        # Then a notification is sent to the user
        self.listener.queue_email.assert_called_once_with(
            to='myemail@test.com',
            subject='A new SSH Key has been added',
            message=ANY,
        )

    def test_user_added(self):
        # Given an empty database
        self.listener.queue_email.reset_mock()
        # When adding a new user to database
        user = UserObject.add_user('newuser')
        user.commit()
        # Then event is raised
        self.listener.queue_email.assert_not_called()

    def test_user_deleted(self):
        # Given a database with a new username
        user = UserObject.add_user('newuser')
        user.commit()
        self.listener.queue_email.reset_mock()
        # When deleting that user
        user.delete()
        user.commit()
        # Then event is raised
        self.listener.queue_email.assert_not_called()

    def test_repo_added(self):
        # Given a database with a user
        user = UserObject.add_user('newuser')
        user.email = 'myemail@test.com'
        user.commit()
        self.listener.queue_email.reset_mock()
        # When adding new repositories
        user.user_root = self.testcases
        user.refresh_repos()
        user.commit()
        # Then a notification is sent to the user
        self.listener.queue_email.assert_any_call(
            to='myemail@test.com',
            subject='New Repository detected',
            message=ANY,
        )

    def test_repo_deleted(self):
        # Given a database with a user with repo
        user = UserObject.add_user('newuser')
        user.email = 'myemail@test.com'
        user.user_root = self.testcases
        user.refresh_repos()
        user.commit()
        self.listener.queue_email.reset_mock()
        # When deleting a repo new repositories
        repo = RepoObject.get_repo('newuser/testcases', as_user=user)
        repo.delete()
        repo.commit()
        # Then a notification is sent to the user
        self.listener.queue_email.assert_called_once_with(
            to='myemail@test.com',
            subject='Repository deleted',
            message=ANY,
        )


class NotificationConfigTest(AbstractNotificationTest):

    default_config = {
        'email-send-changed-notification': True,
        'link-color': '123456',
        'navbar-color': '7890ab',
        'header-name': 'MyHeaderName',
    }

    def test_notification_config(self):
        # Given specific branding configuration
        # When sending an email using the notification plugin
        user = UserObject.get_user(self.USERNAME)
        user.email = 'original_email@test.com'
        user.add().commit()
        self.listener.queue_email.reset_mock()
        user.email = 'email_changed@test.com'
        user.add().commit()
        # Then an email is sent to the user
        self.listener.queue_email.assert_called_once()
        # Then the email is customized with the branding
        message = self.listener.queue_email.call_args[1]['message']
        self.assertIn('#123456', message)
        self.assertIn('#7890ab', message)
        self.assertIn('MyHeaderName', message)


class NotificationCatchAllTest(AbstractNotificationTest):

    default_config = {'email-send-changed-notification': True, 'email-catch-all': 'all@examples.com'}

    def test_notification_catch_all(self):
        # Given a catch all email.
        # When sending an email.
        user = UserObject.get_user(self.USERNAME)
        user.email = 'myemail@test.com'
        user.add().commit()
        self.listener.queue_email.reset_mock()
        user.add_access_token('TEST')
        user.commit()
        # Then email is also sent to catch-all
        self.listener.queue_email.assert_called_once_with(
            to='myemail@test.com',
            subject='A new access token has been created',
            message=ANY,
            bcc='all@examples.com',
        )
