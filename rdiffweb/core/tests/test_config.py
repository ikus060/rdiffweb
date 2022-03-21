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

import os
import unittest

import configargparse

from rdiffweb.core.config import ConfigFileParser, parse_args


class TestParseArg(unittest.TestCase):
    def test_parse_args(self):
        args = parse_args(['--serverport', '8081'])
        self.assertEqual(args.server_port, 8081)

    def test_welcome_msg(self, *args):
        # Test with old argument without dash (-)
        args = parse_args(['--welcomemsg', 'This is a message'])
        self.assertEqual(args.welcome_msg, {'': 'This is a message'})
        # Test with new argument
        args = parse_args(['--welcome-msg', 'This is a message'])
        self.assertEqual(args.welcome_msg, {'': 'This is a message'})
        # Test with locale value
        args = parse_args(['--welcome-msg', 'default', '--welcome-msg-fr', 'french', '--welcome-msg-ru', 'rusian'])
        self.assertEqual(args.welcome_msg, {'': 'default', 'fr': 'french', 'ru': 'rusian'})
        # Test with config file
        args = parse_args(args=[], config_file_contents='WelcomeMsg=default')
        self.assertEqual(args.welcome_msg, {'': 'default'})
        # Test with config file with locale
        args = parse_args(
            args=[], config_file_contents='WelcomeMsg=default\nWelcomeMsg[fr]=french\nWelcomeMsg[ru]=rusian'
        )
        self.assertEqual(args.welcome_msg, {'': 'default', 'fr': 'french', 'ru': 'rusian'})

    def test_ldap_add_user_default_role_with_default_value(self):
        args = parse_args([])
        self.assertEqual(args.ldap_add_user_default_role, 'user')

    def test_ldap_add_user_default_role_with_valu(self):
        for value in ['user', 'admin', 'maintainer']:
            args = parse_args(['--ldap-add-user-default-role', value])
            self.assertEqual(args.ldap_add_user_default_role, value)

    def test_ldap_add_user_default_role_with_invalid(self):
        with self.assertRaises(SystemExit):
            parse_args(['--ldap-add-user-default-role', 'invalid'])

    def test_ldap_add_user_default_userroot(self):
        args = parse_args(['--ldap-add-user-default-userroot', '/this/is/a/path'])
        self.assertEqual(args.ldap_add_user_default_userroot, '/this/is/a/path')

    def test_enable_ssh_keys_default(self):
        args = parse_args([])
        self.assertEqual(args.disable_ssh_keys, False)

    def test_enable_ssh_keys_with_enable(self):
        args = parse_args(['--disable-ssh-keys'])
        self.assertEqual(args.disable_ssh_keys, True)

    def test_config_file(self):
        args = parse_args([], config_file_contents='disable-ssh-keys=true')
        self.assertEqual(args.disable_ssh_keys, True)
        args = parse_args([], config_file_contents='disable_ssh_keys=true')
        self.assertEqual(args.disable_ssh_keys, True)

    def test_config_file_with_comments(self):
        args = parse_args([], config_file_contents='##########\n# this is a comment\nserver-host=0.0.0.0')
        self.assertEqual(args.server_host, "0.0.0.0")


class TestConfigFileParser(unittest.TestCase):
    """
    Unit tests for the get_config() function
    """

    good_config_text = """ #This=is a comment
SpacesValue=is a setting with spaces
spaces setting=withspaces
CommentInValue=Value#this is a comment
NoValue=#This is a setting with no value
"""
    bad_config_texts = ['This#doesnt have an equals', 'This=more=than one equals']

    config_file_path = "/tmp/rdw_config.conf"

    def write_good_file(self):
        f = open(self.config_file_path, "w")
        f.write(self.good_config_text)
        f.close()
        with open(self.config_file_path) as stream:
            self.config = ConfigFileParser().parse(stream)

    def write_bad_file(self, bad_setting_num):
        self.write_good_file()
        f = open(self.config_file_path, "w")
        f.write(self.bad_config_texts[bad_setting_num])
        f.close()
        with open(self.config_file_path) as stream:
            self.config = ConfigFileParser().parse(stream)

    def tearDown(self):
        if os.access(self.config_file_path, os.F_OK):
            os.remove(self.config_file_path)

    def test_get_config_spaces_in_value(self):
        self.write_good_file()
        self.assertEqual("is a setting with spaces", self.config.get("spacesvalue"))

    def test_get_config_spaces_in_setting(self):
        self.write_good_file()
        self.assertEqual("withspaces", self.config.get("spaces setting"))

    def test_get_config_comment_in_value(self):
        self.write_good_file()
        self.assertEqual("Value", self.config.get("commentinvalue"))

    def test_get_config_emptyvalue(self):
        self.write_good_file()
        self.assertEqual("", self.config.get("novalue"))

    def test_get_config_case_insensitivity(self):
        self.write_good_file()
        self.assertEqual("Value", self.config.get("commentinvalue"))

    def test_get_config_missingsetting(self):
        self.write_good_file()
        self.assertEqual(None, self.config.get("settingthatdoesntexist"))

    def test_get_config_badfile(self):
        with self.assertRaises(configargparse.ConfigFileParserException):
            self.write_bad_file(0)
        self.config.get("spacesvalue")
        self.write_bad_file(1)
        value = self.config.get("this")
        self.assertEqual("more=than one equals", value)
