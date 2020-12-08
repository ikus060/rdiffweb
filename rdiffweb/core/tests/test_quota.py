# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2020 rdiffweb contributors
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
Created on Dec 10, 2020

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import unittest
from unittest.mock import MagicMock

from rdiffweb.core.quota import IUserQuota
from rdiffweb.test import AppTestCase


class QuotaTest(AppTestCase):

    reset_testcases = True

    REPO = 'testcases/'

    USERNAME = 'admin'

    PASSWORD = 'admin123'

    def setUp(self):
        AppTestCase.setUp(self)
        self.quota = IUserQuota()
        self.quota.get_disk_usage = MagicMock()
        self.quota.get_disk_quota = MagicMock()
        self.quota.set_disk_quota = MagicMock()
        self.app.quota = self.quota

    def test_get_set_disk_quota(self):
        """
        Just make a call to the function.
        """
        # Get quota
        self.quota.get_disk_quota = MagicMock(return_value=1234)
        userobj = self.app.store.get_user(self.USERNAME)
        self.assertEqual(1234, userobj.disk_quota)
        # Set Quota
        userobj.disk_quota = 4567
        self.quota.set_disk_quota.assert_called_with(userobj, 4567)

    def test_disk_usage(self):
        """
        Just make a call to the function.
        """
        self.quota.get_disk_usage = MagicMock(return_value={'avail':1, 'used':2, 'size':3})
        userobj = self.app.store.get_user(self.USERNAME)
        disk_usage = userobj.disk_usage
        self.assertEqual(1, disk_usage['avail'])
        self.assertEqual(2, disk_usage['used'])
        self.assertEqual(3, disk_usage['size'])


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
