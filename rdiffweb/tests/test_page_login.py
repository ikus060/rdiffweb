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

from cherrypy import HTTPRedirect
import cherrypy
import unittest

from rdiffweb.test import MockRdiffwebApp


class LoginPageTest(unittest.TestCase):

    def setUp(self):
        self.app = MockRdiffwebApp(enabled_plugins=['SQLite'])
        self.app.reset()

    def test_index(self):
        """Make sure the login page can be rendered without error."""
        self.app.root.login.index()

    def test_index_with_user(self):
        """Make sure the login page can be rendered without error."""
        with self.assertRaises(HTTPRedirect):
            cherrypy.session = {}
            cherrypy.request.method = 'POST'
            self.app.root.login.index(login="admin", password="admin123")
            cherrypy.request.method = 'GET'

    def test_index_with_redirect(self):
        """Make sure to property encode/decode redirect url."""
        data = self.app.root.login.index(redirect='/browse/testcases/dir\u2713/')
        self.assertIn('/browse/testcases/dir%E2%9C%93/', data)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
