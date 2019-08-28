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
"""
Created on Jan 1, 2016

@author: Patrik Dufresne <info@patrikdufresne.com>
"""

from __future__ import unicode_literals

import io
import logging
import sys
import tarfile
import unittest
import zipfile

from rdiffweb.controller.page_restore import _content_disposition
from rdiffweb.test import WebCase, AppTestCase


PY3 = sys.version_info[0] == 3


class RestorePageTest(AppTestCase):

    def setUp(self):
        AppTestCase.setUp(self)
        self.page = self.app.root.restore

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


class RestoreTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    maxDiff = None

    def _restore(self, repo, path, date, usetar, kind=None):
        url = "/restore/" + repo + "/" + path
        if date:
            url += '?date=' + date
        if usetar:
            url += '&usetar=T'
        if kind:
            url += '&kind=%s' % kind
        self.getPage(url)

    def test_broken_encoding(self):
        self._restore(self.REPO, "Fichier%20avec%20non%20asci%20char%20%C9velyne%20M%E8re.txt/", "1415221507", True)
        self.assertBody("Centers the value\n")
        self.assertHeader('Content-Disposition', 'attachment; filename*=UTF-8\'\'Fichier%20avec%20non%20asci%20char%20%EF%BF%BDvelyne%20M%EF%BF%BDre.txt')
        self.assertHeader('Content-Type', 'text/plain;charset=utf-8')

        self._restore(self.REPO, "DIR%EF%BF%BD/Data/", "1415059497", True)
        self.assertBody("My Data !\n")
        self.assertHeader('Content-Disposition', 'attachment; filename="Data"')
        self.assertHeader('Content-Type', 'application/octet-stream')

    def test_quoted(self):
        """
        Check names return for a quoted path.
        """
        self._restore(self.REPO, "Char%20%3B059090%20to%20quote/", "1415221507", True)
        self.assertHeader('Content-Disposition', 'attachment; filename*=UTF-8\'\'Char%20%3B090%20to%20quote.tar.gz')
        self.assertHeader('Content-Type', 'application/x-gzip')

    def test_file(self):
        """
        Restore a simple file.
        """
        self._restore(self.REPO, "Fichier%20%40%20%3Croot%3E/", "1414921853", True)
        self.assertInBody("Ajout d'info")
        self.assertHeader('Content-Type', 'application/octet-stream')

    def test_with_quoted_path(self):
        """
        Restore file with quoted path.
        """
        self._restore(self.REPO, "Char%20%3B090%20to%20quote/Data/", "1414921853", True)
        self.assertBody("Bring me some Data !\n")
        self.assertHeader('Content-Type', 'application/octet-stream')

    def test_root_as_tar_gz(self):
        self._restore(self.REPO, "", "1414871387", True)
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
        self._restore(self.REPO, "", "1415221507", True)
        self.assertStatus(200)
        self.assertHeader('Content-Type', 'application/x-gzip')
        #  Read the content as tar.gz with UTF8 encoding.
        expected = {}
        if PY3:
            expected["Fichier avec non asci char \udcc9velyne M\udce8re.txt"] = 18
        else:
            expected["Fichier avec non asci char �velyne M�re.txt"] = 18
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
        self._restore(self.REPO, "", "1414871387", False)
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
        self._restore(self.REPO, "", "1415221507", False)
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
        self._restore(self.REPO, "", '1415221507', False, 'tar.bz2')
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
        self._restore(self.REPO, "", '1415221507', False, 'tar')
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
        self._restore(self.REPO, "R%C3%A9pertoire%20Existant/", "1414871475", True)
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
        self._restore(self.REPO, "R%C3%A9pertoire%20Supprim%C3%A9/", "1414871475", True)
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
        self._restore(self.REPO, "Revisions/Data/", "1415221470", True)
        self.assertBody("Version1\n")
        self.assertHeader('Content-Type', 'application/octet-stream')
        self._restore(self.REPO, "Revisions/Data/", "1415221495", True)
        self.assertBody("Version2\n")
        self.assertHeader('Content-Type', 'application/octet-stream')
        self._restore(self.REPO, "Revisions/Data/", "1415221507", True)
        self.assertBody("Version3\n")
        self.assertHeader('Content-Type', 'application/octet-stream')

    def test_invalid_date(self):
        self._restore(self.REPO, "Revisions/Data/", "1415221a470", True)
        self.assertStatus(400)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
