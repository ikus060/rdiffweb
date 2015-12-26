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

from rdiffweb.rdw_templating import do_format_filesize


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

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
