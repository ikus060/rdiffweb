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
Created on Mar 13, 2019

@author: Patrik Dufresne
"""


import logging
import unittest

from rdiffweb.test import WebCase


class ControllerTest(WebCase):

    @classmethod
    def setup_server(cls):
        WebCase.setup_server(default_config={'HeaderName':'MyTest'})

    def test_headername(self):
        """
        Check if the headername is used in the page.
        """
        self.getPage("/")
        self.assertInBody('MyTest')
        
    def test_theme(self):
        """
        Check if the theme is properly configure. 
        """
        self.getPage("/")
        self.assertInBody('/static/default.css')


class ControllerThemeTest(WebCase):

    @classmethod
    def setup_server(cls):
        WebCase.setup_server(default_config={'DefaultTheme':'orange'})

    def test_theme(self):
        """
        Check if the theme is properly configure. 
        """
        self.getPage("/")
        self.assertInBody('/static/orange.css')


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
