# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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
from datetime import datetime, timezone

import cherrypy
import pkg_resources
from cherrypy import _cpconfig

import rdiffweb.test
from rdiffweb.tools import i18n


class Test(unittest.TestCase):
    def setUp(self):
        self.mo_dir = pkg_resources.resource_filename('rdiffweb', 'locales')  # @UndefinedVariable
        cherrypy.request.config = _cpconfig.Config()

    def test_search_translation(self):
        # Load default translation
        t = i18n._search_translation('en', self.mo_dir, 'messages')
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("en", t.locale.language)

    def test_search_translation_with_date_format(self):
        # Get trans
        t = i18n._search_translation('fr_CA', self.mo_dir, 'messages')
        self.assertIsInstance(t, gettext.GNUTranslations)
        self.assertEqual("fr", t.locale.language)
        # Test translation object
        self.assertEqual("Modifier", t.gettext("Edit"))


class TestI18nWebCase(rdiffweb.test.WebCase):
    def test_language_with_unknown(self):
        #  Query the page without login-in
        self.getPage("/login/", headers=[("Accept-Language", "it")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "en")
        self.assertInBody("Sign in")

    def test_language_en(self):
        self.getPage("/login/", headers=[("Accept-Language", "en-US,en;q=0.8")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "en")
        self.assertInBody("Sign in")

    def test_language_en_fr(self):
        self.getPage("/login/", headers=[("Accept-Language", "en-US,en;q=0.8,fr-CA;q=0.8")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "en")
        self.assertInBody("Sign in")

    def test_language_fr(self):
        self.getPage("/login/")
        self.assertInBody("Sign in")
        self.getPage("/login/", headers=[("Accept-Language", "fr-CA;q=0.8,fr;q=0.6")])
        self.assertStatus('200 OK')
        self.assertHeaderItemValue("Content-Language", "fr")
        self.assertInBody("Se connecter")

    def test_with_preferred_lang(self):
        # Given a default lang 'en'
        date = datetime.utcfromtimestamp(1680111611).replace(tzinfo=timezone.utc)
        self.assertEqual('Sign in', i18n.ugettext('Sign in'))
        self.assertIn('March', i18n.format_datetime(date, format='long'))
        # When using preferred_lang with french
        with i18n.preferred_lang('fr'):
            # Then french translation is used
            self.assertEqual('Se connecter', i18n.ugettext('Sign in'))
            # Then date time formating used french locale
            self.assertIn('mars', i18n.format_datetime(date, format='long'))
        # Then ouside the block, settings goest back to english
        self.assertEqual('Sign in', i18n.ugettext('Sign in'))
        self.assertIn('March', i18n.format_datetime(date, format='long'))


class TestI18nDefaultLangWebCase(rdiffweb.test.WebCase):
    default_config = {'default-lang': 'FR'}

    @classmethod
    def teardown_class(cls):
        # Reset default-lang to avoid issue with other test
        cherrypy.config['tools.i18n.default'] = 'en'
        super().teardown_class()

    def test_default_lang_without_accept_language(self):
        # Given a default language
        # When user connect to the application without Accept-Language
        self.getPage("/login/")
        self.assertStatus(200)
        # Then page is displayed with default lang
        self.assertInBody('lang="fr"')

    def test_default_lang_with_accept_language(self):
        # Given a default language
        # When user connect to the application with Accept-Language English
        self.getPage("/login/", headers=[("Accept-Language", "en-US,en;q=0.8")])
        self.assertStatus(200)
        # Then page is displayed as english
        self.assertInBody('lang="en"')

    def test_default_lang_with_unknown_accept_language(self):
        # Given a default language
        # When user connect to the application with Accept-Language English
        self.getPage("/login/", headers=[("Accept-Language", "it")])
        self.assertStatus(200)
        # Then page is displayed as english
        self.assertInBody('lang="fr"')


class TestI18nInvalidDefaultLangWebCase(rdiffweb.test.WebCase):
    default_config = {'default-lang': 'invalid'}

    def test_default_lang_invalid(self):
        # Given an invalid default language
        # When user connect to the application without Accept-Language
        self.getPage("/login/")
        self.assertStatus(200)
        # Then page is displayed with fallback to "en"
        self.assertInBody('lang="en"')
