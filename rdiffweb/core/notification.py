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
Plugin used to send email to users when their repository is getting too old.
User can control the notification period.
"""

import logging

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from rdiffweb.core.model import RepoObject, UserObject
from rdiffweb.tools.i18n import ugettext as _

logger = logging.getLogger(__name__)
activity = logging.getLogger('activity')
auth = logging.getLogger('auth')


class NotificationPlugin(SimplePlugin):
    """
    Send email notification when a repository get too old (without a backup).
    """

    env = None  # Jinja2 env

    execution_time = '23:00'

    send_changed = False

    bcc = None

    header_name = 'rdiffweb'

    link_color = '#35979c'

    navbar_color = '#383e45'

    def start(self):
        self.bus.log('Start Notification plugin')
        self.bus.publish('schedule_job', self.execution_time, self.notification_job)
        self.bus.subscribe('access_token_added', self.access_token_added)
        self.bus.subscribe('authorizedkey_added', self.authorizedkey_added)
        self.bus.subscribe('user_attr_changed', self.user_attr_changed)
        self.bus.subscribe('user_password_changed', self.user_password_changed)
        self.bus.subscribe('repo_added', self.repo_added)
        self.bus.subscribe('repo_deleted', self.repo_deleted)
        self.bus.subscribe('user_added', self.user_added)
        self.bus.subscribe('user_deleted', self.user_deleted)
        self.bus.subscribe('user_login', self.user_login)

    start.priority = 55

    def stop(self):
        self.bus.log('Stop Notification plugin')
        self.bus.publish('unschedule_job', self.notification_job)
        self.bus.unsubscribe('access_token_added', self.access_token_added)
        self.bus.unsubscribe('authorizedkey_added', self.authorizedkey_added)
        self.bus.unsubscribe('user_attr_changed', self.user_attr_changed)
        self.bus.unsubscribe('user_password_changed', self.user_password_changed)
        self.bus.unsubscribe('repo_added', self.repo_added)
        self.bus.unsubscribe('repo_deleted', self.repo_deleted)
        self.bus.unsubscribe('user_added', self.user_added)
        self.bus.unsubscribe('user_deleted', self.user_deleted)
        self.bus.unsubscribe('user_login', self.user_login)

    stop.priority = 45

    def _queue_mail(self, userobj, subject, template, to=None, **kwargs):
        """
        Generic function to queue email.
        """
        to = userobj.email if to is None else to
        if not to and not self.bcc:
            logger.info("can't sent mail to user [%s] without an email", userobj.username)
            return

        # Also send email to catch-all email.
        queue_mail_kwargs = {}
        if self.bcc:
            queue_mail_kwargs['bcc'] = self.bcc

        # Add branding variable to template creation.
        param = {
            'header_name': self.header_name,
            'font_family': 'Open Sans',
            'link_color': self.link_color,
            'navbar_color': self.navbar_color,
        }
        # Compile the email body
        body = self.env.compile_template(template, user=userobj, **dict(param, **kwargs))
        # Queue the email.
        self.bus.publish('queue_mail', to=to, subject=subject, message=body, **queue_mail_kwargs)

    def access_token_added(self, userobj, name):
        username = userobj.username
        activity.info(f"A new access token {name} for the user {username} has been added")
        if self.send_changed:
            self._queue_mail(
                userobj,
                subject=_("A new access token has been created"),
                template="email_access_token_added.html",
                name=name,
            )

    def authorizedkey_added(self, userobj, fingerprint, comment, **kwargs):
        username = userobj.username
        activity.info(f"A new SSH key {fingerprint} has been added for the user {username}")
        if self.send_changed:
            self._queue_mail(
                userobj,
                subject=_("A new SSH Key has been added"),
                template="email_authorizedkey_added.html",
                comment=comment,
                fingerprint=fingerprint,
            )

    def user_attr_changed(self, userobj, attrs={}):
        username = userobj.username
        # Leave if the mail was not changed.
        if 'email' in attrs:
            activity.info(f"Email address of the user {username} has been changed")
            # If the email attributes was changed, send a mail notification.
            if self.send_changed:
                old_email = attrs['email'][0]
                self._queue_mail(
                    userobj,
                    to=old_email,
                    subject=_("Email address changed"),
                    template="email_changed.html",
                )

        if 'mfa' in attrs:
            state = 'activated' if userobj.mfa == UserObject.DISABLED_MFA else 'disabled'
            activity.info(f"Two-factor authentication has been {state} for the user {username}")
            if self.send_changed:
                subject = (
                    _("Two-Factor Authentication turned off")
                    if userobj.mfa == UserObject.DISABLED_MFA
                    else _("Two-Factor Authentication turned on")
                )
                self._queue_mail(
                    userobj,
                    subject=subject,
                    template="email_mfa.html",
                )

    def user_password_changed(self, userobj):
        username = userobj.username
        activity.info(f"User's password {username} changed")
        if self.send_changed:
            self._queue_mail(
                userobj,
                subject=_("Password changed"),
                template="email_password_changed.html",
            )

    def repo_added(self, userobj, repo_path):
        username = userobj.username
        activity.info(f"New repository named {repo_path} has been added for the user {username}")
        if self.send_changed:
            self._queue_mail(
                userobj,
                subject=_("New Repository detected"),
                template="email_repo_added.html",
                repo_path=repo_path,
            )

    def repo_deleted(self, userobj, repo_path):
        username = userobj.username
        activity.info(f"Repository {repo_path} of the user {username} has been deleted")
        if self.send_changed:
            self._queue_mail(
                userobj,
                subject=_("Repository deleted"),
                template="email_repo_deleted.html",
                repo_path=repo_path,
            )

    def user_added(self, userobj):
        username = userobj.username
        activity.info(f"New user {username} has been added")

    def user_deleted(self, username):
        activity.info(f"User {username} has been deleted")

    def user_login(self, userobj):
        username = userobj.username
        auth.info(f"User {username} login to web application")

    def notification_job(self):
        """
        Loop trough all the user repository and send notifications.
        """

        # For Each user with an email.
        # Identify the repository without activities using the backup statistics.
        for userobj in UserObject.query.filter(UserObject.email != ''):
            old_repos = [
                repo
                for repo in RepoObject.query.filter(RepoObject.user == userobj, RepoObject.maxage > 0)
                if not repo.check_activity()
            ]
            if old_repos:
                self._queue_mail(
                    userobj,
                    subject=_("Notification"),
                    template="email_notification.html",
                    repos=old_repos,
                )


cherrypy.notification = NotificationPlugin(cherrypy.engine)
cherrypy.notification.subscribe()

cherrypy.config.namespaces['notification'] = lambda key, value: setattr(cherrypy.notification, key, value)
