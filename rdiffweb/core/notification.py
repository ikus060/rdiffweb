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
Plugin used to send email to users when their repository is getting too old.
User can control the notification period.
"""
import logging
import platform
import re
from datetime import datetime, timedelta, timezone

import cherrypy
import distro
import requests
from cherrypy.process.plugins import SimplePlugin
from packaging.version import InvalidVersion, Version
from sqlalchemy import func, or_

from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import RepoObject, UserObject
from rdiffweb.tools.i18n import preferred_lang
from rdiffweb.tools.i18n import ugettext as _

logger = logging.getLogger(__name__)
activity = logging.getLogger('activity')
auth = logging.getLogger('auth')


def _sum(iterable):
    if len(iterable) == 0:
        return None
    return sum(iterable)


def _avg(iterable):
    if len(iterable) == 0:
        return None
    return sum(iterable) / len(iterable)


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

    current_version = None

    latest_version_url = None

    def start(self):
        self.bus.log('Start Notification plugin')
        self.bus.publish('schedule_job', self.execution_time, self.check_latest_job)
        self.bus.publish('schedule_job', self.execution_time, self.notification_job)
        self.bus.publish('schedule_job', self.execution_time, self.report_job)
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
        self.bus.publish('unschedule_job', self.check_latest_job)
        self.bus.publish('unschedule_job', self.notification_job)
        self.bus.publish('unschedule_job', self.report_job)
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

    def _is_latest(self):
        """
        Check if the current minarca client is up to date.

        Return True if latest
        False if old
        None if undeterminate.
        """
        # Skip verification if not configured
        if self.current_version is None or self.latest_version_url is None:
            return None

        # Get current version.
        try:
            current_version = Version(self.current_version)
        except InvalidVersion:
            logger.warning('invalid current_version: ' + self.current_version, exc_info=1)
            return None

        # Get latest version
        try:
            headers = {
                'User-Agent': f'{self.header_name}-server/{current_version} python/{platform.python_version()} {platform.system()}/{platform.release()} ({distro.name(True)} {platform.machine()})'
            }
            response = requests.get(self.latest_version_url, headers=headers, timeout=0.5)
            response.raise_for_status()
            latest_version = Version(response.text)
        except requests.exceptions.RequestException:
            logger.warning('fail to get latest version', exc_info=1)
            return None

        # Compare them
        return current_version >= latest_version

    def _queue_mail(self, userobj, template, to=None, **kwargs):
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
        with preferred_lang(userobj.lang):
            message_body = self.env.compile_template(template, user=userobj, **dict(param, **kwargs))
            # Extract subject from template
            match = re.search(r'<title>(.*)</title>', message_body, re.DOTALL)
            subject = match and match.group(1).replace('\n', '').strip()
        subject = subject or _('Notification')
        # Queue the email.
        self.bus.publish('queue_mail', to=to, subject=subject, message=message_body, **queue_mail_kwargs)

    def access_token_added(self, userobj, name):
        username = userobj.username
        activity.info(f"A new access token {name} for the user {username} has been added")
        if self.send_changed:
            self._queue_mail(
                userobj,
                template="email_access_token_added.html",
                name=name,
            )

    def authorizedkey_added(self, userobj, fingerprint, comment, **kwargs):
        username = userobj.username
        activity.info(f"A new SSH key {fingerprint} has been added for the user {username}")
        if self.send_changed:
            self._queue_mail(
                userobj,
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
                    template="email_changed.html",
                )

        if 'mfa' in attrs:
            state = 'activated' if userobj.mfa == UserObject.DISABLED_MFA else 'disabled'
            activity.info(f"Two-factor authentication has been {state} for the user {username}")
            if self.send_changed:
                self._queue_mail(
                    userobj,
                    template="email_mfa.html",
                )

    def user_password_changed(self, userobj):
        username = userobj.username
        activity.info(f"User's password {username} changed")
        if self.send_changed:
            self._queue_mail(
                userobj,
                template="email_password_changed.html",
            )

    def repo_added(self, userobj, repo_path):
        username = userobj.username
        activity.info(f"New repository named {repo_path} has been added for the user {username}")
        if self.send_changed:
            self._queue_mail(
                userobj,
                template="email_repo_added.html",
                repo_path=repo_path,
            )

    def repo_deleted(self, userobj, repo_path):
        username = userobj.username
        activity.info(f"Repository {repo_path} of the user {username} has been deleted")
        if self.send_changed:
            self._queue_mail(
                userobj,
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
        now = RdiffTime()
        for userobj in UserObject.query.filter(UserObject.email != ''):
            try:
                # Identify the repository without activities using the backup statistics.
                old_repos = [
                    repo
                    for repo in RepoObject.query.filter(RepoObject.user == userobj, RepoObject.maxage > 0)
                    if not repo.check_activity()
                    if now.weekday not in repo.ignore_weekday
                ]
                # Check user's disk usage
                disk_usage = userobj.disk_usage
                disk_quota = userobj.disk_quota
                used_pct = disk_usage / disk_quota * 100 if disk_quota else 0
                # Send email if required
                if old_repos or used_pct > 90:
                    self._queue_mail(
                        userobj,
                        template="email_notification.html",
                        repos=old_repos,
                        disk_usage=disk_usage,
                        disk_quota=disk_quota,
                    )
            except Exception:
                logger.exception('fail to send notification to user %s', userobj)

    def check_latest_job(self):
        """
        Check if running latest version.
        """
        # Check if current version and send email to administrator if required
        if self._is_latest() is False:
            for userobj in UserObject.query.filter(UserObject.email != '', UserObject.role == UserObject.ADMIN_ROLE):
                self._queue_mail(
                    userobj,
                    template="email_latest.html",
                )

    def report_job(self, _now=None):
        """
        Loop trough all the user to sent backup report.

        _now is only used for testing
        """
        # For each user that want to receive a report.
        sql_now = int(_now.timestamp()) if _now else func.epoch(func.now())
        query = UserObject.query.filter(
            UserObject.email != '',
            UserObject.report_time_range > 0,
            or_(
                UserObject.report_last_sent.is_(None),
                (sql_now - func.epoch(UserObject.report_last_sent)) > (UserObject.report_time_range * 86400),
            ),
        )
        for userobj in query.all():
            try:
                if self.send_report(userobj, _now=_now):
                    userobj.report_last_sent = datetime.now(tz=timezone.utc)
                    userobj.add()
                    userobj.commit()
            except Exception:
                # In case of error, continue with next user.
                userobj.rollback()
                logger.exception('fail to send report to user %s', userobj)

    def send_report(self, userobj, force=False, _now=None):
        """
        Generate the repport data to be sent.
        """
        # Compute the start & end time for the repport using server timezone
        assert userobj.report_time_range, 'invalid time_range'
        time_range = userobj.report_time_range
        now = RdiffTime(_now).astimezone().replace(hour=0, minute=0, second=0)
        if time_range == 30:
            # Monthly
            end_time = now - timedelta(days=now.day - 1)
            start_time = (end_time - timedelta(days=27)).replace(day=1)
        elif time_range == 7:
            # Weekly
            end_time = now - timedelta(days=now.weekday())
            start_time = end_time - timedelta(days=time_range)
        else:
            # Other
            end_time = now
            start_time = end_time - timedelta(days=time_range)

        # Check if we need to sent a new report
        if not force and userobj.report_last_sent is not None and RdiffTime(userobj.report_last_sent) > start_time:
            return False

        # Compute the data for each repository
        data = []
        for repo in sorted(userobj.repo_objs, key=lambda r: r.display_name):
            data.append(
                {
                    'display_name': repo.display_name,
                    'last_backup_date': repo.last_backup_date,
                    'maxage': repo.maxage,
                    'status': repo.status,
                }
            )
            try:
                stats = repo.session_statistics[start_time:end_time]
                data[-1].update(
                    {
                        'elapsedtime': _avg([s.elapsedtime for s in stats]),
                        'newfiles': _sum([s.newfiles for s in stats]),
                        'deletedfiles': _sum([s.deletedfiles for s in stats]),
                        'changedfiles': _sum([s.changedfiles for s in stats]),
                        'newfilesize': _sum([s.newfilesize for s in stats]),
                        'deletedfilesize': _sum([s.deletedfilesize for s in stats]),
                        'changedsourcesize': _sum([s.changedsourcesize for s in stats]),
                        'totaldestinationsizechange': _sum([s.totaldestinationsizechange for s in stats]),
                        'sourcefilesize': repo.session_statistics[-1].sourcefilesize
                        if len(repo.session_statistics)
                        else None,
                        'errors': _sum([s.errors for s in stats]),
                    }
                )
            except Exception:
                logger.warning('fail to collect data for %s %s', userobj, repo, exc_info=1)

        # Generate email.
        self._queue_mail(
            userobj,
            template="email_report.html",
            data=data,
            disk_usage=userobj.disk_usage,
            disk_quota=userobj.disk_quota,
            time_range=time_range,
            start_time=start_time,
            end_time=end_time,
        )
        return True


cherrypy.notification = NotificationPlugin(cherrypy.engine)
cherrypy.notification.subscribe()

cherrypy.config.namespaces['notification'] = lambda key, value: setattr(cherrypy.notification, key, value)
