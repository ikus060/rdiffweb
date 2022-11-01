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
Created on June 30, 2022

Module to test `user` model.

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""
import datetime
from io import open
from unittest.mock import MagicMock

import cherrypy
import pkg_resources

import rdiffweb.test
from rdiffweb.core.model import Token, UserObject


class TokenTest(rdiffweb.test.WebCase):
    def _read_ssh_key(self):
        """Readthe pub key from test packages"""
        filename = pkg_resources.resource_filename('rdiffweb.core.tests', 'test_publickey_ssh_rsa.pub')
        with open(filename, 'r', encoding='utf8') as f:
            return f.readline()

    def _read_authorized_keys(self):
        """Read the content of test_authorized_keys"""
        filename = pkg_resources.resource_filename('rdiffweb.core.tests', 'test_authorized_keys')
        with open(filename, 'r', encoding='utf8') as f:
            return f.read()

    def setUp(self):
        super().setUp()
        self.listener = MagicMock()
        cherrypy.engine.subscribe('access_token_added', self.listener.access_token_added, priority=50)
        cherrypy.engine.subscribe('queue_mail', self.listener.queue_mail, priority=50)

    def tearDown(self):
        cherrypy.engine.unsubscribe('access_token_added', self.listener.access_token_added)
        cherrypy.engine.unsubscribe('queue_mail', self.listener.queue_mail)
        return super().tearDown()

    def test_check_schedule(self):
        # Given the application is started
        # Then remove_older job should be schedule
        self.assertEqual(1, len([job for job in cherrypy.scheduler.list_jobs() if job.name == 'clean_up']))

    def test_clean_up_without_expired(self):
        # Given a user with 3 Token
        user = UserObject.get_user(self.USERNAME)
        user.add_access_token('test1')
        user.add_access_token('test2')
        user.add_access_token('test3')
        user.commit()
        self.assertEqual(3, Token.query.count())
        # When running notification_job
        cherrypy.token_cleanup.clean_up()
        # Then token are not removed
        self.assertEqual(3, Token.query.count())

    def test_clean_up_with_expired(self):
        # Given a user with 3 Token
        user = UserObject.get_user(self.USERNAME)
        user.add_access_token('test1')
        user.add_access_token('test2')
        user.add_access_token('test3')
        for t in Token.query.all():
            t.expiration_time = datetime.datetime.now()
        user.commit()
        self.assertEqual(3, Token.query.count())
        # When running notification_job
        cherrypy.token_cleanup.clean_up()
        # Then token are not removed
        self.assertEqual(0, Token.query.count())

    def test_add_access_token(self):
        # Given a user with an email
        userobj = UserObject.get_user(self.USERNAME)
        userobj.email = 'test@examples.com'
        userobj.commit()
        # When adding a new token
        token = userobj.add_access_token('test')
        userobj.commit()
        # Then a new token get created
        self.assertTrue(token)
        tokenobj = Token.query.filter(Token.userid == userobj.userid).first()
        self.assertTrue(tokenobj)
        self.assertEqual(None, tokenobj.expiration_time)
        self.assertEqual(None, tokenobj.access_time)
        # Then an email is sent to the user.
        self.listener.access_token_added.assert_called_once_with(userobj, 'test')
        self.listener.queue_mail.assert_called_once()

    def test_add_access_token_duplicate_name(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test')
        userobj.commit()
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When adding a new token with the same name
        with self.assertRaises(ValueError):
            userobj.add_access_token('test')
            userobj.commit()
        userobj.rollback()
        # Then token is not created
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # Then an email is not sent.
        self.listener.access_token_added.assert_called_once_with(userobj, 'test')

    def test_delete_access_token(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test')
        userobj.commit()
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When deleting an access token
        userobj.delete_access_token('test')
        userobj.commit()
        # Then Token get deleted
        self.assertEqual(0, Token.query.filter(Token.userid == userobj.userid).count())

    def test_delete_access_token_invalid(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test')
        userobj.commit()
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When deleting an invalid access token
        with self.assertRaises(ValueError):
            userobj.delete_access_token('invalid')
        # Then Token not deleted
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())

    def test_delete_user_remove_access_tokens(self):
        # Given a user with an existing token
        userobj = UserObject.add_user('testuser', 'password')
        userobj.commit()
        userobj.add_access_token('test')
        userobj.commit()
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When deleting the user
        userobj.delete()
        userobj.commit()
        # Then Token get deleted
        self.assertEqual(0, Token.query.filter(Token.userid == userobj.userid).count())

    def test_verify_access_token(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        token = userobj.add_access_token('test')
        userobj.commit()
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When validating the token
        # Then token is valid
        self.assertTrue(userobj.validate_access_token(token))

    def test_verify_access_token_with_expired(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        token = userobj.add_access_token(
            'test', expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1)
        )
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When validating the token
        # Then token is invalid
        self.assertFalse(userobj.validate_access_token(token))
        # Then token is not removed
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())

    def test_verify_access_token_with_invalid(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test', expiration_time=datetime.datetime.now())
        userobj.commit()
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When validating the token
        # Then token is invalid
        self.assertFalse(userobj.validate_access_token('invalid'))
