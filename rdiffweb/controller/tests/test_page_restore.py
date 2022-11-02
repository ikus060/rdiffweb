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
Created on Jan 1, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import io
import tarfile
import unittest
import zipfile

import rdiffweb.test
from rdiffweb.controller.page_restore import _content_disposition
from rdiffweb.core.model import UserObject


class RestorePageTest(unittest.TestCase):
    def test_content_disposition(self):
        """
        Check value generated for different content-disposition.
        """
        # Simple ascii
        self.assertEqual('attachment; filename="foo.bar"', _content_disposition("foo.bar"))
        # ISO-8859-1 > UTF-8
        self.assertEqual("attachment; filename*=UTF-8''foo-%C3%A4.html", _content_disposition("foo-ä.html"))
        # Ascii filename with %
        self.assertEqual("attachment; filename*=UTF-8''foo-%2541.html", _content_disposition("foo-%41.html"))
        # Ascii filename with ;
        self.assertEqual("attachment; filename*=UTF-8''foo-%3B41.html", _content_disposition("foo-;41.html"))
        # Ascii filename with \
        self.assertEqual("attachment; filename*=UTF-8''foo-%5C41.html", _content_disposition("foo-\\41.html"))


class RestoreTest(rdiffweb.test.WebCase):

    login = True

    maxDiff = None

    def _restore(self, user, repo, path, date, kind=None):
        url = "/restore/" + user + "/" + repo + "/" + path
        if date:
            url += '?date=' + date
        if kind:
            url += '&kind=%s' % kind
        self.getPage(url)

    def test_broken_encoding(self):
        self._restore(
            self.USERNAME,
            self.REPO,
            "Fichier%20avec%20non%20asci%20char%20%C9velyne%20M%E8re.txt/",
            "1415221507",
            False,
        )
        self.assertBody("Centers the value\n")
        self.assertHeader(
            'Content-Disposition',
            'attachment; filename*=UTF-8\'\'Fichier%20avec%20non%20asci%20char%20%EF%BF%BDvelyne%20M%EF%BF%BDre.txt',
        )
        self.assertHeader('Content-Type', 'text/plain;charset=utf-8')

        self._restore(self.USERNAME, self.REPO, "DIR%EF%BF%BD/Data/", "1415059497", False)
        self.assertBody("My Data !\n")
        self.assertHeader('Content-Disposition', 'attachment; filename="Data"')
        self.assertHeader('Content-Type', 'application/octet-stream')

    def test_quoted(self):
        """
        Check names return for a quoted path.
        """
        self._restore(self.USERNAME, self.REPO, "Char%20%3B059090%20to%20quote/", "1415221507", "tar.gz")
        self.assertHeader('Content-Disposition', 'attachment; filename*=UTF-8\'\'Char%20%3B090%20to%20quote.tar.gz')
        self.assertHeader('Content-Type', 'application/x-gzip')

    def test_file(self):
        """
        Restore a simple file.
        """
        self._restore(self.USERNAME, self.REPO, "Fichier%20%40%20%3Croot%3E/", "1414921853", False)
        self.assertInBody("Ajout d'info")
        self.assertHeader('Content-Type', 'application/octet-stream')

    def test_broken_link(self):
        # Given a a broken symlink
        # When trying to retore the broken link
        self._restore(self.USERNAME, self.REPO, "BrokenSymlink", "1477434528", False)
        self.assertStatus(200)
        self.assertHeader('Content-Type', 'application/octet-stream')
        self.assertBody('')

    def test_with_quoted_vs_unquoted_path(self):
        """
        Restore file with quoted path.
        """
        # Char Z to quote
        self._restore(self.USERNAME, self.REPO, "Char%20%3B090%20to%20quote/Data/", "1414921853", False)
        self.assertStatus(200)
        self.assertBody("Bring me some Data !\n")
        self.assertHeader('Content-Type', 'application/octet-stream')

        # Char ;090 to quote
        self._restore(self.USERNAME, self.REPO, "Char%20%3B059090%20to%20quote/Data/", "1454448640", False)
        self.assertStatus(200)
        self.assertBody("Bring me some Data !\n")
        self.assertHeader('Content-Type', 'application/octet-stream')

        # Char ;059090 to quote
        self._restore(self.USERNAME, self.REPO, "Char%20%3B059059090%20to%20quote/Data/", "1453304541", False)
        self.assertStatus(200)
        self.assertBody("Bring me some Data !\n")
        self.assertHeader('Content-Type', 'application/octet-stream')

    def test_root_as_tar_gz(self):
        self._restore(self.USERNAME, self.REPO, "", "1414871387", "tar.gz")
        self.assertStatus(200)
        self.assertHeader('Content-Type', 'application/x-gzip')
        # Build expected files list
        expected = {}
        expected["Répertoire Supprimé"] = 0
        expected["Répertoire Supprimé/Untitled Empty Text File"] = 0
        expected["Répertoire Supprimé/Untitled Empty Text File 2"] = 0
        expected["Répertoire Supprimé/Untitled Empty Text File 3"] = 0
        expected["Fichier @ <root>"] = 0
        expected["Répertoire Existant"] = 0
        expected["Répertoire Existant/Untitled Empty Text File"] = 0
        expected["Répertoire Existant/Untitled Empty Text File 2"] = 0
        expected["Répertoire Existant/Fichier supprimé"] = 0

        #  Read the content as tar.gz with UTF8 encoding.
        actual = {}
        t = tarfile.open(mode='r:gz', fileobj=io.BytesIO(self.body))
        for m in t.getmembers():
            name = m.name
            if isinstance(name, bytes):
                name = name.decode('utf8')
            actual[name] = m.size
        t.close()
        #  Compare the tables.
        self.assertEqual(expected, actual)

    def test_root_as_tar_gz_recent(self):
        self._restore(self.USERNAME, self.REPO, "", "1415221507", "tar.gz")
        self.assertStatus(200)
        self.assertHeader('Content-Type', 'application/x-gzip')
        #  Read the content as tar.gz with UTF8 encoding.
        expected = {}
        expected["Fichier avec non asci char \udcc9velyne M\udce8re.txt"] = 18
        expected["이루마 YIRUMA - River Flows in You.mp3"] = 3636731
        expected["Char ;090 to quote"] = 0
        expected["Char ;090 to quote/Untitled Testcase.doc"] = 14848
        expected["Char ;090 to quote/Data"] = 21
        expected["DIR�"] = 0
        expected["DIR�/Data"] = 10
        expected["test\\test"] = 0
        expected["test\\test/some data"] = 226
        expected["Revisions"] = 0
        expected["Revisions/Data"] = 9
        expected["Répertoire (@vec) {càraçt#èrë} $épêcial"] = 0
        expected["Répertoire (@vec) {càraçt#èrë} $épêcial/Untitled Testcase.doc"] = 14848
        expected["<F!chïer> (@vec) {càraçt#èrë} $épêcial"] = 286
        expected["Fichier @ <root>"] = 13
        expected["Répertoire Existant"] = 0
        expected["Répertoire Existant/Untitled Empty Text File"] = 0
        expected["Répertoire Existant/Untitled Empty Text File 2"] = 0
        #  Read content as tar.gz.
        actual = {}
        t = tarfile.open(mode='r:gz', fileobj=io.BytesIO(self.body))
        for m in t.getmembers():
            name = m.name
            if isinstance(name, bytes):
                name = name.decode('utf8', 'replace')
            actual[name] = m.size
        t.close()
        #  Compare the tables.
        self.assertEqual(expected, actual)

    def test_root_as_zip(self):
        self._restore(self.USERNAME, self.REPO, "", "1414871387", kind='zip')
        self.assertStatus(200)
        self.assertHeader('Content-Type', 'application/zip')
        #  Read the content as tar.gz with UTF8 encoding.
        expected = {}
        expected["Répertoire Supprimé/"] = 0
        expected["Répertoire Supprimé/Untitled Empty Text File"] = 0
        expected["Répertoire Supprimé/Untitled Empty Text File 2"] = 0
        expected["Répertoire Supprimé/Untitled Empty Text File 3"] = 0
        expected["Fichier @ <root>"] = 0
        expected["Répertoire Existant/"] = 0
        expected["Répertoire Existant/Untitled Empty Text File"] = 0
        expected["Répertoire Existant/Untitled Empty Text File 2"] = 0
        expected["Répertoire Existant/Fichier supprimé"] = 0
        #  Read data as zip
        actual = {}
        t = zipfile.ZipFile(io.BytesIO(self.body), mode='r')
        for m in t.infolist():
            name = m.filename
            if isinstance(name, bytes):
                name = name.decode('utf8')
            actual[name] = m.file_size
        t.close()
        #  Compare the tables.
        self.assertEqual(expected, actual)

    def test_root_as_zip_recent(self):
        self._restore(self.USERNAME, self.REPO, "", "1415221507", kind='zip')
        self.assertStatus(200)
        self.assertHeader('Content-Type', 'application/zip')
        #  Read the content as tar.gz with UTF8 encoding.
        expected = {}
        expected["Fichier avec non asci char �velyne M�re.txt"] = 18
        expected["이루마 YIRUMA - River Flows in You.mp3"] = 3636731
        expected["Char ;090 to quote/"] = 0
        expected["Char ;090 to quote/Untitled Testcase.doc"] = 14848
        expected["Char ;090 to quote/Data"] = 21
        expected["DIR�/"] = 0
        expected["DIR�/Data"] = 10
        expected["test\\test/"] = 0
        expected["test\\test/some data"] = 226
        expected["Revisions/"] = 0
        expected["Revisions/Data"] = 9
        expected["Répertoire (@vec) {càraçt#èrë} $épêcial/"] = 0
        expected["Répertoire (@vec) {càraçt#èrë} $épêcial/Untitled Testcase.doc"] = 14848
        expected["<F!chïer> (@vec) {càraçt#èrë} $épêcial"] = 286
        expected["Fichier @ <root>"] = 13
        expected["Répertoire Existant/"] = 0
        expected["Répertoire Existant/Untitled Empty Text File"] = 0
        expected["Répertoire Existant/Untitled Empty Text File 2"] = 0
        #  Read data as zip
        actual = {}
        t = zipfile.ZipFile(io.BytesIO(self.body), mode='r')
        for m in t.infolist():
            name = m.filename
            if isinstance(name, bytes):
                name = name.decode('utf8')
            actual[name] = m.file_size
        t.close()
        #  Compare the tables.
        self.assertEqual(expected, actual)

    def test_root_as_tar_bz2(self):
        self._restore(self.USERNAME, self.REPO, "", '1415221507', 'tar.bz2')
        self.assertStatus(200)
        self.assertHeader('Content-Type', 'application/x-bzip2')
        #  Read content as tar.gz.
        actual = {}
        t = tarfile.open(mode='r:bz2', fileobj=io.BytesIO(self.body))
        for m in t.getmembers():
            name = m.name
            if isinstance(name, bytes):
                name = name.decode('utf8', 'replace')
            actual[name] = m.size
        t.close()
        #  Compare the tables.
        self.assertEqual(18, len(actual))

    def test_root_as_tar(self):
        self._restore(self.USERNAME, self.REPO, "", '1415221507', 'tar')
        self.assertStatus(200)
        self.assertHeader('Content-Type', 'application/x-tar')
        #  Read content as tar.gz.
        actual = {}
        t = tarfile.open(mode='r', fileobj=io.BytesIO(self.body))
        for m in t.getmembers():
            name = m.name
            if isinstance(name, bytes):
                name = name.decode('utf8', 'replace')
            actual[name] = m.size
        t.close()
        #  Compare the tables.
        self.assertEqual(18, len(actual))

    def test_subdirectory(self):
        self._restore(self.USERNAME, self.REPO, "R%C3%A9pertoire%20Existant/", "1414871475", "tar.gz")
        self.assertHeader('Content-Type', 'application/x-gzip')
        #  Read the content as tar.gz with UTF8 encoding.
        expected = {}
        expected["Untitled Empty Text File"] = 0
        expected["Untitled Empty Text File 2"] = 0
        expected["Fichier supprimé"] = 19
        #  Read content as tar.gz
        actual = {}
        t = tarfile.open(mode='r:gz', fileobj=io.BytesIO(self.body))
        for m in t.getmembers():
            name = m.name
            if isinstance(name, bytes):
                name = name.decode('utf8')
            actual[name] = m.size
        t.close()
        #  Compare the tables.
        self.assertEqual(expected, actual)

    def test_subdirectory_deleted(self):
        self._restore(self.USERNAME, self.REPO, "R%C3%A9pertoire%20Supprim%C3%A9/", "1414871475", "tar.gz")
        self.assertHeader('Content-Type', 'application/x-gzip')
        #  Read the content as tar.gz with UTF8 encoding.
        expected = {}
        expected["Untitled Empty Text File"] = 21
        expected["Untitled Empty Text File 2"] = 14
        expected["Untitled Empty Text File 3"] = 0
        #  Read content as tar.gz
        actual = {}
        t = tarfile.open(mode='r:gz', fileobj=io.BytesIO(self.body))
        for m in t.getmembers():
            name = m.name
            if isinstance(name, bytes):
                name = name.decode('utf8')
            actual[name] = m.size
        t.close()
        #  Compare the tables.
        self.assertEqual(expected, actual)

    def test_with_revisions(self):
        self._restore(self.USERNAME, self.REPO, "Revisions/Data/", "1415221470", False)
        self.assertBody("Version1\n")
        self.assertHeader('Content-Type', 'application/octet-stream')
        self._restore(self.USERNAME, self.REPO, "Revisions/Data/", "1415221495", False)
        self.assertBody("Version2\n")
        self.assertHeader('Content-Type', 'application/octet-stream')
        self._restore(self.USERNAME, self.REPO, "Revisions/Data/", "1415221507", False)
        self.assertBody("Version3\n")
        self.assertHeader('Content-Type', 'application/octet-stream')

    def test_invalid_date(self):
        self._restore(self.USERNAME, self.REPO, "Revisions/Data/", "1415221a470", False)
        self.assertStatus(400)

    def test_as_another_user(self):
        # Create a nother user with admin right
        user_obj = UserObject.add_user('anotheruser', 'password')
        user_obj.user_root = self.testcases
        user_obj.refresh_repos()
        user_obj.commit()
        self._restore("anotheruser", "testcases", "Fichier%20%40%20%3Croot%3E/", "1414921853")
        self.assertStatus('200 OK')
        self.assertInBody("Ajout d'info")

        # Remove admin right
        admin = UserObject.get_user('admin')
        admin.role = UserObject.USER_ROLE
        admin.commit()

        # Browse admin's repos
        self._restore("anotheruser", "testcases", "Fichier%20%40%20%3Croot%3E/", "1414921853")
        self.assertStatus('403 Forbidden')
