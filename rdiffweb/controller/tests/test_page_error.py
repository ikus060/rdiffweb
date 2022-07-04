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
Created on Mar 5, 2016

@author: Patrik Dufresne
"""


import rdiffweb.test


class ErrorPageTest(rdiffweb.test.WebCase):
    """
    Check how the error page behave.
    """

    login = True

    def test_error_page(self):
        # When browsing the invalid URL
        self.getPage('/invalid/')
        # Then a 404 error page is return using jinja2 template
        self.assertStatus("404 Not Found")
        self.assertInBody("Oops!")

    def test_error_page_exception(self):
        # When browsing a an invalid path
        self.getPage('/browse/invalid/')
        # Then a 404 error page is return using jinja2 template
        self.assertStatus("404 Not Found")
        self.assertInBody("Oops!")
