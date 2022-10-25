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

from parameterized import parameterized

from rdiffweb.core.passwd import check_password, hash_password


class Test(unittest.TestCase):
    @parameterized.expand(
        [
            ('admin123', 'f865b53623b121fd34ee5426c792e5c33af8c227'),
            ('admin123', '{SSHA}/LAr7zGT/Rv/CEsbrEndyh27h+4fLb9h'),
            ('admin123', '$argon2id$v=19$m=102400,t=2,p=8$/mDhOg8wyZeMTUjcbIC7mg$3pxRSfYgUXmKEKNtasP1Og'),
        ]
    )
    def test_check_password(self, password, challenge):
        self.assertTrue(check_password(password, challenge))
        self.assertTrue(check_password(password, hash_password(password)))
        self.assertFalse(check_password('invalid', challenge))
        self.assertFalse(check_password(password, 'invalid'))

    def test_hash_password(self):
        self.assertTrue(hash_password('admin12').startswith('$argon2id$'))
