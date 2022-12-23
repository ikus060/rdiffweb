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
Created on Apr 25, 2015

Module used to test the i18n tools. Check if translation are properly loaded.

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import gettext
import unittest

import cherrypy
import pkg_resources
from cherrypy import _cpconfig

import rdiffweb.test
from rdiffweb.tools import i18n


class Test(unittest.TestCase):
    def setUp(self):
        self.mo_dir = pkg_resources.resource_filename('rdiffweb', 'locales')  # @UndefinedVariable
        cherrypy.request.config = _cpconfig.Config()

    def tearDown(self):
        del cherrypy.response.i18n

    def test_get_i18n(self):
        # Load default translation
        i18n._get_i18n(self.mo_dir, 'en', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("en", l.language)

    def test_get_i18n_with_accept_language_fr(self):
        # Mock a header
        cherrypy.request.headers["Accept-Language"] = "fr_CA,fr,en_en_US"
        # Load default translation
        i18n._get_i18n(self.mo_dir, 'en_US', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("fr", l.language)

    def test_get_i18n_with_accept_language_unknown(self):
        # Mock a header
        cherrypy.request.headers["Accept-Language"] = "br_CA"
        # Load default translation
        i18n._get_i18n(self.mo_dir, 'en_US', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("en", l.language)

    def test_get_i18n_with_fr(self):
        # Get trans
        i18n._get_i18n(self.mo_dir, 'fr', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("fr", l.language)
        # Test translation object
        self.assertEqual("Modifier", t.gettext("Edit"))
        # Check if the translation fallback
        text = "Invalid String"
        self.assertEqual("Invalid String", t.gettext(text))

    def test_get_i18n_with_en(self):
        # Get trans
        i18n._get_i18n(self.mo_dir, 'en', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("en", l.language)

    def test_get_i18n_with_en_us(self):
        # Get trans
        i18n._get_i18n(self.mo_dir, 'en_US', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("en", l.language)

    def test_get_i18n_with_fr_ca(self):
        # Get trans
        i18n._get_i18n(self.mo_dir, 'fr_CA', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("fr", l.language)

    def test_get_i18n_with_en_fr(self):
        # Get trans
        i18n._get_i18n(self.mo_dir, 'en', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("en", l.language)
        # Test translation object
        self.assertEqual("Edit", t.gettext("Edit"))
        # Check if the translation fallback
        text = "Invalid String"
        self.assertEqual("Invalid String", t.gettext(text))

    def test_get_i18n_with_fr_en(self):
        # Get trans
        i18n._get_i18n(self.mo_dir, 'fr', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("fr", l.language)
        # Test translation object
        self.assertEqual("Modifier", t.gettext("Edit"))

    def test_get_i18n_with_date_format(self):
        # Get trans
        i18n._get_i18n(self.mo_dir, 'fr_CA', 'messages')
        t = cherrypy.response.i18n.trans
        l = cherrypy.response.i18n.locale
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("fr", l.language)
        # Test translation object
        self.assertEqual("Modifier", t.gettext("Edit"))


class TestI18nWebCase(rdiffweb.test.WebCase):
    def test_language_with_unknown(self):
        #  Query the page without login-in
        self.getPage("/login/", headers=[("Accept-Language", "it")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "en_US")
        self.assertInBody("Sign in")

    def test_language_en(self):
        self.getPage("/login/", headers=[("Accept-Language", "en-US,en;q=0.8")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "en_US")
        self.assertInBody("Sign in")

    def test_language_en_fr(self):
        self.getPage("/login/", headers=[("Accept-Language", "en-US,en;q=0.8,fr-CA;q=0.8")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "en_US")
        self.assertInBody("Sign in")

    def test_language_fr(self):
        self.getPage("/login/")
        self.assertInBody("Sign in")
        self.getPage("/login/", headers=[("Accept-Language", "fr-CA;q=0.8,fr;q=0.6")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "fr_CA")
        self.assertInBody("Se connecter")

    def test_language_between_session(self):
        # Make a request with Accept-Language
        self.getPage("/login/", headers=[("Accept-Language", "fr-CA;q=0.8,fr;q=0.6")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "fr_CA")
        self.assertInBody("Se connecter")
        # Make a second request without Accept-Language
        self.getPage("/login/")
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "fr_CA")
        self.assertInBody("Se connecter")
