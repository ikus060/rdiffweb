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
'''
Created on Apr. 10, 2020

@author: Patrik Dufresne
'''

import unittest

from rdiffweb.core.passwd import check_password, hash_password


class Test(unittest.TestCase):
    def test_check_password(self):
        self.assertTrue(check_password('admin123', 'f865b53623b121fd34ee5426c792e5c33af8c227'))
        self.assertTrue(check_password('admin123', '{SSHA}/LAr7zGT/Rv/CEsbrEndyh27h+4fLb9h'))
        self.assertFalse(check_password('admin12', 'f865b53623b121fd34ee5426c792e5c33af8c227'))
        self.assertFalse(check_password('admin12', '{SSHA}/LAr7zGT/Rv/CEsbrEndyh27h+4fLb9h'))
        self.assertTrue(hash_password('admin12').startswith('{SSHA}'))
        self.assertTrue(check_password('admin12', hash_password('admin12')))
        self.assertTrue(check_password('admin123', hash_password('admin123')))
