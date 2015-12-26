#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

import unittest

from rdiffweb.rdw_templating import do_format_filesize, url_for_browse, \
    url_for_history, url_for_restore
from rdiffweb.rdw_helpers import rdwTime


class TemplateManagerTest(unittest.TestCase):

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
        self.assertEqual('/restore/testcases/?date=1414967021', url_for_restore(b'testcases', path=b'', date=rdwTime(1414967021)))
        self.assertEqual('/restore/testcases/Revisions/?date=1414967021', url_for_restore(b'testcases', path=b'Revisions', date=rdwTime(1414967021)))
        self.assertEqual('/restore/testcases/R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial/?date=1414967021',
                         url_for_restore(b'testcases', path=b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial', date=rdwTime(1414967021)))
        # Check if failing with unicode
        with self.assertRaises(AssertionError):
            url_for_restore('testcases', path='', date=rdwTime(1414967021))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
