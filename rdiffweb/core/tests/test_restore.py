# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import io
import os
import tarfile
import tempfile
import unittest
from zipfile import ZipFile

import rdiffweb.test
from rdiffweb.core.librdiff import find_rdiff_backup
from rdiffweb.core.restore import RestoreException, _restore, pipe_restore

EXPECTED = {}
EXPECTED["이루마 YIRUMA - River Flows in You.mp3"] = 3636731
EXPECTED["Char ;090 to quote/"] = 0
EXPECTED["Char ;090 to quote/Untitled Testcase.doc"] = 14848
EXPECTED["Char ;090 to quote/Data"] = 21
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
TAR_EXPECTED["Fichier avec non asci char \udcc9velyne M\udce8re.txt"] = 18


class RestoreTest(rdiffweb.test.WebCase):
    maxDiff = None

    def setUp(self):
        super().setUp()

        # Define path to be archived
        self.path = os.path.join(self.testcases.encode('ascii'), b'testcases')
        assert os.path.isdir(self.path)

        # Define location of rdiff-backup
        self.rdiff_backup = find_rdiff_backup()

    def assertInZip(self, expected_files, filename, equal=True):
        """
        Check if the given `expected_files` exists in the Zip archive.
        """
        new_filename = None
        try:
            # If a stream is provided, dump it a file. ZipFile doesn't read file from a stream.
            if not isinstance(filename, str):
                f = filename
                filename = new_filename = tempfile.mktemp(prefix='rdiffweb_test_restore_archiver_', suffix='.zip')
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

    def test_restore_pipe_zip_file(self):
        """
        Check creation of a zip trough a pipe.
        """
        # Run archiver
        fileobj = pipe_restore(self.rdiff_backup, self.path, restore_as_of=1454448640, encoding='utf-8', kind='zip')
        # Check result.
        self.assertInZip(ZIP_EXPECTED, fileobj)

    def test_restore_raw_singlefile(self):
        # Define path to be archived
        filename = tempfile.mktemp(prefix='rdiffweb_test_restore_archiver_')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                _restore(
                    self.rdiff_backup,
                    os.path.join(self.path, b'Fichier @ <root>'),
                    restore_as_of=1454448640,
                    dest=f,
                    encoding='utf-8',
                    kind='raw',
                )
            # Check result.
            with open(filename, 'rb') as f:
                self.assertEqual(f.read(), b"Ajout d'info\n")
        finally:
            os.remove(filename)

    def test_restore_raw_quote_vs_unquote(self):
        # Define path to be archived
        filename = tempfile.mktemp(prefix='rdiffweb_test_restore_archiver_')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                _restore(
                    self.rdiff_backup,
                    os.path.join(self.path, b'Char ;090 to quote', b'Data'),
                    restore_as_of=1454448640,
                    dest=f,
                    encoding='utf-8',
                    kind='raw',
                )
            # Check result.
            with open(filename, 'rb') as f:
                self.assertEqual(f.read(), b"Bring me some Data !\n")
            # Run archiver
            with open(filename, 'wb') as f:
                _restore(
                    self.rdiff_backup,
                    os.path.join(self.path, b'Char Z to quote', b'Data'),
                    restore_as_of=1414921853,
                    dest=f,
                    encoding='utf-8',
                    kind='raw',
                )
            # Check result.
            with open(filename, 'rb') as f:
                self.assertEqual(f.read(), b"Bring me some Data !\n")
        finally:
            os.remove(filename)

    def test_restore_zip_file(self):
        """
        Check creation of a zipfile.
        """
        # Define path to be archived
        filename = tempfile.mktemp(prefix='rdiffweb_test_restore_archiver_', suffix='.zip')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                _restore(self.rdiff_backup, self.path, restore_as_of=1454448640, dest=f, encoding='utf-8', kind='zip')
            # Check result.
            self.assertInZip(ZIP_EXPECTED, filename)
        finally:
            os.remove(filename)

    def test_restore_zip_file_cp1252(self):
        """
        Check if archiver support different encoding.
        """
        # Define path to be archived
        filename = tempfile.mktemp(prefix='rdiffweb_test_restore_archiver_', suffix='.zip')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                _restore(self.rdiff_backup, self.path, restore_as_of=1454448640, dest=f, encoding='cp1252', kind='zip')
            # Check result.
            expected = {
                "Fichier avec non asci char Évelyne Mère.txt": 18,
            }
            self.assertInZip(expected, filename, equal=False)
        finally:
            os.remove(filename)

    def test_restore_pipe_tar_file(self):
        """
        Check creation of tar.gz.
        """
        # Run archiver
        fileobj = pipe_restore(self.rdiff_backup, self.path, restore_as_of=1454448640, encoding='utf-8', kind='tar')
        # Check result.
        self.assertInTar(TAR_EXPECTED, fileobj, mode='r|')

    def test_restore_tar_file(self):
        """
        Check creation of tar.gz.
        """
        filename = tempfile.mktemp(prefix='rdiffweb_test_restore_archiver_', suffix='.tar')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                _restore(self.rdiff_backup, self.path, restore_as_of=1454448640, dest=f, encoding='utf-8', kind='tar')
            # Check result.
            self.assertInTar(TAR_EXPECTED, filename)
        finally:
            os.remove(filename)

    def test_restore_tar_file_cp1252(self):
        """
        Check if archiver support different encoding.
        """
        filename = tempfile.mktemp(prefix='rdiffweb_test_restore_archiver_', suffix='.tar')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                _restore(self.rdiff_backup, self.path, restore_as_of=1454448640, dest=f, encoding='cp1252', kind='tar')
            # Check result.
            expected = {
                "Fichier avec non asci char Évelyne Mère.txt": 18,
            }
            self.assertInTar(expected, filename, equal=False)
        finally:
            os.remove(filename)

    def test_restore_pipe_tar_gz_file(self):
        """
        Check creation of tar.gz.
        """
        # Run archiver
        fileobj = pipe_restore(self.rdiff_backup, self.path, restore_as_of=1454448640, encoding='utf-8', kind='tar.gz')
        # Check result.
        self.assertInTar(TAR_EXPECTED, fileobj, mode='r|gz')

    def test_restore_tar_gz_file(self):
        """
        Check creation of tar.gz.
        """
        filename = tempfile.mktemp(prefix='rdiffweb_test_restore_archiver_', suffix='.tar.gz')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                _restore(
                    self.rdiff_backup, self.path, restore_as_of=1454448640, dest=f, encoding='utf-8', kind='tar.gz'
                )
            # Check result.
            self.assertInTar(TAR_EXPECTED, filename)
        finally:
            os.remove(filename)

    def test_restore_pipe_tar_bz2_file(self):
        """
        Check creation of tar.gz.
        """
        # Run archiver
        fileobj = pipe_restore(self.rdiff_backup, self.path, restore_as_of=1454448640, encoding='utf-8', kind='tar.bz2')
        # Check result.
        self.assertInTar(TAR_EXPECTED, fileobj, mode='r|bz2')

    def test_restore_tar_bz2_file(self):
        """
        Check creation of tar.bz2.
        """
        filename = tempfile.mktemp(prefix='rdiffweb_test_restore_archiver_', suffix='.tar.bz2')
        try:
            # Run archiver
            with open(filename, 'wb') as f:
                _restore(
                    self.rdiff_backup, self.path, restore_as_of=1454448640, dest=f, encoding='utf-8', kind='tar.bz2'
                )
            # Check result.
            self.assertInTar(TAR_EXPECTED, filename)
        finally:
            os.remove(filename)

    def test_restore_pipe_single_file(self):
        # Given a single file
        path = os.path.join(self.path, b'Revisions/Data')
        # When trying to restore that file
        fileobj = pipe_restore(self.rdiff_backup, path, restore_as_of=1454448640, encoding='utf-8', kind='raw')
        # Then file content is returned
        with fileobj:
            data = fileobj.read()
        self.assertEqual(b'Version3\n', data)

    def test_restore_pipe_invalid_file(self):
        # Given a single file
        path = os.path.join(self.path, b'Revisions/invalid')
        # When trying to restore that file
        # Then an error get raised
        with self.assertRaises(RestoreException):
            pipe_restore(self.rdiff_backup, path, restore_as_of=1454448640, encoding='utf-8', kind='raw')

    def test_restore_pipe_with_interrupted_repo(self):
        # Given a repository with last backup interrupted
        new_current_mirror = os.path.join(self.path, b'rdiff-backup-data/current_mirror.2024-12-04T16:30:40-05:00.data')
        with open(new_current_mirror, 'w') as f:
            f.write('1234')
        # When trying to restore a file
        # Then an error get raised
        path = os.path.join(self.path, b'Revisions/Data')
        with self.assertRaises(RestoreException):
            pipe_restore(self.rdiff_backup, path, restore_as_of=1454448640, encoding='utf-8', kind='raw')


if __name__ == "__main__":
    unittest.main()
