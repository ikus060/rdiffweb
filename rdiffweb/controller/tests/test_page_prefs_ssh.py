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

from base64 import b64encode

import rdiffweb.test
from rdiffweb.core.model import UserObject

PREFS_SSHKEYS = "/prefs/sshkeys"


class PagePrefSshKeysTest(rdiffweb.test.WebCase):

    login = True

    def _delete_ssh_key(self, fingerprint):
        b = {'action': 'delete', 'fingerprint': fingerprint}
        self.getPage(PREFS_SSHKEYS, method='POST', body=b)

    def _add_ssh_key(self, title, key):
        b = {'action': 'add', 'title': title, 'key': key}
        self.getPage(PREFS_SSHKEYS, method='POST', body=b)

    def test_page(self):
        self.getPage(PREFS_SSHKEYS)
        self.assertStatus('200 OK')

    def test_add(self):
        # Delete existing keys
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEqual(0, len(list(user.authorizedkeys)))

        # Add a new key
        self._add_ssh_key(
            "test@mysshkey",
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
        )
        self.assertStatus('200 OK')
        self.assertEqual(1, len(list(user.authorizedkeys)))

        # Show page
        self.getPage(PREFS_SSHKEYS)
        self.assertInBody("test@mysshkey")
        self.assertInBody("4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91")

    def test_add_duplicate(self):
        # Delete existing keys
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        user.commit()
        self.assertEqual(0, len(list(user.authorizedkeys)))

        # Add a new key
        self._add_ssh_key(
            "test@mysshkey",
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
        )
        self.assertStatus('200 OK')
        self.assertNotInBody("Duplicate key.")
        self.assertEqual(1, len(list(user.authorizedkeys)))

        # Add a duplicate key
        self._add_ssh_key(
            "test@mysshkey",
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
        )
        self.assertStatus('200 OK')
        self.assertInBody("Duplicate key.")
        self.assertEqual(1, len(list(user.authorizedkeys)))

    def test_add_invalid(self):
        # Delete existing keys
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)

        # Add key
        self._add_ssh_key("test@mysshkey", "lkjasdfoiuwerlk")
        self.assertStatus(200)
        self.assertInBody("Invalid SSH key.")
        self.assertEqual(0, len(list(user.authorizedkeys)))

    def test_add_get_method(self):
        # Given an authenticated user
        user = UserObject.get_user('admin')
        # When querying a page with parameters (HTTP GET)
        self.getPage(
            "/prefs/sshkeys?action=add&title=ssh1&key=ssh-rsa+AAAAB3NzaC1yc2EAAAADAQABAAAAgQCzurRNVKwb0ZJCmUgGenoe4vth5gnHxgnzjHSUO8r7IZiouB6DAciiVUAryV6MQm5trwIXNo0QDwFxyX99exIwUlDu3OzhZHKKbb721hCID17AWZMAQIgxQdu6b27s5YgJXsaxXWvEO2lSRVOnVXoCSI7mK5St%2FCJ8O1OdXivNIQ%3D%3D+noname%0D%0A"
        )
        # Then page return without error
        self.assertStatus(200)
        # Then ssh key is not added
        self.assertEqual(0, len(list(user.authorizedkeys)))

    def test_add_with_title_too_long(self):
        # Given an authenticated user without any ssh keys
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEqual(0, len(list(user.authorizedkeys)))
        # When adding a key with title too long.
        self._add_ssh_key(
            "title" * 52,
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
        )
        # Then page return with error
        self.assertStatus('200 OK')
        self.assertInBody('Title too long.')
        # Then key is not added
        self.assertEqual(0, len(list(user.authorizedkeys)))

    def test_delete(self):
        # Delete existing keys
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEqual(0, len(list(user.authorizedkeys)))

        # Add a new key
        self._add_ssh_key(
            "test@mysshkey",
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
        )
        self.assertStatus('200 OK')
        self.assertEqual(1, len(list(user.authorizedkeys)))

        # Delete Key
        self._delete_ssh_key("4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91")
        self.assertStatus('200 OK')
        self.assertEqual(0, len(list(user.authorizedkeys)))

    def test_delete_invalid(self):
        # Delete existing keys
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEqual(0, len(list(user.authorizedkeys)))

        # Add a new key
        self._add_ssh_key(
            "test@mysshkey",
            "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
        )
        self.assertStatus('200 OK')
        self.assertEqual(1, len(list(user.authorizedkeys)))

        # Delete Key
        self._delete_ssh_key("invalid")
        self.assertStatus('200 OK')
        self.assertEqual(1, len(list(user.authorizedkeys)))


class ApiSshKeysTest(rdiffweb.test.WebCase):

    headers = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]

    def test_post(self):
        # Given a user without ssh keys
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEqual(0, len(list(user.authorizedkeys)))

        # When POST a valid ssh key
        self.getPage(
            '/api/currentuser/sshkeys',
            headers=self.headers,
            method='POST',
            body={
                'title': "test@mysshkey",
                'key': "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
            },
        )
        # Then page return success
        self.assertStatus(200)
        # Then key get added to the user
        self.assertEqual(1, len(list(user.authorizedkeys)))

    def test_post_duplicate(self):
        # Given a user with an existing SSH Keys
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        self.assertEqual(0, len(list(user.authorizedkeys)))
        user.add_authorizedkey(
            key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
            comment="test@mysshkey",
        )
        user.commit()

        # When POST a duplicate ssh key
        self.getPage(
            '/api/currentuser/sshkeys',
            headers=self.headers,
            method='POST',
            body={
                'title': "test@mysshkey",
                'key': "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
            },
        )
        # Then page return success
        self.assertStatus(400)
        # Then key get added to the user
        self.assertEqual(1, len(list(user.authorizedkeys)))

    def test_delete(self):
        # Given a user with an existing ssh key
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        user.add_authorizedkey(
            key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
            comment="test@mysshkey",
        )
        user.commit()
        self.assertEqual(1, len(list(user.authorizedkeys)))
        # When deleting the ssh key
        self.getPage(
            '/api/currentuser/sshkeys/4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91',
            headers=self.headers,
            method='DELETE',
        )
        # Then page return with success
        self.assertStatus('200 OK')

        # Then key get deleted from database
        self.assertEqual(0, len(list(user.authorizedkeys)))

    def test_get(self):
        # Given a user with an existing ssh key
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        user.add_authorizedkey(
            key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
            comment="test@mysshkey",
        )
        user.commit()
        self.assertEqual(1, len(list(user.authorizedkeys)))
        # When deleting the ssh key
        data = self.getJson(
            '/api/currentuser/sshkeys/4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91',
            headers=self.headers,
            method='GET',
        )
        # Then page return with success with sshkey
        self.assertStatus('200 OK')
        self.assertEqual(
            data, {'title': "test@mysshkey", 'fingerprint': '4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91'}
        )

    def test_get_invalid(self):
        # Given a user with an existing ssh key
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        user.add_authorizedkey(
            key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
            comment="test@mysshkey",
        )
        user.commit()
        self.assertEqual(1, len(list(user.authorizedkeys)))
        # When deleting the ssh key
        self.getPage(
            '/api/currentuser/sshkeys/invalid',
            headers=self.headers,
            method='GET',
        )
        # Then page return with success with sshkey
        self.assertStatus(404)

    def test_list(self):
        # Given a user with an existing ssh key
        user = UserObject.get_user('admin')
        for key in user.authorizedkeys:
            user.delete_authorizedkey(key.fingerprint)
        user.add_authorizedkey(
            key="ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDSEN5VTn9MLituZvdYTZMbZEaMxe0UuU7BelxHkvxzSpVWtazrIBEc3KZjtVoK9F3+0kd26P4DzSQuPUl3yZDgyZZeXrF6p2GlEA7A3tPuOEsAQ9c0oTiDYktq5/Go8vD+XAZKLd//qmCWW1Jg4datkWchMKJzbHUgBrBH015FDbGvGDWYTfVyb8I9H+LQ0GmbTHsuTu63DhPODncMtWPuS9be/flb4EEojMIx5Vce0SNO9Eih38W7jTvNWxZb75k5yfPJxBULRnS5v/fPnDVVtD3JSGybSwKoMdsMX5iImAeNhqnvd8gBu1f0IycUQexTbJXk1rPiRcF13SjKrfXz ikus060@ikus060-t530",
            comment="test@mysshkey",
        )
        user.commit()
        self.assertEqual(1, len(list(user.authorizedkeys)))
        # When deleting the ssh key
        data = self.getJson(
            '/api/currentuser/sshkeys',
            headers=self.headers,
            method='GET',
        )
        # Then page return with success with sshkey
        self.assertStatus('200 OK')
        self.assertEqual(
            data, [{'title': "test@mysshkey", 'fingerprint': '4d:42:8b:35:e5:55:71:f7:b3:0d:58:f9:b1:2c:9e:91'}]
        )


class PagePrefSshKeysWithSSHKeyDisabled(rdiffweb.test.WebCase):

    login = True

    default_config = {
        "disable_ssh_keys": "true",
    }

    def test_get_page(self):
        # When making a query to preferences
        self.getPage("/prefs/sshkeys", method='GET')
        # Then the page should return with success but without SSH
        self.assertStatus(200)
        self.assertInBody("SSH Keys management is disabled by your administrator.")
