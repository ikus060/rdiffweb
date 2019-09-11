#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

from __future__ import unicode_literals

from future.builtins import str
import unittest

from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.rdw_templating import do_format_filesize, url_for_browse, \
    url_for_history, url_for_restore, attrib


class TemplateManagerTest(unittest.TestCase):

    def test_attrib(self):
        # Single value
        self.assertEqual('id="row"', attrib(id='row'))
        # Single value with quote
        self.assertEqual('id="val&lt;ue&quot;with&quot;qu&gt;ot&amp;e"', attrib(id='val<ue"with"qu>ot&e'))
        # Multi attribute
        self.assertEqual('id="row" type="table"', attrib(type='table', id='row'))
        # Attribute with list
        self.assertEqual('type="table container"', attrib(type=['table', 'container']))
        # Attribute with class
        self.assertEqual('class="table container"', attrib(**{'class': ['table', 'container']}))
        # Boolean expressions
        self.assertEqual('id="active"', attrib(id=[False, 'active', False]))
        self.assertEqual('data="coucou" id="active"', attrib(type=False, id=[False, 'active', False], data='coucou'))
        active = True
        self.assertEqual('id="active"', attrib(id=[active and 'active']))
        active = False
        self.assertEqual('', attrib(id=[active and 'active']))

        # With True
        self.assertEqual('selected', attrib(selected=True))

        # Bytes
        self.assertEqual('selected="text"', attrib(selected=b'text'))

        # Newstr
        self.assertEqual('selected="text"', attrib(selected=str('text')))

    def test_do_format_filesize(self):
        # Test simple values
        self.assertEqual(do_format_filesize(1024, False), "1.0 kB")
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024, False), "1.1 GB")
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024 * 1024, False), "1.1 TB")
        self.assertEqual(do_format_filesize(0, False), "0 Bytes")
        self.assertEqual(do_format_filesize(980, False), "980 Bytes")
        self.assertEqual(do_format_filesize(1024 * 980, False), "1.0 MB")
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024 * 1.2, False), "1.3 GB")
        # Round to one decimal
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024 * 1.243, False), "1.3 GB")
        # Round to one decimal
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024 * 1024 * 120, False), "131.9 TB")

    def test_do_format_filesize_with_binary(self):
        # Test simple values
        self.assertEqual(do_format_filesize(1024, True), "1.0 KiB")
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024, True), "1.0 GiB")
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024 * 1024, True), "1.0 TiB")
        self.assertEqual(do_format_filesize(0, True), "0 Bytes")
        self.assertEqual(do_format_filesize(980, True), "980 Bytes")
        self.assertEqual(do_format_filesize(1024 * 980, True), "980.0 KiB")
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024 * 1.2, True), "1.2 GiB")
        # Round to one decimal
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024 * 1.243, True), "1.2 GiB")
        # Round to one decimal
        self.assertEqual(do_format_filesize(1024 * 1024 * 1024 * 1024 * 120, True), "120.0 TiB")

    def test_url_for_browse(self):
        """Check creation of url"""
        self.assertEqual('/browse/testcases/', url_for_browse(b'testcases'))
        self.assertEqual('/browse/testcases/Revisions/', url_for_browse(b'testcases', path=b'Revisions'))
        self.assertEqual('/browse/testcases/Revisions/?restore=T', url_for_browse(b'testcases', path=b'Revisions', restore=True))
        self.assertEqual('/browse/testcases/R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial/',
                         url_for_browse(b'testcases', path=b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial'))
        # Check if failing with unicode
        with self.assertRaises(AssertionError):
            url_for_browse('testcases')

    def test_url_for_history(self):
        """Check creation of url"""
        self.assertEqual('/history/testcases/', url_for_history(b'testcases'))
        # Check if failing with unicode
        with self.assertRaises(AssertionError):
            url_for_history('testcases')

    def test_url_for_restore(self):
        self.assertEqual('/restore/testcases?date=1414967021', url_for_restore(b'testcases', path=b'', date=RdiffTime(1414967021)))
        self.assertEqual('/restore/testcases/Revisions?date=1414967021', url_for_restore(b'testcases', path=b'Revisions', date=RdiffTime(1414967021)))
        self.assertEqual('/restore/testcases/R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial?date=1414967021',
                         url_for_restore(b'testcases', path=b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial', date=RdiffTime(1414967021)))
        # Check if failing with unicode
        with self.assertRaises(AssertionError):
            url_for_restore('testcases', path='', date=RdiffTime(1414967021))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
