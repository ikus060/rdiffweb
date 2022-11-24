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
Created on Oct 3, 2015

Module used to test the librdiff.

@author: Patrik Dufresne
"""
import datetime
import os
import shutil
import tarfile
import tempfile
import time
import unittest
from inspect import isclass
from unittest.case import skipIf

import pkg_resources
from parameterized import parameterized

from rdiffweb.core.librdiff import (
    AccessDeniedError,
    DoesNotExistError,
    FileStatisticsEntry,
    IncrementEntry,
    RdiffDirEntry,
    RdiffRepo,
    RdiffTime,
    SessionStatisticsEntry,
    rdiff_backup_version,
    unquote,
)


class MockRdiffRepo(RdiffRepo):
    def __init__(self):
        p = bytes(pkg_resources.resource_filename('rdiffweb.core', 'tests'), encoding='utf-8')  # @UndefinedVariable
        RdiffRepo.__init__(self, p, encoding='utf-8')
        self.root_path = MockDirEntry(self)


class MockDirEntry(RdiffDirEntry):
    def __init__(self, repo):
        self._repo = repo
        self.path = b''


class IncrementEntryTest(unittest.TestCase):
    def test_init(self):
        increment = IncrementEntry(b'my_filename.txt.2014-11-02T17:23:41-05:00.diff.gz')
        self.assertEqual(b'my_filename.txt', increment.name)
        self.assertEqual(RdiffTime(1414967021), increment.date)
        self.assertEqual(b'.diff.gz', increment.suffix)

    def test_extract_date(self):
        self.assertEqual(
            RdiffTime(1414967021), IncrementEntry._extract_date(b'my_filename.txt.2014-11-02T17:23:41-05:00.diff.gz')
        )
        self.assertEqual(
            RdiffTime(1414967021), IncrementEntry._extract_date(b'my_filename.txt.2014-11-02T17-23-41-05-00.diff.gz')
        )
        # Check if date with quoted characther are proerply parsed.
        # On NTFS, colon (:) are not supported.
        self.assertEqual(
            RdiffTime(1483443123),
            IncrementEntry._extract_date(b'my_filename.txt.2017-01-03T06;05832;05803-05;05800.diff.gz'),
        )


class RdiffDirEntryTest(unittest.TestCase):
    def setUp(self):
        self.repo = MockRdiffRepo()

    def test_init(self):
        entry = RdiffDirEntry(self.repo, b'my_filename.txt', False, [])
        self.assertFalse(entry.isdir)
        self.assertFalse(entry.exists)
        self.assertEqual(os.path.join(b'my_filename.txt'), entry.path)
        self.assertEqual(os.path.join(self.repo.full_path, b'my_filename.txt'), entry.full_path)

    def test_change_dates(self):
        """Check if dates are properly sorted."""
        increments = [
            IncrementEntry(b'my_filename.txt.2014-11-02T17:23:41-05:00.diff.gz'),
            IncrementEntry(b'my_filename.txt.2014-11-02T09:16:43-05:00.missing'),
            IncrementEntry(b'my_filename.txt.2014-11-03T19:04:57-05:00.diff.gz'),
        ]
        entry = RdiffDirEntry(self.repo, b'my_filename.txt', False, increments)

        self.assertEqual(
            [RdiffTime('2014-11-02T17:23:41-05:00'), RdiffTime('2014-11-03T19:04:57-05:00')], entry.change_dates
        )

    def test_change_dates_with_exists(self):
        """Check if dates are properly sorted."""
        increments = [
            IncrementEntry(b'my_filename.txt.2014-11-02T17:23:41-05:00.diff.gz'),
            IncrementEntry(b'my_filename.txt.2014-11-02T09:16:43-05:00.missing'),
            IncrementEntry(b'my_filename.txt.2014-11-03T19:04:57-05:00.diff.gz'),
        ]
        entry = RdiffDirEntry(self.repo, b'my_filename.txt', True, increments)

        self.assertEqual(
            [RdiffTime('2014-11-02T17:23:41-05:00'), RdiffTime('2014-11-03T19:04:57-05:00')], entry.change_dates
        )

    def test_display_name(self):
        """Check if display name is unquoted and unicode."""
        entry = RdiffDirEntry(self.repo, b'my_dir', True, [])
        self.assertEqual('my_dir', entry.display_name)

        entry = RdiffDirEntry(self.repo, b'my;090dir', True, [])
        self.assertEqual('myZdir', entry.display_name)

    def test_file_size(self):
        # Given a dir increment
        increments = [
            IncrementEntry(
                bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial.2014-11-05T16:05:07-05:00.dir', encoding='utf-8'),
            )
        ]
        entry = RdiffDirEntry(
            self.repo, bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'), False, increments
        )
        # When getting the file_size
        # Then the size is 0
        self.assertEqual(-1, entry.file_size)

    def test_file_size_without_stats(self):
        increments = [IncrementEntry(b'my_file.2014-11-05T16:04:30-05:00.dir')]
        entry = RdiffDirEntry(self.repo, b'my_file', False, increments)
        self.assertEqual(-1, entry.file_size)


class FileErrorTest(unittest.TestCase):
    def test_init(self):
        e = DoesNotExistError('some/path')
        self.assertEqual('some/path', str(e))

        e = AccessDeniedError('some/path')
        self.assertEqual('some/path', str(e))


class FileStatisticsEntryTest(unittest.TestCase):
    """
    Test the file statistics entry.
    """

    def setUp(self):
        self.repo = MockRdiffRepo()

    def test_get_mirror_size(self):
        entry = FileStatisticsEntry(self.repo, b'file_statistics.2014-11-05T16:05:07-05:00.data')
        size = entry.get_mirror_size(bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'))
        self.assertEqual(143, size)

    def test_get_source_size(self):
        entry = FileStatisticsEntry(self.repo, b'file_statistics.2014-11-05T16:05:07-05:00.data')
        size = entry.get_source_size(bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'))
        self.assertEqual(286, size)

    def test_get_mirror_size_gzip(self):
        entry = FileStatisticsEntry(self.repo, b'file_statistics.2014-11-05T16:05:07-05:00.data.gz')
        size = entry.get_mirror_size(bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'))
        self.assertEqual(143, size)

    def test_get_source_size_gzip(self):
        entry = FileStatisticsEntry(self.repo, b'file_statistics.2014-11-05T16:05:07-05:00.data.gz')
        size = entry.get_source_size(bytes('<F!chïer> (@vec) {càraçt#èrë} $épêcial', encoding='utf-8'))
        self.assertEqual(286, size)


class LogEntryTest(unittest.TestCase):
    def setUp(self):
        self.repo = MockRdiffRepo()
        self.root_path = self.repo.root_path

    @parameterized.expand(
        [
            (
                'with_uncompress',
                '2015-11-19T07:27:46-05:00',
                'SpecialFileError home/coucou Socket error: AF_UNIX path too long',
            ),
            (
                'with_compress',
                '2015-11-20T07:27:46-05:00',
                'SpecialFileError home/coucou Socket error: AF_UNIX path too long',
            ),
        ]
    )
    def test_errors_tail(self, unused, date, expected_content):
        entry = self.repo.error_log[RdiffTime(date)]
        self.assertIsNotNone(entry)
        self.assertEqual(entry.tail(), expected_content)


class RdiffRepoTest(unittest.TestCase):
    def setUp(self):
        # Extract 'testcases.tar.gz'
        testcases = pkg_resources.resource_filename('rdiffweb.tests', 'testcases.tar.gz')  # @UndefinedVariable
        self.temp_dir = tempfile.mkdtemp(prefix='rdiffweb_tests_')
        tarfile.open(testcases).extractall(self.temp_dir)
        # Define location of testcases
        self.testcases_dir = os.path.normpath(os.path.join(self.temp_dir, 'testcases'))
        self.testcases_dir = self.testcases_dir.encode('utf8')
        self.repo = RdiffRepo(os.path.join(self.temp_dir, 'testcases'), encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self.temp_dir.encode('utf8'), True)

    def test_init(self):
        self.assertEqual('testcases', self.repo.display_name)

    def test_init_with_absolute(self):
        self.repo = RdiffRepo(os.path.join(self.temp_dir, '/testcases'), encoding='utf-8')
        self.assertEqual('testcases', self.repo.display_name)

    def test_init_with_invalid(self):
        self.repo = RdiffRepo(os.path.join(self.temp_dir, 'invalid'), encoding='utf-8')
        self.assertEqual('failed', self.repo.status[0])
        self.assertEqual(None, self.repo.last_backup_date)
        self.assertEqual('invalid', self.repo.display_name)

    @parameterized.expand(
        [
            (
                "with_root",
                b"/",
                'testcases',
                b'',
                True,
                True,
                True,
                -1,
                [
                    '2014-11-01T15:49:47-04:00',
                    '2014-11-01T15:50:26-04:00',
                    '2014-11-01T15:50:48-04:00',
                    '2014-11-01T15:51:15-04:00',
                    '2014-11-01T15:51:29-04:00',
                    '2014-11-01T16:30:22-04:00',
                    '2014-11-01T16:30:50-04:00',
                    '2014-11-01T18:07:19-04:00',
                    '2014-11-01T20:12:45-04:00',
                    '2014-11-01T20:18:11-04:00',
                    '2014-11-01T20:51:18-04:00',
                    '2014-11-02T09:16:43-05:00',
                    '2014-11-02T09:50:53-05:00',
                    '2014-11-02T17:23:41-05:00',
                    '2014-11-03T15:46:47-05:00',
                    '2014-11-03T19:04:57-05:00',
                    '2014-11-05T16:01:02-05:00',
                    '2014-11-05T16:04:30-05:00',
                    '2014-11-05T16:04:55-05:00',
                    '2014-11-05T16:05:07-05:00',
                    '2016-01-20T10:42:21-05:00',
                    '2016-02-02T16:30:40-05:00',
                ],
            ),
            (
                "with_dir",
                b"Subdirectory",
                'Subdirectory',
                b'Subdirectory',
                True,
                True,
                False,
                -1,
                [
                    '2014-11-05T16:04:55-05:00',
                    '2016-01-20T10:42:21-05:00',
                    '2016-02-02T16:30:40-05:00',
                ],
            ),
            (
                "with_dir_utf8_char",
                b"Subdirectory/Fold\xc3\xa8r with \xc3\xa9ncod\xc3\xafng",
                'Foldèr with éncodïng',
                b'Subdirectory/Fold\xc3\xa8r with \xc3\xa9ncod\xc3\xafng',
                True,
                True,
                False,
                -1,
                ['2014-11-05T16:04:55-05:00', '2016-02-02T16:30:40-05:00'],
            ),
            (
                "with_dir",
                b"Revisions",
                'Revisions',
                b'Revisions',
                True,
                True,
                False,
                -1,
                [
                    '2014-11-03T19:04:57-05:00',
                    '2014-11-05T16:04:30-05:00',
                    '2014-11-05T16:04:55-05:00',
                    '2014-11-05T16:05:07-05:00',
                    '2016-02-02T16:30:40-05:00',
                ],
            ),
            (
                "with_file",
                b'Revisions/Data',
                'Data',
                b'Revisions/Data',
                True,
                False,
                False,
                9,
                [
                    '2014-11-03T19:04:57-05:00',
                    '2014-11-05T16:04:30-05:00',
                    '2014-11-05T16:04:55-05:00',
                    '2014-11-05T16:05:07-05:00',
                    '2016-02-02T16:30:40-05:00',
                ],
            ),
            (
                "with_broken_symlink",
                b'BrokenSymlink',
                'BrokenSymlink',
                b'BrokenSymlink',
                True,
                False,
                False,
                7,
                ['2014-11-05T16:05:07-05:00', '2016-02-02T16:30:40-05:00'],
            ),
            (
                "with_char_to_quote",
                b'Char ;090 to quote',
                'Char Z to quote',
                b'Char ;090 to quote',
                False,
                True,
                False,
                -1,
                ['2014-11-01T18:07:19-04:00', '2014-11-01T20:18:11-04:00', '2014-11-03T19:04:57-05:00'],
            ),
            (
                "with_char_to_quote",
                b'Char ;059090 to quote',
                'Char ;090 to quote',
                b'Char ;059090 to quote',
                True,
                True,
                False,
                -1,
                ['2014-11-03T15:46:47-05:00', '2014-11-05T16:05:07-05:00', '2016-02-02T16:30:40-05:00'],
            ),
            (
                "with_char_to_quote",
                b'Char ;059059090 to quote',
                'Char ;059090 to quote',
                b'Char ;059059090 to quote',
                False,
                True,
                False,
                -1,
                ['2014-11-05T16:04:55-05:00', '2016-01-20T10:42:21-05:00'],
            ),
            (
                "with_loop_symlink",
                b'Subdirectory/LoopSymlink',
                'LoopSymlink',
                b'Subdirectory/LoopSymlink',
                True,
                True,
                False,
                -1,
                ['2014-11-05T16:05:07-05:00', '2016-02-02T16:30:40-05:00'],
            ),
            (
                "with_subdir_symlink",
                b'SymlinkToSubdirectory',
                'SymlinkToSubdirectory',
                b'SymlinkToSubdirectory',
                True,
                True,
                False,
                -1,
                ['2014-11-05T16:05:07-05:00', '2016-02-02T16:30:40-05:00'],
            ),
        ]
    )
    def test_fstat(self, unused, input, display_name, path, exists, isdir, isroot, file_size, change_dates):
        dir_entry = self.repo.fstat(input)
        self.assertEqual(display_name, dir_entry.display_name)
        self.assertEqual(path, dir_entry.path)
        self.assertEqual(os.path.join(self.testcases_dir, path).rstrip(b'/'), dir_entry.full_path)
        self.assertEqual(exists, dir_entry.exists)
        self.assertEqual(isdir, dir_entry.isdir)
        self.assertEqual(isroot, dir_entry.isroot)
        self.assertEqual(file_size, dir_entry.file_size)
        self.assertEqual([RdiffTime(t) for t in change_dates], list(dir_entry.change_dates))
        # For consistency, check if the same value are retreived using listdir
        if not isroot:
            parent_dir = os.path.dirname(input)
            children = self.repo.listdir(parent_dir)
            dir_entry = next(c for c in children if c.path == input)
            self.assertEqual(display_name, dir_entry.display_name)
            self.assertEqual(path, dir_entry.path)
            self.assertEqual(os.path.join(self.testcases_dir, path).rstrip(b'/'), dir_entry.full_path)
            self.assertEqual(exists, dir_entry.exists)
            self.assertEqual(isdir, dir_entry.isdir)
            self.assertEqual(isroot, dir_entry.isroot)
            self.assertEqual(file_size, dir_entry.file_size)
            self.assertEqual([RdiffTime(t) for t in change_dates], list(dir_entry.change_dates))

    def test_fstat_outside_repo(self):
        with self.assertRaises(AccessDeniedError):
            self.repo.fstat(b"../")

    @parameterized.expand(
        [
            (
                "with_root",
                b"",
                [
                    '<F!chïer> (@vec) {càraçt#èrë} $épêcial',
                    'BrokenSymlink',
                    'Char ;059090 to quote',
                    'Char ;090 to quote',
                    'Char Z to quote',
                    'DIR�',
                    'Fichier @ <root>',
                    'Fichier avec non asci char �velyne M�re.txt',
                    'Revisions',
                    'Répertoire (@vec) {càraçt#èrë} $épêcial',
                    'Répertoire Existant',
                    'Répertoire Supprimé',
                    'Subdirectory',
                    'SymlinkToSubdirectory',
                    'test\\test',
                    '이루마 YIRUMA - River Flows in You.mp3',
                ],
            ),
            ("with_children utf8_char", b"Subdirectory", ['Foldèr with éncodïng', 'LoopSymlink']),
            ("with_dir_utf8_char", b"Subdirectory/Fold\xc3\xa8r with \xc3\xa9ncod\xc3\xafng", ['my file']),
            ("with_dir", b"Revisions", ['Data']),
            ("with_file", b"Revisions/Data", DoesNotExistError),
            ("with_broken_symlink", b"BrokenSymlink", DoesNotExistError),
            ("with_loop_symlink", b"Subdirectory/LoopSymlink", ['Foldèr with éncodïng', 'LoopSymlink']),
            ("with_subdir_symlink", b"SymlinkToSubdirectory", ['Foldèr with éncodïng', 'LoopSymlink']),
        ]
    )
    def test_listdir(self, unused, path, listdir):
        if isclass(listdir) and issubclass(listdir, Exception):
            with self.assertRaises(listdir):
                self.repo.listdir(path)
            return
        self.assertEqual(listdir, sorted([d.display_name for d in self.repo.listdir(path)]))

    def test_listdir_outside_repo(self):
        with self.assertRaises(AccessDeniedError):
            self.repo.listdir(b"../")

    @skipIf(rdiff_backup_version() < (2, 0, 1), "rdiff-backup-delete is available since 2.0.1")
    def test_listdir_empty_folder(self):
        # Given a folder without data
        self.repo.delete(b"Revisions/Data")
        # When listing entries
        entries = self.repo.listdir(b"Revisions")
        # Then the list is empty.
        self.assertEqual([], entries)

    def test_listdir_attributes(self):
        children = self.repo.listdir(b"Revisions")
        self.assertEqual(1, len(children))
        dir_entry = children[0]
        self.assertEqual('Data', dir_entry.display_name)
        self.assertEqual(b'Revisions/Data', dir_entry.path)
        self.assertEqual(os.path.join(self.testcases_dir, b'Revisions/Data'), dir_entry.full_path)
        self.assertEqual(True, dir_entry.exists)
        self.assertEqual(False, dir_entry.isdir)
        self.assertEqual(False, dir_entry.isroot)
        self.assertEqual(9, dir_entry.file_size)
        self.assertEqual(
            [
                RdiffTime('2014-11-03T19:04:57-05:00'),
                RdiffTime('2014-11-05T16:04:30-05:00'),
                RdiffTime('2014-11-05T16:04:55-05:00'),
                RdiffTime('2014-11-05T16:05:07-05:00'),
                RdiffTime('2016-02-02T16:30:40-05:00'),
            ],
            list(dir_entry.change_dates),
        )

    def test_with_rdiff_backup_data(self):
        with self.assertRaises(DoesNotExistError):
            self.repo.fstat(b'rdiff-backup-data')
        with self.assertRaises(DoesNotExistError):
            self.repo.listdir(b'rdiff-backup-data')

    def test_with_invalid(self):
        with self.assertRaises(DoesNotExistError):
            self.repo.fstat(b'invalid')
        with self.assertRaises(DoesNotExistError):
            self.repo.listdir(b'invalid')

    def test_status(self):
        status = self.repo.status
        self.assertEqual('ok', status[0])
        self.assertEqual('', status[1])

    def test_status_access_denied_current_mirror(self):
        # Skip test if running as root. Because root as access to everything.
        if os.geteuid() == 0:
            return
        # Change the permissions of the files.
        os.chmod(
            os.path.join(self.testcases_dir, b'rdiff-backup-data', b'current_mirror.2016-02-02T16:30:40-05:00.data'),
            0000,
        )
        # Create repo again to query status
        self.repo = RdiffRepo(os.path.join(self.temp_dir, 'testcases'), encoding='utf-8')
        status = self.repo.status
        self.assertEqual('failed', status[0])

    def test_status_access_denied_rdiff_backup_data(self):
        # Skip test if running as root. Because root as access to everything.
        if os.geteuid() == 0:
            return
        # Change the permissions of the files.
        os.chmod(os.path.join(self.testcases_dir, b'rdiff-backup-data'), 0000)
        # Query status.
        self.repo = RdiffRepo(os.path.join(self.temp_dir, 'testcases'), encoding='utf-8')
        status = self.repo.status
        self.assertEqual('failed', status[0])
        # Make sure history entry doesn't raise error
        list(self.repo.mirror_metadata)

    def test_remove_older(self):
        # Given a repository with history
        self.assertEqual(22, len(self.repo.mirror_metadata))
        # When removing older then 1D
        self.repo.remove_older(1)
        # Then all history get deleted up to one
        self.assertEqual(1, len(self.repo.mirror_metadata))

    @parameterized.expand(
        [
            ("with_root", b'/', 1454448640, 'zip', 'testcases.zip', b'PK\x03\x04'),
            ("with_zip", b'Revisions', 1454448640, 'zip', 'Revisions.zip', b'PK\x03\x04'),
            ("with_tar", b'Revisions', 1454448640, 'tar', 'Revisions.tar', b'././@PaxHeader'),
            ("with_tar_gz", b'Revisions', 1454448640, 'tar.gz', 'Revisions.tar.gz', b'\x1f\x8b'),
            ("with_tar_bz2", b'Revisions', 1454448640, 'tar.bz2', 'Revisions.tar.bz2', b'BZh'),
            ("with_none_file", b'Revisions/Data', 1454448640, None, 'Data', b'Version3\n'),
            ("with_raw_file", b'Revisions/Data', 1454448640, 'raw', 'Data', b'Version3\n'),
            ("with_zip_file", b'Revisions/Data', 1454448640, 'zip', 'Data.zip', b'PK\x03\x04'),
        ]
    )
    def test_restore(self, unused, path, restore_as_of, kind, expected_filename, expected_startswith):
        filename, stream = self.repo.restore(path, restore_as_of=restore_as_of, kind=kind)
        self.assertEqual(expected_filename, filename)
        data = stream.read()
        self.assertTrue(data.startswith(expected_startswith))

    def test_unquote(self):
        self.assertEqual(b'Char ;090 to quote', unquote(b'Char ;059090 to quote'))

    def test_error_log_range(self):
        logs = self.repo.error_log[0:1]
        self.assertEqual(1, len(logs))
        self.assertEqual("", self.repo.error_log[0].read())

    def test_backup_log(self):
        self.assertEqual("", self.repo.backup_log.read())

    def test_restore_log(self):
        self.assertEqual(
            self.repo.restore_log.read(),
            """Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmpKDNO4t/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmpnG33kc/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmpGUEHJC/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmpBlFPsW/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmpkfCejo/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmphXpFnS as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/rdiffweb_restore_udS97a/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/rdiffweb_restore_LL4rCm/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/rdiffweb_restore_zpYgT3/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/rdiffweb_restore_7H93yy/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/rdiffweb_restore_Xe2CfG/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/rdiffweb_restore_rHFERA/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmpF7rSar/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmpgHTL2j/root as it was as of Wed Nov  5 16:05:07 2014.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmpVo1u4Z/root as it was as of Wed Jan 20 10:42:21 2016.
Starting restore of /home/ikus060/Downloads/testcases to /tmp/tmpBRxRxe/root as it was as of Wed Jan 20 10:42:21 2016.
""",
        )

    @parameterized.expand(
        [
            (
                "with_idx_1",
                1,
                '2014-11-01T15:50:26-04:00',
            ),
            (
                "with_idx_2",
                2,
                '2014-11-01T15:50:48-04:00',
            ),
            (
                "with_idx_3",
                3,
                '2014-11-01T15:51:15-04:00',
            ),
            (
                "with_neg_idx_1",
                -1,
                '2016-02-02T16:30:40-05:00',
            ),
            (
                "with_date",
                RdiffTime('2016-02-02T16:30:40-05:00'),
                '2016-02-02T16:30:40-05:00',
            ),
            (
                "with_slice_idx",
                slice(0, 2),
                [
                    '2014-11-01T15:49:47-04:00',
                    '2014-11-01T15:50:26-04:00',
                ],
            ),
            (
                "with_slice_date_start",
                slice(RdiffTime('2016-01-20T10:42:21-05:00'), None),
                ['2016-01-20T10:42:21-05:00', '2016-02-02T16:30:40-05:00'],
            ),
            (
                "with_slice_date_start_stop",
                slice(
                    RdiffTime('2014-11-02T17:00:00-05:00'),
                    RdiffTime('2014-11-04T00:00:00-05:00'),
                ),
                [
                    '2014-11-02T17:23:41-05:00',
                    '2014-11-03T15:46:47-05:00',
                    '2014-11-03T19:04:57-05:00',
                ],
            ),
            (
                "with_slice_date_start_stop_exact_match",
                slice(RdiffTime('2014-11-02T17:23:41-05:00'), RdiffTime('2014-11-03T19:04:57-05:00')),
                [
                    '2014-11-02T17:23:41-05:00',
                    '2014-11-03T15:46:47-05:00',
                    '2014-11-03T19:04:57-05:00',
                ],
            ),
            (
                "with_slice_invalid_idx",
                slice(100, 120),
                [],
            ),
            (
                "with_keyerror_date",
                RdiffTime('2022-11-03T15:46:47-05:00'),
                KeyError,
            ),
            (
                "with_keyerror_int",
                1024,
                KeyError,
            ),
        ]
    )
    def test_session_statistics(self, unsed, value, expected_value):
        if isinstance(expected_value, list):
            self.assertEqual(expected_value, [str(o.date) for o in self.repo.session_statistics[value]])
        elif isclass(expected_value) and issubclass(expected_value, Exception):
            with self.assertRaises(expected_value):
                self.repo.session_statistics[value]
        else:
            self.assertEqual(expected_value, str(self.repo.session_statistics[value].date))

    @parameterized.expand(
        [
            ("with_file", b'Revisions/Data'),
            ("with_folder", b'Subdirectory'),
            ("with_folder_ending_slash", b'Subdirectory/'),
            ("with_dir_utf8_char", b"Subdirectory/Fold\xc3\xa8r with \xc3\xa9ncod\xc3\xafng"),
            ("with_broken_symlink", b'BrokenSymlink'),
        ]
    )
    @skipIf(rdiff_backup_version() < (2, 0, 1), "rdiff-backup-delete is available since 2.0.1")
    def test_delete_file(self, unused, path):
        # Delete a file
        self.repo.delete(path)
        # Check file is deleted
        with self.assertRaises(DoesNotExistError):
            self.repo.fstat(path)


class SessionStatisticsEntryTest(unittest.TestCase):
    def test_getattr(self):
        """
        Check how a session statistic is read.
        """
        entry = SessionStatisticsEntry(MockRdiffRepo(), b'session_statistics.2014-11-02T09:16:43-05:00.data')
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


class RdiffTimeTest(unittest.TestCase):
    def test_add(self):
        """Check if addition with timedelta is working as expected."""
        # Without timezone
        self.assertEqual(
            RdiffTime('2014-11-08T21:04:30Z'), RdiffTime('2014-11-05T21:04:30Z') + datetime.timedelta(days=3)
        )
        # With timezone
        self.assertEqual(
            RdiffTime('2014-11-08T21:04:30-04:00'), RdiffTime('2014-11-05T21:04:30-04:00') + datetime.timedelta(days=3)
        )

    def test_compare(self):
        """Check behaviour of comparison operator operator."""

        self.assertTrue(RdiffTime('2014-11-07T21:04:30-04:00') < RdiffTime('2014-11-08T21:04:30Z'))
        self.assertTrue(RdiffTime('2014-11-08T21:04:30Z') < RdiffTime('2014-11-08T21:50:30Z'))
        self.assertFalse(RdiffTime('2014-11-08T22:04:30Z') < RdiffTime('2014-11-08T21:50:30Z'))

        self.assertFalse(RdiffTime('2014-11-07T21:04:30-04:00') > RdiffTime('2014-11-08T21:04:30Z'))
        self.assertFalse(RdiffTime('2014-11-08T21:04:30Z') > RdiffTime('2014-11-08T21:50:30Z'))
        self.assertTrue(RdiffTime('2014-11-08T22:04:30Z') > RdiffTime('2014-11-08T21:50:30Z'))

    def test_init_now(self):
        t0 = RdiffTime()
        self.assertAlmostEqual(int(time.time()), t0.epoch(), delta=5000)

    @parameterized.expand(
        [
            (1415221470, 1415221470),
            ('2014-11-05T21:04:30Z', 1415221470),
            ('2014-11-05T16:04:30-05:00', 1415221470),
            ('2014-11-05T23:04:30+02:00', 1415221470),
            ('2014-11-05T23-04-30+02-00', 1415221470),
        ]
    )
    def test_init(self, value, expected_epoch):
        t1 = RdiffTime(value)
        self.assertEqual(expected_epoch, t1.epoch())

    def test_int(self):
        """Check if int(RdiffTime) return expected value."""
        self.assertEqual(1415221470, int(RdiffTime(1415221470)))
        self.assertEqual(1415217870, int(RdiffTime(1415221470, 3600)))

    def test_str(self):
        """Check if __str__ is working."""
        self.assertEqual('2014-11-05T21:04:30Z', str(RdiffTime(1415221470)))
        self.assertEqual('2014-11-05T21:04:30+01:00', str(RdiffTime(1415221470, 3600)))

    def test_sub(self):
        """Check if addition with timedelta is working as expected."""
        # Without timezone
        self.assertEqual(
            RdiffTime('2014-11-02T21:04:30Z'), RdiffTime('2014-11-05T21:04:30Z') - datetime.timedelta(days=3)
        )
        # With timezone
        self.assertEqual(
            RdiffTime('2014-11-02T21:04:30-04:00'), RdiffTime('2014-11-05T21:04:30-04:00') - datetime.timedelta(days=3)
        )

        # With datetime
        self.assertTrue((RdiffTime('2014-11-02T21:04:30Z') - RdiffTime()).days < 0)
        self.assertTrue((RdiffTime() - RdiffTime('2014-11-02T21:04:30Z')).days > 0)

    def test_set_time(self):
        self.assertEqual(RdiffTime('2014-11-05T00:00:00Z'), RdiffTime('2014-11-05T21:04:30Z').set_time(0, 0, 0))
        self.assertEqual(
            RdiffTime('2014-11-02T00:00:00-04:00'), RdiffTime('2014-11-02T21:04:30-04:00').set_time(0, 0, 0)
        )
