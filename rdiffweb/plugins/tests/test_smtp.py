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

from unittest import mock

import cherrypy
from cherrypy.test import helper

from .. import smtp  # noqa


class SmtpPluginTest(helper.CPWebCase):
    @classmethod
    def setup_server(cls):
        cherrypy.config.update(
            {
                'smtp.server': '__default__',
                'smtp.username': 'username',
                'smtp.password': 'password',
                'smtp.email_from': 'Test <email_from@test.com>',
            }
        )

    def test_send_mail(self):
        # Given a valid smtp server
        with mock.patch(smtp.__name__ + '.smtplib') as smtplib:
            # When publishing a send_mail
            cherrypy.engine.publish('send_mail', to='target@test.com', subject='subjet', message='body')
            # Then smtplib is called to send the mail.
            smtplib.SMTP.assert_called_once_with('__default__', 25)
            smtplib.SMTP.return_value.send_message.assert_called_once_with(mock.ANY)
            smtplib.SMTP.return_value.quit.assert_called_once_with()

    def test_send_mail_with_to_tuple(self):
        # Given a valid smtp server
        with mock.patch(smtp.__name__ + '.smtplib') as smtplib:
            # When publishing a send_mail
            cherrypy.engine.publish(
                'send_mail',
                to=('A name', 'target@test.com'),
                subject='subjet',
                message='body',
                bcc=('A bcc name', 'bcc@test.com'),
                reply_to=('A Reply Name', 'replyto@test.com'),
            )
            # Then smtplib is called to send the mail.
            smtplib.SMTP.assert_called_once_with('__default__', 25)
            smtplib.SMTP.return_value.send_message.assert_called_once_with(mock.ANY)
            smtplib.SMTP.return_value.quit.assert_called_once_with()

    def test_queue_mail(self):
        # Given a paused scheduler plugin
        cherrypy.scheduler._scheduler.pause()
        # When queueing a email
        cherrypy.engine.publish('queue_mail', to='target@test.com', subject='subjet', message='body')
        # Then a new job get schedule
        self.assertEqual(1, len(cherrypy.scheduler.list_tasks()))

    def test_html2plaintext(self):
        """
        Check if this convertion is working fine.
        """

        html = """<html>
  <head></head>
  <body>
    <p>Hi!<br>
       How are you?<br>
       Here is the <a href="https://www.python.org">link</a> you wanted.
    </p>
  </body>
</html>
"""

        expected = """Hi!
How are you?
Here is the link you wanted."""
        self.assertEqual(expected, smtp._html2plaintext(html))

    def test_formataddr(self):
        self.assertEqual('test@test.com', smtp._formataddr('test@test.com'))
        self.assertEqual('TEST <test@test.com>', smtp._formataddr(('TEST', 'test@test.com')))
        self.assertEqual(
            'test2@test.com, TEST3 <test3@test.com>', smtp._formataddr(['test2@test.com', ('TEST3', 'test3@test.com')])
        )
