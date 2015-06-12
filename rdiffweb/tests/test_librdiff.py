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

import pkg_resources
import unittest

from rdiffweb.librdiff import RdiffPath, FileStatisticsEntry, RdiffRepo
"""
Created on Oct 3, 2015

Module used to test the librdiff.

@author: Patrik Dufresne
"""


class MockRdiffRepo(RdiffRepo):

    def __init__(self):
        self.encoding = 'utf8'
        self.data_path = pkg_resources.resource_filename('rdiffweb', 'tests')  # @UndefinedVariable


class MockRdiffPath(RdiffPath):

    def __init__(self):
        self.repo = MockRdiffRepo()


class FileStatisticsEntryTest(unittest.TestCase):
    """
    Test the file statistics entry.
    """

    def setUp(self):
        self.root_path = MockRdiffPath()

    def test_get_mirror_size(self):
        entry = FileStatisticsEntry(self.root_path, b'file_statistics.2014-11-05T16:05:07-05:00.data')
        size = entry.get_mirror_size(b'<F!chïer> (@vec) {càraçt#èrë} $épêcial')
        self.assertEqual(143, size)

    def test_get_source_size(self):
        entry = FileStatisticsEntry(self.root_path, b'file_statistics.2014-11-05T16:05:07-05:00.data')
        size = entry.get_source_size(b'<F!chïer> (@vec) {càraçt#èrë} $épêcial')
        self.assertEqual(286, size)

    def test_get_mirror_size_gzip(self):
        entry = FileStatisticsEntry(self.root_path, b'file_statistics.2014-11-05T16:05:07-05:00.data.gz')
        size = entry.get_mirror_size(b'<F!chïer> (@vec) {càraçt#èrë} $épêcial')
        self.assertEqual(143, size)

    def test_get_source_size_gzip(self):
        entry = FileStatisticsEntry(self.root_path, b'file_statistics.2014-11-05T16:05:07-05:00.data.gz')
        size = entry.get_source_size(b'<F!chïer> (@vec) {càraçt#èrë} $épêcial')
        self.assertEqual(286, size)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
