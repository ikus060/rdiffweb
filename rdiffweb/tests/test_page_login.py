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
Created on Dec 26, 2015

@author: Patrik Dufresne
"""

from __future__ import unicode_literals

import logging
import unittest

from rdiffweb.test import WebCase


class LoginPageTest(WebCase):

    def test_getpage(self):
        """
        Make sure the login page can be rendered without error.
        """
        self.getPage('/login/')
        self.assertStatus('200 OK')
        self.assertInBody('login')

    def test_getpage_with_redirect_get(self):
        """
        Check encoding of redirect url when send using GET method.
        """
        #  Query the page without login-in
        self.getPage('/browse/' + self.REPO + '/DIR%EF%BF%BD/')
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/?redirect=/browse/' + self.REPO + '/DIR%EF%BF%BD/')

    def test_getpage_with_redirect_post(self):
        """
        Check encoding of redirect url when send using POST method.
        """
        b = {'login': 'admin',
             'password': 'invalid',
             'redirect': '/browse/' + self.REPO + '/DIR%EF%BF%BD/'}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('200 OK')
        self.assertInBody('id="form-login"')
        self.assertInBody('value="/browse/' + self.REPO + '/DIR%EF%BF%BD/"')

    def test_getpage_with_querystring_redirect_get(self):
        """
        Check if unauthenticated users are redirect properly to login page.
        """
        self.getPage('/browse/' + self.REPO + '/?restore=T')
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/?redirect=/browse/' + self.REPO + '/%3Frestore%3DT')

        self.getPage('/restore/' + self.REPO + '/?date=1414871387&usetar=T')
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/?redirect=/restore/' + self.REPO + '/%3Fdate%3D1414871387%26usetar%3DT')

    def test_getpage_with_redirection(self):
        """
        Check if redirect url is properly rendered in HTML.
        """
        b = {'login': 'admin',
             'password': 'admin123',
             'redirect': '/restore/' + self.REPO + '/?date=1414871387&usetar=T'}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/restore/' + self.REPO + '/?date=1414871387&usetar=T')

    def test_getpage_with_empty_password(self):
        """
        Check if authentication is failing without a password.
        """
        b = {'login': 'admin',
             'password': ''}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('200 OK')
        self.assertInBody('Invalid username or password.')

    def test_index_with_redirect(self):
        """
        Make sure to property encode/decode redirect url.
        """
        data = self.app.root.login.index(redirect='/browse/' + self.REPO + '/dir\u2713/')
        self.assertIn('/browse/' + self.REPO + '/dir%E2%9C%93/', data)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
