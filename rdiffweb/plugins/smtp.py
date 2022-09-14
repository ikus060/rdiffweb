# -*- coding: utf-8 -*-
# SMTP Plugins for cherrypy
# Copyright (C) 2022 IKUS Software
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

import email.utils
import re
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from xml.etree.ElementTree import fromstring, tostring

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from . import scheduler  # noqa: This plugin required scheduler


def _html2plaintext(html, body_id=None, encoding='utf-8'):
    """From an HTML text, convert the HTML to plain text.
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
    except Exception:
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
    html = re.sub(r'<br\s*/?>', '\n', html)
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


def _formataddr(value):
    """
    Format the given value into a valid email address. Support raw string, tuple or a list of string.
    """
    if not value:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (tuple, list)) and len(value) == 2 and isinstance(value[0], str) and isinstance(value[1], str):
        return email.utils.formataddr(value)
    if not isinstance(value, (tuple, list)):
        raise TypeError('expect a string, a tuple or a list of email address')
    return ', '.join(map(_formataddr, value))


class SmtpPlugin(SimplePlugin):

    server = None
    username = None
    password = None
    encryption = None
    email_from = None

    def start(self):
        self.bus.log('Start SMTP plugin')
        self.bus.subscribe("send_mail", self.send_mail)
        self.bus.subscribe("queue_mail", self.queue_mail)

    def stop(self):
        self.bus.log('Stop SMTP plugin')
        self.bus.unsubscribe("send_mail", self.send_mail)
        self.bus.unsubscribe("queue_mail", self.queue_mail)

    def queue_mail(self, *args, **kwargs):
        """
        Queue mail to be sent.
        """
        # Skip sending email if smtp server is not configured.
        if not self.server:
            self.bus.log('cannot send email because SMTP Server is not configured')
            return
        if not self.email_from:
            self.bus.log('cannot send email because SMTP From is not configured')
            return
        self.bus.publish('schedule_task', self.send_mail, *args, **kwargs)

    def send_mail(self, subject: str, message: str, to=None, cc=None, bcc=None, reply_to=None):
        """
        Reusable method to be called to send email to the user user.
        `user` user object where to send the email.
        """
        assert subject
        assert message
        assert to or bcc
        to = _formataddr(to)
        cc = _formataddr(cc)
        bcc = _formataddr(bcc)
        reply_to = _formataddr(reply_to)

        # Skip sending email if smtp server is not configured.
        if not self.server:
            self.bus.log('cannot send email because SMTP Server is not configured')
            return
        if not self.email_from:
            self.bus.log('cannot send email because SMTP From is not configured')
            return

        # Compile both template.
        text = _html2plaintext(message)

        # Record the MIME types of both parts - text/plain and text/html.
        msg = MIMEMultipart('alternative')
        msg['Subject'] = str(subject)
        msg['From'] = self.email_from
        if to:
            msg['To'] = to
        if cc:
            msg['Cc'] = cc
        if bcc:
            msg['Bcc'] = bcc
        if reply_to:
            msg['Reply-To'] = reply_to
        msg['Message-ID'] = email.utils.make_msgid()
        msg.attach(MIMEText(text, 'plain', 'utf8'))
        msg.attach(MIMEText(message, 'html', 'utf8'))

        host, unused, port = self.server.partition(':')
        if self.encryption == 'ssl':
            conn = smtplib.SMTP_SSL(host, port or 465)
        else:
            conn = smtplib.SMTP(host, port or 25)
        try:
            if self.encryption == 'starttls':
                conn.starttls()
            # Authenticate if required.
            if self.username:
                conn.login(self.username, self.password)
            conn.send_message(msg)
        finally:
            conn.quit()


# Register SMTP plugin
cherrypy.smtp = SmtpPlugin(cherrypy.engine)
cherrypy.smtp.subscribe()

cherrypy.config.namespaces['smtp'] = lambda key, value: setattr(cherrypy.smtp, key, value)
