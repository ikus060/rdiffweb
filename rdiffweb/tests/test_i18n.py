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
Created on Apr 25, 2015

Module used to test the i18n tools. Check if translation are properly loaded.

@author: ikus060
"""
from __future__ import unicode_literals

import cherrypy
import gettext
import pkg_resources
import unittest

from rdiffweb import i18n


class Test(unittest.TestCase):

    def setUp(self):
        self.mo_dir = pkg_resources.resource_filename('rdiffweb', 'locales')  # @UndefinedVariable

    def tearDown(self):
        pass

    def test_load_translation(self):
        # Load default translation
        t = i18n.load_translation()
        self.assertTrue(isinstance(t, gettext.GNUTranslations))
        self.assertEqual("en", t._lang)

    def test_load_translation_with_accept_language_fr(self):
        # Mock a header
        cherrypy.request.headers["Accept-Language"] = "fr_CA,fr,en_en_US"
        # Load default translation
        t = i18n.load_translation()
        self.assertTrue(isinstance(t, gettext.GNUTranslations))
        self.assertEqual("fr", t._lang)

    def test_load_translation_with_accept_language_unknown(self):
        # Mock a header
        cherrypy.request.headers["Accept-Language"] = "br_CA"
        # Load default translation
        t = i18n.load_translation()
        self.assertTrue(isinstance(t, gettext.GNUTranslations))
        self.assertEqual("en", t._lang)

    def test_translation_with_fr(self):
        # Get trans
        t = i18n._translation("messages", [self.mo_dir], ["fr"])
        self.assertTrue(isinstance(t, gettext.GNUTranslations))
        self.assertEqual("fr", t._lang)
        # Test translation object
        self.assertEqual("Modifier", t.gettext("Edit"))
        # Check if the translation fallback
        self.assertEqual("Invalid String", t.gettext("Invalid String"))
        pass

    def test_translation_with_en(self):
        # Get trans
        t = i18n._translation("messages", [self.mo_dir], ["en"])
        self.assertTrue(isinstance(t, gettext.GNUTranslations))
        self.assertEqual("en", t._lang)
        pass

    def test_translation_with_en_us(self):
        # Get trans
        t = i18n._translation("messages", [self.mo_dir], ["en_US"])
        self.assertTrue(isinstance(t, gettext.GNUTranslations))
        self.assertEqual("en", t._lang)
        pass

    def test_translation_with_fr_ca(self):
        # Get trans
        t = i18n._translation("messages", [self.mo_dir], ["fr_CA"])
        self.assertTrue(isinstance(t, gettext.GNUTranslations))
        self.assertEqual("fr", t._lang)
        pass

    def test_translation_with_en_fr(self):
        # Get trans
        t = i18n._translation("messages", [self.mo_dir], ["en", "fr"])
        self.assertTrue(isinstance(t, gettext.GNUTranslations))
        self.assertEqual("en", t._lang)
        # Test translation object
        self.assertEqual("Edit", t.gettext("Edit"))
        # Check if the translation fallback
        self.assertEqual("Invalid String", t.gettext("Invalid String"))
        pass

    def test_translation_with_fr_en(self):
        # Get trans
        t = i18n._translation("messages", [self.mo_dir], ["fr", "en"])
        self.assertTrue(isinstance(t, gettext.GNUTranslations))
        self.assertEqual("fr", t._lang)
        # Test translation object
        self.assertEqual("Modifier", t.gettext("Edit"))
        pass

    def test_translation_with_unknown(self):
        # Get trans
        t = i18n._translation("messages", [self.mo_dir], ["br"])
        self.assertTrue(isinstance(t, gettext.NullTranslations))
        self.assertEqual("en", t._lang)
        pass


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
