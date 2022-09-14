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


from parameterized import parameterized_class

import rdiffweb.test


@parameterized_class(
    [
        {"default_config": {'environment': 'production'}, "expect_stacktrace": False},
        {"default_config": {'environment': 'development'}, "expect_stacktrace": True},
        {"default_config": {'debug': False}, "expect_stacktrace": False},
        {"default_config": {'debug': True}, "expect_stacktrace": True},
    ]
)
class ErrorPageTest(rdiffweb.test.WebCase):

    login = True

    def test_error_page_html(self):
        # When browsing the invalid URL
        self.getPage('/invalid/')
        # Then a 404 error page is return using jinja2 template
        self.assertStatus("404 Not Found")
        self.assertInBody("Oops!")
        if self.expect_stacktrace:
            self.assertInBody('Traceback (most recent call last):')
        else:
            self.assertNotInBody('Traceback (most recent call last):')
        self.assertInBody("The path &#39;/invalid/&#39; was not found.")

    def test_error_page_plain_text(self):
        # When browsing a an invalid path
        self.getPage('/invalid/', headers=[("Accept", "text/plain")])
        # Then a 404 error page is return in plain text
        self.assertStatus("404 Not Found")
        self.assertInBody(b"The path '/invalid/' was not found.")
        self.assertNotInBody(b"<html>")
