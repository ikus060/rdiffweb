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

    def _queue_mail(self, userobj, subject, template, to=None, **kwargs):
        """
        Generic function to queue email.
        """
        if not userobj.email:
            logger.info("can't sent mail to user [%s] without an email", userobj.username)
            return

        # Mimic the behavior of CSS style for email template.
        cfg = self.app.cfg
        param = {
            'header_name': self.app.cfg.header_name,
            'font_family': 'Open Sans',
        }
        if cfg.default_theme == 'default':
            param.update({'link_color': '#35979c', 'navbar_color': '#383e45'})
            for key in ['link_color', 'btn_bg_color', 'btn_fg_color', 'navbar_color', 'font_family']:
                if getattr(cfg, key, None):
                    param[key] = getattr(cfg, key, None)
        elif cfg.default_theme == 'blue':
            param.update({'link_color': '#153a58', 'navbar_color': '#153a58'})
        elif cfg.default_theme == 'orange':
            param.update({'link_color': '#dd4814', 'navbar_color': '#dd4814'})

        # Compile the email body
        body = self.app.templates.compile_template(template, user=userobj, **dict(param, **kwargs))
        # Queue the email.
        self.bus.publish('queue_mail', to=to or userobj.email, subject=subject, message=body)

    def access_token_added(self, userobj, name):
        if not self.send_changed:
            return

        self._queue_mail(
            userobj,
            subject=_("A new access token has been created"),
            template="email_access_token_added.html",
            name=name,
        )

    def authorizedkey_added(self, userobj, fingerprint, comment, **kwargs):
        if not self.send_changed:
            return
        self._queue_mail(
            userobj,
            subject=_("A new SSH Key has been added"),
            template="email_authorizedkey_added.html",
            comment=comment,
            fingerprint=fingerprint,
        )

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
            self._queue_mail(
                userobj,
                to=old_email,
                subject=_("Email address changed"),
                template="email_changed.html",
            )

        if 'mfa' in attrs:
            if not userobj.email:
                logger.info("can't sent mail to user [%s] without an email", userobj.username)
                return
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
        if not self.send_changed:
            return

        self._queue_mail(
            userobj,
            subject=_("Password changed"),
            template="email_password_changed.html",
        )

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
