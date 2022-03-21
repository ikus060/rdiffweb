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
Created on Dec 26, 2015

@author: Patrik Dufresne
"""


import unittest

from rdiffweb.core.rdw_helpers import quote_url, unquote_url


class Test(unittest.TestCase):
    def test_quote_url(self):
        self.assertEqual('this%20is%20some%20path', quote_url('this is some path'))
        self.assertEqual('this%20is%20some%20path', quote_url(b'this is some path'))
        self.assertEqual(
            'R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial',
            quote_url(b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial'),
        )

    def test_unquote_url(self):
        self.assertEqual(b'this is some path', unquote_url('this%20is%20some%20path'))
        self.assertEqual(b'this is some path', unquote_url(b'this%20is%20some%20path'))
