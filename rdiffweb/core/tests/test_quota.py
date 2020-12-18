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

from rdiffweb.core.quota import IUserQuota, QuotaUnsupported, QuotaException
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
        userobj = self.app.store.get_user(self.USERNAME)
        self.quota.get_disk_usage = MagicMock(return_value=3)
        disk_usage = userobj.disk_usage
        self.assertEqual(3, disk_usage)


class DefaultQuotaTest(AppTestCase):

    reset_testcases = True

    REPO = 'testcases/'

    USERNAME = 'admin'

    PASSWORD = 'admin123'

    def test_get_disk_quota(self):
        """
        Just make a call to the function.
        """
        # Get quota
        userobj = self.app.store.get_user(self.USERNAME)
        self.assertIsInstance(userobj.disk_quota, int)

    def test_disk_usage(self):
        """
        Just make a call to the function.
        """
        userobj = self.app.store.get_user(self.USERNAME)
        disk_usage = userobj.disk_usage
        self.assertIsInstance(disk_usage, int)

    def test_get_disk_usage(self):
        """
        Check if value is available.
        """
        # Mock command line
        self.app.quota._get_usage_cmd = "echo 21474836"

        # Make sure an exception is raised.
        userobj = self.app.store.add_user('bob')
        self.assertEquals(21474836, self.app.quota.get_disk_usage(userobj))

    def test_set_disk_quota(self):
        # Mock command
        self.app.quota._set_quota_cmd = "echo ok"

        userobj = self.app.store.add_user('bob')
        self.app.quota.set_disk_quota(userobj, quota=1234567)

    def test_set_disk_quota_unsupported(self):
        # Mock empty command
        self.app.quota._get_usage_cmd = ""
        # Create user
        userobj = self.app.store.add_user('bob')
        # expect exception
        with self.assertRaises(QuotaUnsupported):
            self.app.quota.set_disk_quota(userobj, quota=1234567)

    def test_update_userquota_401(self):
        userobj = self.app.store.add_user('bob')
        # Mock co mmand
        self.app.quota._set_quota_cmd = "exit 3"
        # Make sure an exception is raised.
        with self.assertRaises(QuotaException):
            self.app.quota.set_disk_quota(userobj, quota=1234567)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
