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

import datetime
import logging

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from rdiffweb.core import librdiff
from rdiffweb.core.model import UserObject
from rdiffweb.tools.i18n import ugettext as _

logger = logging.getLogger(__name__)


class NotificationPlugin(SimplePlugin):
    """
    Send email notification when a repository get too old (without a backup).
    """

    execution_time = '23:00'

    send_changed = False

    def start(self):
        self.bus.log('Start Notification plugin')
        self.bus.publish('schedule_job', self.execution_time, self.notification_job)
        self.bus.subscribe('access_token_added', self.access_token_added)
        self.bus.subscribe('authorizedkey_added', self.authorizedkey_added)
        self.bus.subscribe('user_attr_changed', self.user_attr_changed)
        self.bus.subscribe('user_password_changed', self.user_password_changed)

    start.priority = 55

    def stop(self):
        self.bus.log('Stop Notification plugin')
        self.bus.publish('unschedule_job', self.notification_job)
        self.bus.unsubscribe('access_token_added', self.access_token_added)
        self.bus.unsubscribe('authorizedkey_added', self.authorizedkey_added)
        self.bus.unsubscribe('user_attr_changed', self.user_attr_changed)
        self.bus.unsubscribe('user_password_changed', self.user_password_changed)

    stop.priority = 45

    @property
    def app(self):
        return cherrypy.tree.apps['']

    def access_token_added(self, userobj, name):
        if not self.send_changed:
            return

        if not userobj.email:
            logger.info("can't sent mail to user [%s] without an email", userobj.username)
            return

        # Send a mail notification
        body = self.app.templates.compile_template(
            "email_access_token_added.html", **{"header_name": self.app.cfg.header_name, 'user': userobj, 'name': name}
        )
        self.bus.publish('queue_mail', to=userobj.email, subject=_("A new access token has been created"), message=body)

    def authorizedkey_added(self, userobj, fingerprint, comment, **kwargs):
        if not self.send_changed:
            return

        if not userobj.email:
            logger.info("can't sent mail to user [%s] without an email", userobj.username)
            return

        # If the email attributes was changed, send a mail notification.
        body = self.app.templates.compile_template(
            "email_authorizedkey_added.html",
            **{"header_name": self.app.cfg.header_name, 'user': userobj, 'comment': comment, 'fingerprint': fingerprint}
        )
        self.bus.publish('queue_mail', to=userobj.email, subject=_("A new SSH Key has been added"), message=body)

    def user_attr_changed(self, userobj, attrs={}):
        if not self.send_changed:
            return

        # Leave if the mail was not changed.
        if 'email' in attrs:
            old_email = attrs['email'][0]
            if not old_email:
                logger.info("can't sent mail to user [%s] without an email", userobj.username)
                return
            # If the email attributes was changed, send a mail notification.
            subject = _("Email address changed")
            body = self.app.templates.compile_template(
                "email_changed.html", **{"header_name": self.app.cfg.header_name, 'user': userobj}
            )
            self.bus.publish('queue_mail', to=old_email, subject=str(subject), message=body)

        if 'mfa' in attrs:
            if not userobj.email:
                logger.info("can't sent mail to user [%s] without an email", userobj.username)
                return
            subject = (
                _("Two-Factor Authentication turned off")
                if userobj.mfa == UserObject.DISABLED_MFA
                else _("Two-Factor Authentication turned on")
            )
            body = self.app.templates.compile_template(
                "email_mfa.html", **{"header_name": self.app.cfg.header_name, 'user': userobj}
            )
            self.bus.publish('queue_mail', to=userobj.email, subject=str(subject), message=body)

    def user_password_changed(self, userobj):
        if not self.send_changed:
            return

        if not userobj.email:
            logger.info("can't sent mail to user [%s] without an email", userobj.username)
            return

        # If the email attributes was changed, send a mail notification.
        body = self.app.templates.compile_template(
            "email_password_changed.html", **{"header_name": self.app.cfg.header_name, 'user': userobj}
        )
        self.bus.publish('queue_mail', to=userobj.email, subject=_("Password changed"), message=body)

    def notification_job(self):
        """
        Loop trough all the user repository and send notifications.
        """

        now = librdiff.RdiffTime()

        def _user_repos():
            """Return a generator trought user repos to be notified."""
            for user in UserObject.query.all():
                # Check if user has email.
                if not user.email:
                    continue
                # Identify old repo for current user.
                old_repos = []
                for repo in user.repo_objs:
                    # Check if repo has age configured (in days)
                    maxage = repo.maxage
                    if not maxage or maxage <= 0:
                        continue
                    # Check repo age.
                    if repo.last_backup_date is None or repo.last_backup_date < (now - datetime.timedelta(days=maxage)):
                        old_repos.append(repo)
                # Return an item only if user had old repo
                if old_repos:
                    yield user, old_repos

        # For each candidate, send mail.
        for user, repos in _user_repos():
            parms = {'user': user, 'repos': repos}
            body = self.app.templates.compile_template("email_notification.html", **parms)
            cherrypy.engine.publish('queue_mail', to=user.email, subject=_("Notification"), message=body)


cherrypy.notification = NotificationPlugin(cherrypy.engine)
cherrypy.notification.subscribe()

cherrypy.config.namespaces['notification'] = lambda key, value: setattr(cherrypy.notification, key, value)
