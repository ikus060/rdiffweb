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
Created on May 11, 2015

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import os
import shutil
import tempfile
import unittest
from io import open

import pkg_resources

from rdiffweb.core import authorizedkeys


class AuthorizedKeysTest(unittest.TestCase):
    """
    Test AuthorizedKeys class.
    """

    def test_add(self):

        # Create a key
        key = authorizedkeys.AuthorizedKey(options=False, keytype='ssh-rsa', key='AAAAA', comment='bobo@computer')

        # Copy file
        tempfilename = tempfile.mktemp()
        filename = pkg_resources.resource_filename(__name__, 'test_authorized_keys')  # @UndefinedVariable
        shutil.copyfile(filename, tempfilename)

        try:
            # Remove key from file
            authorizedkeys.add(tempfilename, key)

            # Read the file again.
            keys = list(authorizedkeys.read(tempfilename))
            self.assertEqual(6, len(keys))

            # Check data
            self.assertEqual('ssh-rsa', keys[5].keytype)
            self.assertEqual('AAAAA', keys[5].key)
            self.assertEqual('bobo@computer', keys[5].comment)
        finally:
            os.remove(tempfilename)

    def test_check_publickey_with_rsa(self):
        filename = pkg_resources.resource_filename(__name__, 'test_publickey_ssh_rsa.pub')  # @UndefinedVariable
        f = open(filename, 'r', encoding='utf8')
        line = f.readline()
        f.close()
        # Check line.
        key = authorizedkeys.check_publickey(line)
        self.assertEqual('ssh-rsa', key.keytype)
        self.assertEqual(372, len(key.key))
        self.assertTrue(key.key.startswith('AAAAB3NzaC1yc2EAAAADAQABAAABAQDDY'))
        self.assertEqual('ikus060@ikus060-t530', key.comment)
        self.assertEqual('3c:99:ed:a7:82:a8:71:09:2c:15:3d:78:4a:8c:11:99', key.fingerprint)

    def test_check_publickey_with_dsa(self):
        filename = pkg_resources.resource_filename(__name__, 'test_publickey_ssh_dsa.pub')  # @UndefinedVariable
        f = open(filename, 'r', encoding='utf8')
        line = f.readline()
        f.close()
        # Check line.
        key = authorizedkeys.check_publickey(line)
        self.assertEqual('ssh-dss', key.keytype)
        self.assertEqual(580, len(key.key))
        self.assertTrue(key.key.startswith('AAAAB3NzaC1kc3MAAACBAM8gRuUD+MFPy'))
        self.assertEqual('ikus060@ikus060-t530', key.comment)
        self.assertEqual('2b:28:92:b5:75:85:42:35:99:5d:bf:a5:f1:fb:a6:71', key.fingerprint)

    def test_check_publickey_with_invalid(self):
        with self.assertRaises(ValueError):
            authorizedkeys.check_publickey('123445342')

    def test_exists(self):
        filename = pkg_resources.resource_filename(__name__, 'test_authorized_keys')  # @UndefinedVariable
        # Check if key exists.
        key = authorizedkeys.AuthorizedKey(
            options=False, keytype='ssh-rsa', key='AAAAB3NzaC1yc2EAAAADAQABAAUGK', comment='bobo@computer'
        )
        self.assertTrue(authorizedkeys.exists(filename, key))
        # Check with different type.
        key = authorizedkeys.AuthorizedKey(
            options=False, keytype='ssh-dss', key='AAAAB3NzaC1yc2EAAAADAQABAAUGK', comment='bobo@computer'
        )
        self.assertFalse(authorizedkeys.exists(filename, key))

    def test_unicode(self):
        options = 'command="bash",no-user-rc'
        key = authorizedkeys.AuthorizedKey(options=options, keytype='ssh-rsa', key='AAAAA', comment='bobo@computer')
        line = key.getvalue()
        self.assertEqual('command="bash",no-user-rc ssh-rsa AAAAA bobo@computer', line)
        self.assertIsInstance(line, str)

    def test_str(self):
        options = 'command="bash",no-user-rc'
        key = authorizedkeys.AuthorizedKey(options=options, keytype='ssh-rsa', key='AAAAA', comment='bobo@computer')
        line = key.getvalue()
        self.assertEqual('command="bash",no-user-rc ssh-rsa AAAAA bobo@computer', line)
        self.assertIsInstance(line, str)

    def test_parse_options(self):
        self.assertEqual({'key': 'value'}, authorizedkeys._parse_options('key="value"'))
        self.assertEqual({'option': False}, authorizedkeys._parse_options('option'))
        self.assertEqual(
            {'option1': False, 'key': 'value', 'option2': False},
            authorizedkeys._parse_options('option1,key="value",option2'),
        )

    def test_read(self):
        filename = pkg_resources.resource_filename(__name__, 'test_authorized_keys')  # @UndefinedVariable
        keys = list(authorizedkeys.read(filename))
        self.assertEqual(5, len(list(keys)))

        # Check first key
        self.assertEqual('ssh-rsa', keys[0].keytype)
        self.assertTrue(keys[0].key.startswith('AAAAB3NzaC1yc2EAAAADAQABAAABAQDFqrQ'))
        self.assertEqual('root@thymara', keys[0].comment)

        # Check second key
        self.assertEqual('ssh-rsa', keys[1].keytype)
        self.assertTrue(keys[1].key.startswith('AAAAB3NzaC1yc2EAAAADAQABAAABAQDf'))
        self.assertEqual('root@mercor', keys[1].comment)
        self.assertEqual({'command': 'mycommand arg'}, keys[1].options)

        # Check thrid key
        self.assertEqual('ssh-rsa', keys[2].keytype)
        self.assertTrue(keys[2].key.startswith('AAAAB3NzaC1yc2EAAAADAQABAAUGK'))
        self.assertEqual('root@kalo', keys[2].comment)
        self.assertEqual({'no-user-rc': False}, keys[2].options)

        # Check fourth key
        self.assertEqual('ssh-rsa', keys[3].keytype)
        self.assertEqual('AAAAB3NzaC1yc2EAAAADAQSTlX', keys[3].key)
        self.assertEqual('root@ranculos', keys[3].comment)
        self.assertEqual({'command': 'mycommand arg'}, keys[3].options)

        # Check fifth key
        self.assertEqual('ssh-rsa', keys[4].keytype)
        self.assertEqual('AAAAB3NzaC1yc2EAAAADAQABAAUGK', keys[4].key)
        self.assertEqual('', keys[4].comment)
        self.assertEqual({'tunnel': 'n', 'no-X11-forwarding': False}, keys[4].options)

    def test_remove(self):
        # Copy file
        tempfilename = tempfile.mktemp()
        filename = pkg_resources.resource_filename(__name__, 'test_authorized_keys')  # @UndefinedVariable
        shutil.copyfile(filename, tempfilename)

        try:
            # Remove key from file
            authorizedkeys.remove(tempfilename, '7b:25:d6:13:a2:c2:ae:c3:cd:5e:c6:b4:e9:78:9b:00')

            # Read the file again.
            keys = list(authorizedkeys.read(tempfilename))
            self.assertEqual(4, len(keys))

            # Check data
            self.assertEqual('root@mercor', keys[0].comment)
            self.assertEqual('root@kalo', keys[1].comment)
        finally:
            os.remove(tempfilename)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
