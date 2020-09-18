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
Created on Nov 16, 2017

@author: Patrik Dufresne
"""


from base64 import b64encode
import logging
from rdiffweb.test import WebCase
import unittest


class APITest(WebCase):

    reset_app = True

    reset_testcases = True
    
    headers = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]

    def test_get_index(self):
        data = self.getJson('/api/', headers=self.headers)
        self.assertIsNotNone(data.get('version'))

    def test_get_currentuser(self):
        data = self.getJson('/api/currentuser/', headers=self.headers)
        self.assertEqual(data.get('username'), 'admin')
        self.assertEqual(data.get('email'), '')
        # This value change on every execution.
        self.assertEqual(1, len(data.get('repos')))
        repo = data.get('repos')[0]
        self.assertEqual(repo.get('keepdays'), -1)
        self.assertEqual(repo.get('last_backup_date'), '2016-02-02T16:30:40-05:00')
        self.assertEqual(repo.get('status'), 'ok')
        self.assertEqual(repo.get('display_name'), 'testcases')
        self.assertEqual(repo.get('encoding'), 'utf-8')
        self.assertEqual(repo.get('name'), 'testcases')
        self.assertEqual(repo.get('maxage'), 0)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
