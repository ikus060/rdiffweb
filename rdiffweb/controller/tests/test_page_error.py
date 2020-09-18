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
Created on Mar 5, 2016

@author: Patrik Dufresne
"""


import logging
import unittest

from rdiffweb.test import WebCase


class ErrorPageTest(WebCase):
    """
    Check how the error page behave.
    """

    login = True

    reset_app = True

    reset_testcases = True

    def test_error_page(self):
        self.getPage('/invalid/')
        self.assertStatus("404 Not Found")
        self.assertInBody("Oops!")

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
