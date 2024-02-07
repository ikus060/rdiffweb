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
Created on Feb 13, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""
from datetime import datetime, timedelta, timezone
from unittest import skipIf
from unittest.mock import ANY, MagicMock

import cherrypy
import responses
from parameterized import parameterized

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
    def setUp(self):
        super().setUp()
        cherrypy.engine.subscribe("get_disk_quota", self.listener.get_disk_quota, priority=40)
        self.listener.get_disk_quota.return_value = False

    def tearDown(self):
        cherrypy.engine.unsubscribe("get_disk_quota", self.listener.get_disk_quota)
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

    def test_notification_job_disk_usage(self):
        # Given a user with an email address and a disk quota
        # Set user config
        user = UserObject.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.commit()
        self.listener.get_disk_quota.return_value = user.disk_usage
        # Given a user with a repo without max age.
        repo = RepoObject.query.filter(RepoObject.user == user, RepoObject.repopath == self.REPO).first()
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

    @parameterized.expand(
        [
            ('disabled', 0, None, None),
            ('daily_never_sent', 1, None, 'Daily Backup Report'),
            ('daily_sent_today', 1, 0, None),
            ('daily_sent_yesterday', 1, 1, None),
            ('daily_sent_two_day_ago', 1, 2, 'Daily Backup Report'),
            ('weekly_never_sent', 7, None, 'Weekly Backup Report'),
            ('weekly_sent_today', 7, 0, None),
            ('weekly_sent_yesterday', 7, 1, None),
            ('weekly_sent_12_days_ago', 7, 12, None),
            ('weekly_sent_13_days_ago', 7, 13, 'Weekly Backup Report'),
            ('monthly_never_sent', 30, None, 'Monthly Backup Report'),
            ('monthly_sent_today', 30, 0, None),
            ('monthly_sent_yesterday', 30, 1, None),
            ('monthly_sent_31_days_ago', 30, 31, None),
            ('monthly_sent_1_month_ago', 30, 32, 'Monthly Backup Report'),
            ('random_never_sent', 4, None, 'Backup Report'),
        ]
    )
    def test_report_job(self, unused, time_range, last_sent, expected_subject):
        # Given we are the 1 April 2023, Saturday
        now = datetime(2023, 4, 1, 14, 39, 16, tzinfo=timezone(timedelta(hours=-4)))
        # Given a user with an email address and report time range
        # Set user config
        user = UserObject.get_user(self.USERNAME)
        user.email = 'test@test.com'
        user.report_time_range = time_range
        user.report_last_sent = now - timedelta(days=last_sent) if last_sent is not None else None
        user.commit()
        self.listener.queue_email.reset_mock()
        # When running notification_job
        cherrypy.notification.report_job(_now=now)

        # Then an email is queue for this user
        if expected_subject:
            self.listener.queue_email.assert_called_once_with(
                to='test@test.com',
                subject=expected_subject,
                message=ANY,
            )
            user.expire()
            self.assertIsNotNone(user.report_last_sent)
        else:
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

    def test_user_lang(self):
        # Given a user's with prefered language
        user = UserObject.get_user(self.USERNAME)
        user.email = 'myemail@test.com'
        user.lang = 'fr'
        user.add().commit()
        self.listener.queue_email.reset_mock()

        # When sending notification to that user
        user.add_access_token('TEST')
        user.commit()

        # Then the mail is sent with the prefered language
        self.listener.queue_email.assert_called_once_with(
            to='myemail@test.com',
            subject="Un nouveau jeton d'accès a été créé",
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


class NotificationLatest(AbstractNotificationTest):
    url = 'https://latest.ikus-soft.com/rdiffweb/latest_version'

    default_config = {'latest-version-url': url}

    @skipIf(rdiffweb.__version__ == 'DEV', 'not working with dev version')
    @responses.activate
    def test_check_latest_job_with_upgrade(self):
        # Given an administrator
        adminobj = UserObject.get_user(self.USERNAME)
        adminobj.email = 'admin@example.com'
        adminobj.add().commit()
        # Given a user
        userobj = UserObject(username='user')
        userobj.email = 'user@examples.com'
        userobj.add().commit()
        # Given the application may be upgraded
        responses.add(responses.GET, self.url, body='9.9.9')
        # When running the check_latest_job
        cherrypy.notification.check_latest_job()
        # Then an email is only sent to the adminstrator
        self.listener.queue_email.assert_called_once_with(
            to='admin@example.com',
            subject='Upgrade available for Rdiffweb',
            message=ANY,
        )

    @responses.activate
    def test_check_latest_job_without_upgrade(self):
        # Given an administrator
        adminobj = UserObject.get_user(self.USERNAME)
        adminobj.email = 'admin@example.com'
        adminobj.add().commit()
        # Given the application may be upgraded
        responses.add(responses.GET, self.url, body='0.0.1')
        # When running the check_latest_job
        cherrypy.notification.check_latest_job()
        # Then an email is send to the adminstrator
        self.listener.queue_email.assert_not_called()
