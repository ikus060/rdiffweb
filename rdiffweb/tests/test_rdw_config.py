#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 rdiffweb contributors
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

import os
import unittest

from rdiffweb.rdw_config import Configuration, SettingsError


class ConfigurationTest(unittest.TestCase):
    """
    Unit tests for the get_config() function
    """

    good_config_text = """ #This=is a comment
SpacesValue=is a setting with spaces
spaces setting=withspaces
CommentInValue=Value#this is a comment
NoValue=#This is a setting with no value
"""
    bad_config_texts = [
        'This#doesnt have an equals',
        'This=more=than one equals']

    config_file_path = "/tmp/rdw_config.conf"

    def write_good_file(self):
        f = open(self.config_file_path, "w")
        f.write(self.good_config_text)
        f.close()
        self.config = Configuration(self.config_file_path)

    def write_bad_file(self, bad_setting_num):
        self.write_good_file()
        f = open(self.config_file_path, "w")
        f.write(self.bad_config_texts[bad_setting_num])
        f.close()
        self.config = Configuration(self.config_file_path)

    def tearDown(self):
        if (os.access(self.config_file_path, os.F_OK)):
            os.remove(self.config_file_path)

    def test_get_config_badparms(self):
        self.write_good_file()
        with self.assertRaises(AssertionError):
            self.config.get_config("setting=")

    def test_get_config_spaces_in_value(self):
        self.write_good_file()
        self.assertEqual("is a setting with spaces", self.config.get_config("SpacesValue"))

    def test_get_config_spaces_in_setting(self):
        self.write_good_file()
        self.assertEqual("withspaces", self.config.get_config("spaces setting"))

    def test_get_config_comment_in_value(self):
        self.write_good_file()
        self.assertEqual("Value", self.config.get_config("CommentInValue"))

    def test_get_config_emptyvalue(self):
        self.write_good_file()
        self.assertEqual("", self.config.get_config("NoValue"))

    def test_get_config_case_insensitivity(self):
        self.write_good_file()
        self.assertEqual("Value", self.config.get_config("commentinvalue"))

    def test_get_config_missingsetting(self):
        self.write_good_file()
        self.assertEqual("", self.config.get_config("SettingThatDoesntExist"))

    def test_get_config_badfile(self):
        self.write_bad_file(0)
        try:
            self.config.get_config("SpacesValue")
        except SettingsError:
            pass
        else:
            assert(False)

        self.write_bad_file(1)
        value = self.config.get_config("This")
        self.assertEqual("more=than one equals", value)

    def test_set_config(self):
        self.write_good_file()
        self.config.set_config('new_key', 'new_value')
        self.config.save()
        # re-read the config file
        self.config2 = Configuration(self.config_file_path)
        # Check value.
        self.assertEqual('new_value', self.config2.get_config('new_key'))

    def test_set_config_uppercase(self):
        self.write_good_file()
        self.config.set_config('NewKey', 'new_value')
        self.config.save()
        # re-read the config file
        self.config2 = Configuration(self.config_file_path)
        # Check value.
        self.assertEqual('new_value', self.config2.get_config('newkey'))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
