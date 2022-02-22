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
from rdiffweb.tools.i18n import ugettext as _

logger = logging.getLogger(__name__)


class NotificationPlugin(SimplePlugin):
    """
    Send email notification when a repository get too old (without a backup).
    """

    def __init__(self, bus):
        super().__init__(bus)
        self.bus.subscribe('user_attr_changed', self.user_attr_changed)
        self.bus.subscribe('user_password_changed', self.user_password_changed)
        self.bus.subscribe('stop', self.stop)

    def stop(self):
        self.bus.unsubscribe('user_attr_changed', self.user_attr_changed)
        self.bus.unsubscribe('user_password_changed', self.user_password_changed)
        self.bus.unsubscribe('stop', self.stop)

    @property
    def app(self):
        return cherrypy.tree.apps['']

    def user_attr_changed(self, userobj, attrs={}):
        # Leave if the mail was not changed.
        if 'email' not in attrs:
            return

        if not userobj.email:
            logger.info("can't sent mail to user [%s] without an email", userobj.username)
            return

        # If the email attributes was changed, send a mail notification.
        body = self.app.templates.compile_template("email_changed.html", **{"header_name": self.app.cfg.header_name, 'user': userobj})
        self.bus.publish('queue_mail', to=userobj.email, subject=_("Email address changed"), message=body)

    def user_password_changed(self, userobj):

        if not userobj.email:
            logger.info(
                "can't sent mail to user [%s] without an email", userobj.username)
            return

        # If the email attributes was changed, send a mail notification.
        body = self.app.templates.compile_template("password_changed.html", **{"header_name": self.app.cfg.header_name, 'user': userobj})
        self.bus.publish('queue_mail', to=userobj.email, subject=_("Password changed"), message=body)


def notification_job(app):
    """
    Loop trough all the user repository and send notifications.
    """

    now = librdiff.RdiffTime()

    def _user_repos():
        """Return a generator trought user repos to be notified."""
        for user in app.store.users():
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
        body = app.templates.compile_template("email_changed.html", **parms)
        cherrypy.engine.publish('queue_mail', to=user.email, subject=_("Notification"), message=body)
