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

import logging
import unittest

from rdiffweb.test import WebCase


class SSHKeysTest(WebCase):

    PREFS_SSHKEYS = "/prefs/sshkeys/"

    login = True

    reset_app = True

    # Enable testcases to define a user_root
    reset_testcases = True

    def _delete_ssh_key(self, key):
        b = {'action': 'delete',
             'key': key}
        self.getPage(self.PREFS_SSHKEYS, method='POST', body=b)

    def _add_ssh_key(self, title, key):
        b = {'action': 'add',
             'title': title,
             'key': key}
        self.getPage(self.PREFS_SSHKEYS, method='POST', body=b)

    def _list_ssh_keys(self):
        self.getPage(self.PREFS_SSHKEYS)

    def test_too_small(self):
        # Delete existing keys
        self._list_ssh_keys()
        while self.body.count(b'Delete') > 0:
            self._delete_ssh_key("1")
        # Add key
        self._add_ssh_key("test@mysshkey", "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAAAYQCyJWg3VAcBpOgjtkKGl3QB5mTGsFkoi5T7nx2o8MuXY+jHpXE+SIFap7C4w6uxYlJEQpcu/YaEdj6174ZK+8p8y2/HxQ08izVOA7hQdElX2wh5xP0OsCQDRJwC4Sb3Ny8= ikus060@ikus060-t530")
        self.assertInBody("SSH key is too short")

    def test_invalid(self):
        # Delete existing keys
        self._list_ssh_keys()
        while self.body.count(b'Delete') > 0:
            self._delete_ssh_key("1")
        # Add key
        self._add_ssh_key("test@mysshkey", "lkjasdfoiuwerlk")
        self.assertInBody("Invalid SSH key.")

    def test_add_delete(self):
        # Delete existing keys
        self._list_ssh_keys()
        while self.body.count(b'Delete') > 0:
            self._delete_ssh_key("1")
        # Add a new key
        self._add_ssh_key("test@mysshkey", "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530")
        self._list_ssh_keys()
        self.assertInBody("test@mysshkey")
        self.assertInBody("4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91")
        self._delete_ssh_key("1")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
