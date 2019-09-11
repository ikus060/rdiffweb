#!/usr/bin/python
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
Created on Jan 30, 2016

Test archiver module.

@author: Patrik Dufresne <info@patrikdufresne.com>
"""

from __future__ import unicode_literals

from future.builtins import str
import io
import os
import shutil
import sys
import tarfile
import tempfile
import threading
import unittest
from zipfile import ZipFile

from rdiffweb.core.archiver import archive
from rdiffweb.test import AppTestCase

PY3 = sys.version_info[0] == 3

EXPECTED = {}
EXPECTED["이루마 YIRUMA - River Flows in You.mp3"] = 3636731
EXPECTED["Char ;059090 to quote/"] = 0
EXPECTED["Char ;059090 to quote/Untitled Testcase.doc"] = 14848
EXPECTED["Char ;059090 to quote/Data"] = 21
EXPECTED["DIR�/"] = 0
EXPECTED["DIR�/Data"] = 10
EXPECTED["test\\test/"] = 0
EXPECTED["test\\test/some data"] = 226
EXPECTED["Revisions/"] = 0
EXPECTED["Revisions/Data"] = 9
EXPECTED["Subdirectory/"] = 0
EXPECTED["Subdirectory/Foldèr with éncodïng/"] = 0
EXPECTED["Subdirectory/Foldèr with éncodïng/my file"] = 58
EXPECTED["Répertoire (@vec) {càraçt#èrë} $épêcial/"] = 0
EXPECTED["Répertoire (@vec) {càraçt#èrë} $épêcial/Untitled Testcase.doc"] = 14848
EXPECTED["<F!chïer> (@vec) {càraçt#èrë} $épêcial"] = 286
EXPECTED["Fichier @ <root>"] = 13
EXPECTED["Répertoire Existant/"] = 0
EXPECTED["Répertoire Existant/Untitled Empty Text File"] = 0
EXPECTED["Répertoire Existant/Untitled Empty Text File 2"] = 0

# Add stuff specific to ZIP.
ZIP_EXPECTED = EXPECTED.copy()
ZIP_EXPECTED["Fichier avec non asci char �velyne M�re.txt"] = 18

# Add symlink to TAR.
TAR_EXPECTED = EXPECTED.copy()
TAR_EXPECTED["BrokenSymlink"] = 0
TAR_EXPECTED["Subdirectory/LoopSymlink"] = 0
TAR_EXPECTED["SymlinkToSubdirectory"] = 0
if PY3:
    TAR_EXPECTED["Fichier avec non asci char \udcc9velyne M\udce8re.txt"] = 18
else:
    TAR_EXPECTED["Fichier avec non asci char �velyne M�re.txt"] = 18


def archive_async(*args, **kwargs):
    thread = threading.Thread(target=archive, args=args, kwargs=kwargs)
    thread.start()


class ArchiverTest(AppTestCase):

    maxDiff = None

    reset_testcases = True

    def setUp(self):
        AppTestCase.setUp(self)

        # Remove rdiff-backup-data directory
        path = os.path.join(self.app.testcases.encode('ascii'), b'testcases', b'rdiff-backup-data')
        shutil.rmtree(path)

        # Define path to be archived
        self.path = os.path.join(self.app.testcases.encode('ascii'), b'testcases')
        assert os.path.isdir(self.path)

    def assertInZip(self, expected_files, filename, equal=True):
        """
        Check if the given `expected_files` exists in the Zip archive.
        """
        new_filename = None
        try:
            # If a stream is provided, dump it a file. ZipFile doesn't read file from a stream.
            if not isinstance(filename, str):
                f = filename
                filename = new_filename = tempfile.mktemp(prefix='rdiffweb_test_archiver_', suffix='.zip')
                with io.open(new_filename, 'wb') as out:
                    byte = f.read(4096)
                    while byte:
                        out.write(byte)
                        byte = f.read(4096)
                f.close()

            # Get data from zip.
            actual = {}
            a = ZipFile(filename)
            for m in a.infolist():
                name = m.filename
                if isinstance(name, bytes):
                    name = name.decode('utf8')
                actual[name] = m.file_size
            a.close()
            # Compare.
            if equal:
                self.assertEqual(expected_files, actual)
            else:
                for expected_file in expected_files:
                    self.assertIn(expected_file, actual)
        finally:
            if new_filename:
                os.remove(new_filename)

    def assertInTar(self, expected_files, filename, mode=None, equal=True):
        """
        Check if the given `expected_files` exists in the Zip archive.
        """
        if not mode:
            mode = 'r:'
            if filename.endswith('.bz2') or filename.endswith('.tbz2'):
                mode = 'r:bz2'
            elif filename.endswith('.gz') or filename.endswith('.tgz'):
                mode = 'r:gz'

        # Get data from zip.
        actual = {}
        if isinstance(filename, str):
            t = tarfile.open(name=filename, mode=mode)
        else:
            t = tarfile.open(fileobj=filename, mode=mode)
        for m in t.getmembers():
            name = m.name
            if isinstance(name, bytes):
                name = name.decode('utf8')
            if m.isdir():
                name += "/"
            actual[name] = m.size
        t.close()
        if hasattr(filename, 'close'):
            filename.close()
        # Compare.
        if equal:
            self.assertEqual(expected_files, actual)
        else:
            for expected_file in expected_files:
                self.assertIn(expected_file, actual)

    def test_pipe_zip_file(self):
        """
        Check creation of a zip trough a pipe.
        """
        rfd, wfd = os.pipe()
        # Run archiver
        archive_async(self.path, io.open(wfd, 'wb'), encoding='utf-8', kind='zip')
        # Check result.
        self.assertInZip(ZIP_EXPECTED, io.open(rfd, 'rb'))

    def test_zip_file(self):
        """
        Check creation of a zipfile.
        """
        # Define path to be archived
        filename = tempfile.mktemp(prefix='rdiffweb_test_archiver_', suffix='.zip')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                archive(self.path, f, encoding='utf-8', kind='zip')
            # Check result.
            self.assertInZip(ZIP_EXPECTED, filename)
        finally:
            os.remove(filename)

    def test_zip_file_cp1252(self):
        """
        Check if archiver support different encoding.
        """
        # Define path to be archived
        filename = tempfile.mktemp(prefix='rdiffweb_test_archiver_', suffix='.zip')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                archive(self.path, f, encoding='cp1252', kind='zip')
            # Check result.
            expected = {
                "Fichier avec non asci char Évelyne Mère.txt": 18,
            }
            self.assertInZip(expected, filename, equal=False)
        finally:
            os.remove(filename)

    def test_pipe_tar_file(self):
        """
        Check creation of tar.gz.
        """
        rfd, wfd = os.pipe()
        # Run archiver
        archive_async(self.path, io.open(wfd, 'wb'), encoding='utf-8', kind='tar')
        # Check result.
        self.assertInTar(TAR_EXPECTED, io.open(rfd, 'rb'), mode='r|')

    def test_tar_file(self):
        """
        Check creation of tar.gz.
        """
        filename = tempfile.mktemp(prefix='rdiffweb_test_archiver_', suffix='.tar')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                archive(self.path, f, encoding='utf-8', kind='tar')
            # Check result.
            self.assertInTar(TAR_EXPECTED, filename)
        finally:
            os.remove(filename)

    def test_tar_file_cp1252(self):
        """
        Check if archiver support different encoding.
        """
        filename = tempfile.mktemp(prefix='rdiffweb_test_archiver_', suffix='.tar')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                archive(self.path, f, encoding='cp1252', kind='tar')
            # Check result.
            expected = {
                "Fichier avec non asci char Évelyne Mère.txt": 18,
            }
            self.assertInTar(expected, filename, equal=False)
        finally:
            os.remove(filename)

    def test_pipe_tar_gz_file(self):
        """
        Check creation of tar.gz.
        """
        rfd, wfd = os.pipe()
        # Run archiver
        archive_async(self.path, io.open(wfd, 'wb'), encoding='utf-8', kind='tar.gz')
        # Check result.
        self.assertInTar(TAR_EXPECTED, io.open(rfd, 'rb'), mode='r|gz')

    def test_tar_gz_file(self):
        """
        Check creation of tar.gz.
        """
        filename = tempfile.mktemp(prefix='rdiffweb_test_archiver_', suffix='.tar.gz')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                archive(self.path, f, encoding='utf-8', kind='tar.gz')
            # Check result.
            self.assertInTar(TAR_EXPECTED, filename)
        finally:
            os.remove(filename)

    def test_pipe_tar_bz2_file(self):
        """
        Check creation of tar.gz.
        """
        rfd, wfd = os.pipe()
        # Run archiver
        archive_async(self.path, io.open(wfd, 'wb'), encoding='utf-8', kind='tar.bz2')
        # Check result.
        self.assertInTar(TAR_EXPECTED, io.open(rfd, 'rb') , mode='r|bz2')

    def test_tar_bz2_file(self):
        """
        Check creation of tar.bz2.
        """
        filename = tempfile.mktemp(prefix='rdiffweb_test_archiver_', suffix='.tar.bz2')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                archive(self.path, f, encoding='utf-8', kind='tar.bz2')
            # Check result.
            self.assertInTar(TAR_EXPECTED, filename)
        finally:
            os.remove(filename)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
