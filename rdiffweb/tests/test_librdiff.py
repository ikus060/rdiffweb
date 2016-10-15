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
"""
Created on Oct 3, 2015

Module used to test the librdiff.

@author: Patrik Dufresne
"""

from __future__ import unicode_literals

from builtins import bytes
import encodings
import os
import pkg_resources
import unittest

from rdiffweb.librdiff import RdiffPath, FileStatisticsEntry, RdiffRepo, \
    DirEntry, IncrementEntry, SessionStatisticsEntry, HistoryEntry
from rdiffweb.rdw_helpers import rdwTime


class MockRdiffRepo(RdiffRepo):

    def __init__(self):
        self.encoding = encodings.search_function('utf-8')
        assert self.encoding
        self.repo_root = bytes(pkg_resources.resource_filename('rdiffweb', 'tests'), encoding='utf-8')  # @UndefinedVariable
        self.data_path = os.path.join(self.repo_root, b'rdiff-backup-data')
        self.root_path = MockRdiffPath(self)


class MockRdiffPath(RdiffPath):

    def __init__(self, repo):
        self.repo = repo
        self.path = b''


class IncrementEntryTest(unittest.TestCase):

    def setUp(self):
        self.repo = MockRdiffRepo()
        backup_dates = [
            1414871387, 1414871426, 1414871448, 1414871475, 1414871489, 1414873822,
            1414873850, 1414879639, 1414887165, 1414887491, 1414889478, 1414937803,
            1414939853, 1414967021, 1415047607, 1415059497, 1415221262, 1415221470,
            1415221495, 1415221507]
        self.repo._backup_dates = [rdwTime(x) for x in backup_dates]
        self.root_path = self.repo.root_path

    def test_extract_date(self):

        self.assertEqual(rdwTime(1414967021), IncrementEntry.extract_date(b'my_filename.txt.2014-11-02T17:23:41-05:00.diff.gz'))

    def test_init(self):

        increment = IncrementEntry(self.root_path, b'my_filename.txt.2014-11-02T17:23:41-05:00.diff.gz')
        self.assertEqual(rdwTime(1414967021), increment.date)
        self.assertEqual(b'my_filename.txt', increment.filename)


class DirEntryTest(unittest.TestCase):

    def setUp(self):
        self.repo = MockRdiffRepo()
        backup_dates = [
            1414871387, 1414871426, 1414871448, 1414871475, 1414871489, 1414873822,
            1414873850, 1414879639, 1414887165, 1414887491, 1414889478, 1414937803,
            1414939853, 1414967021, 1415047607, 1415059497, 1415221262, 1415221470,
            1415221495, 1415221507]
        self.repo._backup_dates = [rdwTime(x) for x in backup_dates]
        self.root_path = self.repo.root_path

    def test_change_dates(self):
        """Check if dates are properly sorted."""
        increments = [
            IncrementEntry(self.root_path, b'my_filename.txt.2014-11-02T17:23:41-05:00.diff.gz'),
            IncrementEntry(self.root_path, b'my_filename.txt.2014-11-02T09:16:43-05:00.missing'),
            IncrementEntry(self.root_path, b'my_filename.txt.2014-11-03T19:04:57-05:00.diff.gz')]
        entry = DirEntry(self.root_path, b'my_filename.txt', False, increments)

        self.assertEqual(
            [rdwTime(1414939853),
             rdwTime(1414967021),
             rdwTime(1415059497)],
            entry.change_dates)

    def test_change_dates_with_exists(self):
        """Check if dates are properly sorted."""
        increments = [
            IncrementEntry(self.root_path, b'my_filename.txt.2014-11-02T17:23:41-05:00.diff.gz'),
            IncrementEntry(self.root_path, b'my_filename.txt.2014-11-02T09:16:43-05:00.missing'),
            IncrementEntry(self.root_path, b'my_filename.txt.2014-11-03T19:04:57-05:00.diff.gz')]
        entry = DirEntry(self.root_path, b'my_filename.txt', True, increments)

        self.assertEqual(
            [rdwTime(1414939853),
             rdwTime(1414967021),
             rdwTime(1415059497),
             rdwTime(1415221507)],
            entry.change_dates)

    def test_restore_dates(self):
        increments = [
            IncrementEntry(self.root_path, b'my_dir.2014-11-05T16:04:30-05:00.dir'),
            IncrementEntry(self.root_path, b'my_dir.2014-11-05T16:04:55-05:00.dir')]
        entry = DirEntry(self.root_path, b'my_dir', False, increments)
        self.assertEqual(
            [rdwTime(1415221470),
             rdwTime(1415221495),
             ],
            entry.restore_dates)

    def test_restore_dates_with_exists(self):
        increments = [
            IncrementEntry(self.root_path, b'my_dir.2014-11-05T16:04:30-05:00.dir'),
            IncrementEntry(self.root_path, b'my_dir.2014-11-05T16:04:55-05:00.dir')]
        entry = DirEntry(self.root_path, b'my_dir', True, increments)
        self.assertEqual(
            [rdwTime(1415221470),
             rdwTime(1415221495),
             rdwTime(1415221507),
             ],
            entry.restore_dates)

    def test_display_name(self):
        """Check if display name is unquoted and unicode."""
        entry = DirEntry(self.root_path, b'my_dir', True, [])
        self.assertEqual('my_dir', entry.display_name)

        entry = DirEntry(self.root_path, b'my;090dir', True, [])
        self.assertEqual('myZdir', entry.display_name)

    def test_file_size(self):
        increments = [
            IncrementEntry(self.root_path, bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial.2014-11-05T16:05:07-05:00.dir', encoding='utf-8'))]
        entry = DirEntry(self.root_path, bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'), False, increments)
        self.assertEqual(286, entry.file_size)

    def test_file_size_without_stats(self):
        increments = [
            IncrementEntry(self.root_path, b'my_file.2014-11-05T16:04:30-05:00.dir')]
        entry = DirEntry(self.root_path, b'my_file', False, increments)
        self.assertEqual(0, entry.file_size)


class FileStatisticsEntryTest(unittest.TestCase):
    """
    Test the file statistics entry.
    """

    def setUp(self):
        self.repo = MockRdiffRepo()
        self.root_path = self.repo.root_path

    def test_get_mirror_size(self):
        entry = FileStatisticsEntry(self.root_path, b'file_statistics.2014-11-05T16:05:07-05:00.data')
        size = entry.get_mirror_size(bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'))
        self.assertEqual(143, size)

    def test_get_source_size(self):
        entry = FileStatisticsEntry(self.root_path, b'file_statistics.2014-11-05T16:05:07-05:00.data')
        size = entry.get_source_size(bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'))
        self.assertEqual(286, size)

    def test_get_mirror_size_gzip(self):
        entry = FileStatisticsEntry(self.root_path, b'file_statistics.2014-11-05T16:05:07-05:00.data.gz')
        size = entry.get_mirror_size(bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'))
        self.assertEqual(143, size)

    def test_get_source_size_gzip(self):
        entry = FileStatisticsEntry(self.root_path, b'file_statistics.2014-11-05T16:05:07-05:00.data.gz')
        size = entry.get_source_size(bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'))
        self.assertEqual(286, size)


class HistoryEntryTest(unittest.TestCase):

    def setUp(self):
        self.repo = MockRdiffRepo()
        self.root_path = self.repo.root_path

    def test_errors(self):
        increment = IncrementEntry(self.root_path, b'error_log.2015-11-19T07:27:46-05:00.data')
        entry = HistoryEntry(self.repo, increment.date)
        self.assertTrue(entry.has_errors)
        self.assertEqual('SpecialFileError home/coucou Socket error: AF_UNIX path too long', entry.errors)


class RdiffRepoTest(unittest.TestCase):

    def setUp(self):
        self.repo = MockRdiffRepo()
        self.root_path = self.repo.root_path

    def test_unquote(self):
        self.assertEqual(b'Char ;090 to quote', self.repo.unquote(b'Char ;059090 to quote'))


class SessionStatisticsEntryTest(unittest.TestCase):

    def setUp(self):
        self.repo = MockRdiffRepo()
        self.root_path = self.repo.root_path

    def test_getattr(self):
        """
        Check how a session statistic is read.
        """
        entry = SessionStatisticsEntry(self.root_path, b'session_statistics.2014-11-02T09:16:43-05:00.data')
        self.assertEqual(1414937803.00, entry.starttime)
        self.assertEqual(1414937764.82, entry.endtime)
        self.assertAlmostEqual(-38.18, entry.elapsedtime, delta=-0.01)
        self.assertEqual(14, entry.sourcefiles)
        self.assertEqual(3666973, entry.sourcefilesize)
        self.assertEqual(13, entry.mirrorfiles)
        self.assertEqual(30242, entry.mirrorfilesize)
        self.assertEqual(1, entry.newfiles)
        self.assertEqual(3636731, entry.newfilesize)
        self.assertEqual(0, entry.deletedfiles)
        self.assertEqual(0, entry.deletedfilesize)
        self.assertEqual(1, entry.changedfiles)
        self.assertEqual(0, entry.changedsourcesize)
        self.assertEqual(0, entry.changedmirrorsize)
        self.assertEqual(2, entry.incrementfiles)
        self.assertEqual(0, entry.incrementfilesize)
        self.assertEqual(3636731, entry.totaldestinationsizechange)
        self.assertEqual(0, entry.errors)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
