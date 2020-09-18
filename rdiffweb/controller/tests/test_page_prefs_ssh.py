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

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""


import logging
import unittest

from rdiffweb.test import WebCase


class SSHKeysTest(WebCase):

    PREFS_SSHKEYS = "/prefs/sshkeys/"

    login = True

    reset_app = True

    # Enable testcases to define a user_root
    reset_testcases = True

    def _delete_ssh_key(self, fingerprint):
        b = {'action': 'delete',
             'fingerprint': fingerprint}
        self.getPage(self.PREFS_SSHKEYS, method='POST', body=b)

    def _add_ssh_key(self, title, key):
        b = {'action': 'add',
             'title': title,
             'key': key}
        self.getPage(self.PREFS_SSHKEYS, method='POST', body=b)

    def test_page(self):
        self.getPage(self.PREFS_SSHKEYS)
        self.assertStatus('200 OK')

    def test_add(self):
        # Delete existing keys
        user = self.app.store.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEquals(0, len(list(user.authorizedkeys)))
        
        # Add a new key
        self._add_ssh_key("test@mysshkey", "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530")
        self.assertStatus('200 OK')
        self.assertEquals(1, len(list(user.authorizedkeys)))
        
        # Show page
        self.getPage(self.PREFS_SSHKEYS)
        self.assertInBody("test@mysshkey")
        self.assertInBody("4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91")

    def test_add_duplicate(self):
        # Delete existing keys
        user = self.app.store.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEquals(0, len(list(user.authorizedkeys)))
        
        # Add a new key
        self._add_ssh_key("test@mysshkey", "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530")
        self.assertStatus('200 OK')
        self.assertNotInBody("Duplicate key.")
        self.assertEquals(1, len(list(user.authorizedkeys)))
        
        # Add a new key
        self._add_ssh_key("test@mysshkey", "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530")
        self.assertStatus('200 OK')
        self.assertInBody("Duplicate key.")
        self.assertEquals(1, len(list(user.authorizedkeys)))

    def test_add_invalid(self):
        # Delete existing keys
        user = self.app.store.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
            
        # Add key
        self._add_ssh_key("test@mysshkey", "lkjasdfoiuwerlk")
        self.assertInBody("Invalid SSH key.")
        self.assertEquals(0, len(list(user.authorizedkeys)))

    def test_delete(self):
        # Delete existing keys
        user = self.app.store.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEquals(0, len(list(user.authorizedkeys)))
        
        # Add a new key
        self._add_ssh_key("test@mysshkey", "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530")
        self.assertStatus('200 OK')
        self.assertEquals(1, len(list(user.authorizedkeys)))
        
        # Delete Key
        self._delete_ssh_key("4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91")
        self.assertStatus('200 OK')
        self.assertEquals(0, len(list(user.authorizedkeys)))

    def test_delete_invalid(self):
        # Delete existing keys
        user = self.app.store.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEquals(0, len(list(user.authorizedkeys)))
        
        # Add a new key
        self._add_ssh_key("test@mysshkey", "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530")
        self.assertStatus('200 OK')
        self.assertEquals(1, len(list(user.authorizedkeys)))
        
        # Delete Key
        self._delete_ssh_key("invalid")
        self.assertStatus('200 OK')
        self.assertEquals(1, len(list(user.authorizedkeys)))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
