#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 Patrik Dufresne Service Logiciel
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
from __future__ import unicode_literals

from builtins import str
import cherrypy
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate
import logging
import os
import re
import smtplib
import time
from xml.etree.ElementTree import fromstring, tostring

from rdiffweb import librdiff
from rdiffweb.core import RdiffError, RdiffWarning
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_helpers import rdwTime
from rdiffweb.rdw_plugin import IPreferencesPanelProvider, JobPlugin, \
    IUserChangeListener


_logger = logging.getLogger(__name__)


def html2plaintext(html, body_id=None, encoding='utf-8'):
    """ From an HTML text, convert the HTML to plain text.
    If @param body_id is provided then this is the tag where the
    body (not necessarily <body>) starts.
    """
    # (c) Fry-IT, www.fry-it.com, 2007
    # <peter@fry-it.com>
    # download here: http://www.peterbe.com/plog/html2plaintext
    assert isinstance(html, str)
    url_index = []
    try:
        tree = fromstring(html)

        if body_id is not None:
            source = tree.xpath('//*[@id=%s]' % (body_id,))
        else:
            source = tree.xpath('//body')
        if len(source):
            tree = source[0]

        i = 0
        for link in tree.findall('.//a'):
            url = link.get('href')
            if url:
                i += 1
                link.tag = 'span'
                link.text = '%s [%s]' % (link.text, i)
                url_index.append(url)

        html = tostring(tree, encoding=encoding)
    except:
        # Don't fail if the html is invalid.
        pass
    # \r char is converted into &#13;, must remove it
    html = html.replace('&#13;', '')

    html = html.replace('<strong>', '*').replace('</strong>', '*')
    html = html.replace('<b>', '*').replace('</b>', '*')
    html = html.replace('<h3>', '*').replace('</h3>', '*')
    html = html.replace('<h2>', '**').replace('</h2>', '**')
    html = html.replace('<h1>', '**').replace('</h1>', '**')
    html = html.replace('<em>', '/').replace('</em>', '/')
    html = html.replace('<tr>', '\n')
    html = html.replace('</p>', '\n')
    html = re.sub('<br\s*/?>', '\n', html)
    html = re.sub('<.*?>', ' ', html)
    html = html.replace(' ' * 2, ' ')
    html = html.replace('&gt;', '>')
    html = html.replace('&lt;', '<')
    html = html.replace('&amp;', '&')

    # strip all lines
    html = '\n'.join([x.strip() for x in html.splitlines()])
    html = html.replace('\n' * 2, '\n')

    for i, url in enumerate(url_index):
        if i == 0:
            html += '\n\n'
        html += '[%s] %s\n' % (i + 1, url)

    return html.strip('\n')


def _utf8(self, val):
    """Utility method to encode text to utf8 for email."""
    assert isinstance(val, str)
    return val.encode('utf-8')


class NotificationPlugin(IPreferencesPanelProvider, JobPlugin, IUserChangeListener):
    """
    Send email notification when a repository get too old (without a backup).
    """

    @property
    def _encryption(self):
        return self.app.cfg.get_config('EmailEncryption', 'none')

    @property
    def _email_host(self):
        value = self.app.cfg.get_config('EmailHost')
        value = value.partition(':')[0]
        return value

    @property
    def _email_port(self):
        value = self.app.cfg.get_config('EmailHost')
        value = value.partition(':')[2]
        try:
            return int(value)
        except:
            return 0

    @property
    def _email_from(self):
        return self.app.cfg.get_config('EmailSender', self.app.cfg.get_config('EmailFrom'))

    @property
    def _smtp_username(self):
        return self.app.cfg.get_config('EmailUsername', None)

    @property
    def _smtp_password(self):
        return self.app.cfg.get_config('EmailPassword', None)

    def activate(self):
        """Called by the plugin manager to setup the plugin."""
        super(NotificationPlugin, self).activate()

        # If notification are disabled, delete the handler.
        notify = self.app.cfg.get_config_bool('EmailSendChangedNotification', False)
        if not notify:
            del self.user_attr_changed

    @property
    def job_execution_time(self):
        """
        Implementation of JobPlugin interface.
        """
        return self.app.cfg.get_config('EmailNotificationTime', '23:00')

    def job_run(self):
        """
        Implementation of JobPLugin interface.
        Go trough all the repositories and users to send mail in batches.
        """
        self.send_notifications()

    def user_attr_changed(self, username, attrs={}):
        """
        Implementation of IUserChangeListener interface.
        """
        # Leave if the mail was not changed.
        if 'email' not in attrs:
            return

        # get User object (to get email)
        userobj = self.app.userdb.get_user(username)
        assert userobj
        # If the email attributes was changed, send a mail notification.
        self.send_mail(userobj, _("Email address changed"), "email_changed.html")

    def send_notifications(self):
        """
        Loop trough all the user repository and send notifications.
        """

        now = rdwTime()

        def _user_repos():
            """Return a generator trought user repos to be notified."""
            for user in self.app.userdb.list():
                # Check if user has email.
                if not user.email:
                    continue
                # Identify old repo for current user.
                old_repos = []
                for repo in user.repo_list:
                    # Check if repo has age configured (in days)
                    maxage = repo.maxage
                    if not maxage or maxage <= 0:
                        continue
                    # Check repo age.
                    r = librdiff.RdiffRepo(user.user_root, repo.name)
                    if r.last_backup_date < (now - datetime.timedelta(days=maxage)):
                        old_repos.append(r)
                # Return an item only if user had old repo
                if old_repos:
                    yield user, old_repos

        # For each candidate, send mail.
        for user, repos in _user_repos():
            parms = {'user': user, 'repos': repos}
            self.send_mail(user, _('Notification'), 'email_notification.html', **parms)

    def send_mail(self, to_user, subject, template_name, **kwargs):
        """
        Reusable method to be called to send email to the user user.
        `user` user object where to send the email.
        ``
        """
        # Build email from template.
        parms = {'user': to_user}
        parms.update(kwargs)

        # Compile both template.
        html = self.app.templates.compile_template(template_name, **parms)
        text = html2plaintext(html)

        # Record the MIME types of both parts - text/plain and text/html.
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        email_from = self.app.cfg.get_config("HeaderName", 'rdiffweb')
        if self._email_from:
            email_from += " <%s>" % self._email_from

        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = email_from
        msg['To'] = to_user.email
        # msg['Date'] = formatdate(localtime=True)
        msg.attach(part1)
        msg.attach(part2)

        # Open an SMTP connection.
        conn = None
        if self._encryption == 'ssl':
            conn = smtplib.SMTP_SSL(self._email_host, self._email_port)
        else:
            conn = smtplib.SMTP(self._email_host, self._email_port)
        try:
            if self._encryption == 'starttls':
                conn.starttls()

            # Authenticate if required.
            if self._smtp_username:
                conn.login(self._smtp_username, self._smtp_password)
            conn.sendmail(self._email_from, to_user.email, msg.as_string())
        finally:
            if conn is not None:
                conn.quit()

    def get_prefs_panels(self):
        """
        Return a single page.
        """
        yield ('notification', _('Notification'))

    def _handle_set_notification_info(self, **kwargs):

        # Loop trough user repo and update max age.
        for repo in self.app.currentuser.repo_list:
            # Get value received for the repo.
            value = kwargs.get(repo.name, None)
            if value is None:
                continue
            try:
                value = int(value)
            except:
                continue
            # Update the maxage
            repo.maxage = value

    def render_prefs_panel(self, panelid, **kwargs):  # @UnusedVariable
        # Process the parameters.
        params = dict()
        action = kwargs.get('action')
        if action:
            try:
                if action == "set_notification_info":
                    self._handle_set_notification_info(**kwargs)
                else:
                    _logger.info("unknown action: %s", action)
                    raise cherrypy.NotFound("Unknown action")
            except RdiffWarning as e:
                params['warning'] = str(e)
            except RdiffError as e:
                params['error'] = str(e)
            except Exception as e:
                _logger.warning("unknown error processing action", exc_info=True)
                params['error'] = _("Unknown error")

        params.update({
            'email': self.app.currentuser.email,
            'repos': [
                {'name': r.name, 'maxage': r.maxage}
                for r in self.app.currentuser.repo_list],
        })
        return "prefs_notification.html", params
