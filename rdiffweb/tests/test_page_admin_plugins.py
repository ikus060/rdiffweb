#!/usr/bin/env python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 Patrik Dufresne Service Logiciel
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
Created on Dec 31, 2015

@author: Patrik Dufresne
"""

from __future__ import print_function
from __future__ import unicode_literals

import logging
import unittest

from rdiffweb.test import WebCase


class PluginsTestAsAdmin(WebCase):
    """
    Plugin to verify admin plugin page as Admin.
    """

    login = True

    reset_app = True

    def test_plugins_List(self):
        self.getPage("/admin/plugins/")
        self.assertInBody('Ldap')
        self.assertInBody('SQLite')


class PluginsTestAsUser(WebCase):
    """
    Plugin to verify admin plugin page as user.
    """

    reset_app = True

    def setUp(self):
        WebCase.setUp(self)
        # Add test user
        self.app.userdb.add_user('test', 'test123')
        self._login('test', 'test123')

    def test_plugins_List(self):
        """
        Check if listing plugins as user is forbidden.
        """
        self.getPage("/admin/plugins/")
        self.assertStatus(403)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
