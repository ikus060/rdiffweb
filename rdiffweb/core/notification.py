# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""
Plugin used to send email to users when their repository is getting too old.
User can control the notification period.
"""

import logging
import platform
import re
from collections import Counter
from datetime import datetime, timedelta, timezone

import cherrypy
import distro
import requests
from cherrypy.process.plugins import SimplePlugin
from cherrypy_foundation.tools.i18n import preferred_lang
from cherrypy_foundation.tools.i18n import ugettext as _
from packaging.version import InvalidVersion, Version
from sqlalchemy import func, or_

from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import Message, UserObject

CONTEXT = 'NOTIFICATION'


def _log_user_login(user_id, date, ip_address, user_agent):
    """Used to log user loging asynchronously."""
    # Make sure to start from a clean session.
    cherrypy.db.clear_sessions()
    # Log event
    with cherrypy.db.session.begin():
        user = UserObject.get_user(user_id)
        user.add_message(
            Message(
                body=_("User login to web application"),
                type=Message.TYPE_EVENT,
                date=date,
                ip_address=ip_address,
                user_agent=user_agent,
                author=user,
            )
        )


class NotificationPlugin(SimplePlugin):
    """
    Send email notification when a repository get too old (without a backup).
    """

    env = None  # Jinja2 env

    execution_time = '23:00'

    send_changed = False

    bcc = None

    header_name = 'rdiffweb'

    current_version = None

    latest_version_url = None

    def start(self):
        self.bus.log('Start Notification plugin')
        self.bus.publish('scheduler:add_job_daily', self.execution_time, self.check_latest_job)
        self.bus.publish('scheduler:add_job_daily', self.execution_time, self.notification_job)
        self.bus.publish('scheduler:add_job_daily', self.execution_time, self.report_job)
        self.bus.subscribe('access_token_added', self.access_token_added)
        self.bus.subscribe('authorizedkey_added', self.authorizedkey_added)
        self.bus.subscribe('user_updated', self.user_updated)
        self.bus.subscribe('user_password_changed', self.user_password_changed)
        self.bus.subscribe('repo_added', self.repo_added)
        self.bus.subscribe('repo_deleted', self.repo_deleted)
        self.bus.subscribe('user_deleted', self.user_deleted)
        self.bus.subscribe('user_added', self.user_added)
        self.bus.subscribe('user_login', self.user_login)

    def stop(self):
        self.bus.log('Stop Notification plugin')
        self.bus.publish('scheduler:remove_job', self.check_latest_job)
        self.bus.publish('scheduler:remove_job', self.notification_job)
        self.bus.publish('scheduler:remove_job', self.report_job)
        self.bus.unsubscribe('access_token_added', self.access_token_added)
        self.bus.unsubscribe('authorizedkey_added', self.authorizedkey_added)
        self.bus.unsubscribe('user_updated', self.user_updated)
        self.bus.unsubscribe('user_password_changed', self.user_password_changed)
        self.bus.unsubscribe('repo_added', self.repo_added)
        self.bus.unsubscribe('repo_deleted', self.repo_deleted)
        self.bus.unsubscribe('user_deleted', self.user_deleted)
        self.bus.unsubscribe('user_added', self.user_added)
        self.bus.unsubscribe('user_login', self.user_login)

    def graceful(self):
        """Reload of subscribers."""
        self.stop()
        self.start()

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
            cherrypy.log(
                f'invalid current_version: {self.current_version}',
                context=CONTEXT,
                traceback=True,
                severity=logging.WARNING,
            )
            return None

        # Get latest version
        try:
            headers = {
                'User-Agent': (
                    f'{self.header_name}-server/{current_version}'
                    f' python/{platform.python_version()}'
                    f' {platform.system()}/{platform.release()}'
                    f' ({distro.name(True)} {platform.machine()})'
                )
            }
            response = requests.get(self.latest_version_url, headers=headers, timeout=0.5)
            response.raise_for_status()
            latest_version = Version(response.text)
        except requests.exceptions.RequestException:
            cherrypy.log(
                'fail to get latest version',
                context=CONTEXT,
                traceback=True,
                severity=logging.WARNING,
            )
            return None

        # Compare them
        return current_version >= latest_version

    def _queue_mail(self, userobj, template, to=None, **kwargs):
        """
        Generic function to queue email.
        """
        to = userobj.email if to is None else to
        if not to and not self.bcc:
            cherrypy.log(
                f"can't sent mail to user [{userobj.username}] without an email",
                context=CONTEXT,
                severity=logging.INFO,
            )
            return

        # Also send email to catch-all email.
        queue_mail_kwargs = {}
        if self.bcc:
            queue_mail_kwargs['bcc'] = self.bcc

        # Add branding variable to template creation.
        param = {
            # Hardcode bootstrap colors.
            'bs_colors': {
                'success': {
                    'color': "rgb(25, 135, 84)",
                    'bg_subtle': "rgb(209, 231, 221)",
                    'text_emphasis': "rgb(10, 54, 34)",
                },
                'warning': {
                    'color': "rgb(255, 193, 7)",
                    'bg_subtle': "rgb(255, 243, 205)",
                    'text_emphasis': "rgb(102, 77, 3)",
                },
                'info': {
                    'color': "rgb(13, 202, 240)",
                    'bg_subtle': "rgb(207, 244, 252)",
                    'text_emphasis': "rgb(5, 81, 96)",
                },
                'danger': {
                    'color': "rgb(220, 53, 69)",
                    'bg_subtle': "rgb(248, 214, 218)",
                    'text_emphasis': "rgb(88, 21, 28)",
                },
            }
        }
        # Compile the email body
        with preferred_lang(userobj.lang):
            tmpl = self.env.get_template(template)
            message_body = tmpl.render(user=userobj, **dict(param, **kwargs))
            # Extract subject from template
            match = re.search(r'<title>(.*)</title>', message_body, re.DOTALL)
            subject = match and match.group(1).replace('\n', '').strip()
        subject = subject or _(CONTEXT)
        # Queue the email.
        self.bus.publish('queue_mail', to=to, subject=subject, message=message_body, **queue_mail_kwargs)

    def access_token_added(self, userobj, name):
        cherrypy.log(
            f"A new access token {name} for the user {userobj.username} has been added",
            context=CONTEXT,
            severity=logging.INFO,
        )
        if self.send_changed:
            self._queue_mail(
                userobj,
                template="email_access_token_added.html",
                name=name,
            )

    def authorizedkey_added(self, userobj, fingerprint, comment, **kwargs):
        cherrypy.log(
            f"A new SSH key {fingerprint} has been added for the user {userobj.username}",
            context=CONTEXT,
            severity=logging.INFO,
        )
        if self.send_changed:
            self._queue_mail(
                userobj,
                template="email_authorizedkey_added.html",
                comment=comment,
                fingerprint=fingerprint,
            )

    def user_updated(self, userobj, attrs={}):
        username = userobj.username
        if 'email' in attrs:
            cherrypy.log(
                f"Email address of the user {username} has been changed",
                context=CONTEXT,
                severity=logging.INFO,
            )
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
            cherrypy.log(
                f"Two-factor authentication has been {state} for the user {username}",
                context=CONTEXT,
                severity=logging.INFO,
            )
            if self.send_changed:
                self._queue_mail(
                    userobj,
                    template="email_mfa.html",
                )

    def user_password_changed(self, userobj):
        cherrypy.log(
            f"User's password {userobj.username} changed",
            context=CONTEXT,
            severity=logging.INFO,
        )
        if self.send_changed:
            self._queue_mail(
                userobj,
                template="email_password_changed.html",
            )

    def repo_added(self, userobj, repo_path):
        cherrypy.log(
            f"New repository named {repo_path} has been added for the user {userobj.username}",
            context=CONTEXT,
            severity=logging.INFO,
        )
        if self.send_changed:
            self._queue_mail(
                userobj,
                template="email_repo_added.html",
                repo_path=repo_path,
            )

    def repo_deleted(self, userobj, repo_path):
        cherrypy.log(
            f"Repository {repo_path} of the user {userobj.username} has been deleted",
            context=CONTEXT,
            severity=logging.INFO,
        )
        if self.send_changed:
            self._queue_mail(
                userobj,
                template="email_repo_deleted.html",
                repo_path=repo_path,
            )

    def user_added(self, userobj):
        cherrypy.log(
            f"New user {userobj.username} has been added",
            context=CONTEXT,
            severity=logging.INFO,
        )

    def user_deleted(self, username):
        cherrypy.log(
            f"User {username} has been deleted",
            context=CONTEXT,
            severity=logging.INFO,
        )

    def user_login(self, userobj):
        cherrypy.log(
            f"User {userobj.username} login to web application",
            context=CONTEXT,
            severity=logging.INFO,
        )
        # Log user_login in a different thread.
        if hasattr(userobj, 'add_message'):
            request = cherrypy.serving.request
            now = datetime.now(timezone.utc)
            self.bus.publish(
                'scheduler:add_job_now',
                _log_user_login,
                user_id=userobj.id,
                date=now,
                ip_address=request.remote.ip,
                user_agent=request.headers.get('User-Agent', ''),
            )

    def notification_job(self):
        """
        Loop trough all the user repository and send notifications.
        """
        cherrypy.log('Running notification job', context=CONTEXT, severity=logging.INFO)
        # For Each user with an email.
        for userobj in UserObject.query.filter(UserObject.email != ''):
            try:
                # Identify failed, overdue or inactive repo.
                repo_objs = [
                    r
                    for r in userobj.repo_objs
                    if r.status[0] in ['failed', 'overdue', 'inactive'] or r.is_overdue() or r.is_inactive()
                ]
                # Send email if required
                if repo_objs:
                    self._queue_mail(
                        userobj,
                        template="email_notification.html",
                        repo_objs=repo_objs,
                    )
                # Send email if required
                if userobj.disk_usage_threshold:
                    # Check user's disk usage
                    disk_usage = userobj.disk_usage
                    disk_quota = userobj.disk_quota
                    used_pct = disk_usage / disk_quota * 100 if disk_quota else 0
                    cherrypy.log(
                        f"user {userobj} disk usage {used_pct}% (threshold: {userobj.disk_usage_threshold}%)",
                        context=CONTEXT,
                        severity=logging.INFO,
                    )
                    if used_pct >= float(userobj.disk_usage_threshold):
                        cherrypy.log("FOO - sending email")
                        self._queue_mail(
                            userobj,
                            template="email_storage_usage.html",
                            disk_usage=disk_usage,
                            disk_quota=disk_quota,
                        )
            except Exception:
                cherrypy.log(
                    f'fail to send notification to user {userobj}',
                    context=CONTEXT,
                    traceback=True,
                    severity=logging.ERROR,
                )

    def check_latest_job(self):
        """
        Check if running latest version.
        """
        # Check if current version and send email to administrator if required
        if self._is_latest() is False:
            for userobj in UserObject.query.filter(
                UserObject.email != '', UserObject.role == UserObject.ADMIN_ROLE, UserObject.check_latest.is_(True)
            ):
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
                cherrypy.log(
                    f'fail to send report to user {userobj}',
                    context=CONTEXT,
                    traceback=True,
                    severity=logging.ERROR,
                )

    def send_report(self, userobj, force=False, _now=None):
        """
        Generate the repport data to be sent.
        """
        # Compute the start & end time for the repport using server timezone
        assert userobj.report_time_range, 'invalid time_range'
        time_range = userobj.report_time_range
        now = RdiffTime(_now) if _now else RdiffTime()
        now = now.astimezone().replace(hour=0, minute=0, second=0)
        if time_range == 30:
            # Monthly
            end_time = activity_end = now - timedelta(days=now.day - 1)
            start_time = activity_start = (end_time - timedelta(days=27)).replace(day=1)
        elif time_range == 7:
            # Weekly
            end_time = activity_end = now - timedelta(days=now.weekday())
            start_time = activity_start = end_time - timedelta(days=time_range)
        else:
            # Other
            end_time = activity_end = now
            start_time = end_time - timedelta(days=time_range)
            activity_start = RdiffTime() - timedelta(days=30)

        # Check if we need to sent a new report
        if not force and userobj.report_last_sent is not None and RdiffTime(userobj.report_last_sent) > start_time:
            return False

        repo_objs = list(userobj.repo_objs)
        status_counts = Counter(r.status[0] for r in repo_objs)

        data = {
            "start_time": start_time,
            "end_time": end_time,
            "time_range": time_range,
            # User repo
            "repo_objs": repo_objs,
            "total_repo": len(repo_objs),
            "total_ok": status_counts["ok"],
            "total_broken": status_counts["broken"],
            "total_overdue": status_counts["overdue"],
            "total_interrupted": status_counts["interrupted"],
            "total_in_progress": status_counts["in_progress"],
            # Errors
            "error_count": sum(r.session_statistics[-1].errors for r in repo_objs if r.last_backup_date),
            # Storage
            "disk_usage": userobj.disk_usage,
            "disk_quota": userobj.disk_quota,
            # Heatmap
            "activity_start": activity_start,
            "activity_end": activity_end,
            "activity_dates": [
                d.date for repo in repo_objs for d in repo.session_statistics[activity_start:activity_end]
            ],
        }

        # Generate email.
        self._queue_mail(userobj, template="email_report.html", **data)
        return True


cherrypy.notification = NotificationPlugin(cherrypy.engine)
cherrypy.notification.subscribe()

cherrypy.config.namespaces['notification'] = lambda key, value: setattr(cherrypy.notification, key, value)
