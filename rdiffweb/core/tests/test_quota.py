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
Created on Dec 10, 2020

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

from unittest import mock
from unittest.mock import MagicMock

import cherrypy

from rdiffweb import test
from rdiffweb.core.model import UserObject


class QuotaPluginTest(test.WebCase):

    default_config = {
        'quota-get-cmd': 'echo 123456',
        'quota-used-cmd': 'echo 21474836',
        'quota-set-cmd': 'echo $RDIFFWEB_QUOTA',
    }

    def test_get_disk_usage(self):
        # Given a user
        userobj = UserObject.add_user('bob')
        userobj.commit()
        # When querying quota for a userobj
        result = cherrypy.engine.publish('get_disk_usage', userobj)
        # Then quota return a value
        self.assertEqual(21474836, result[0])

    def test_get_disk_quota(self):
        # Given a user
        userobj = UserObject.add_user('bob')
        userobj.commit()
        # When querying quota for a userobj
        result = cherrypy.engine.publish('get_disk_quota', userobj)
        # Then quota return a value
        self.assertEqual(123456, result[0])

    def test_set_disk_quota(self):
        # Given a used cmd
        userobj = UserObject.add_user('bob')
        userobj.commit()
        # When querying quota for a userobj
        results = cherrypy.engine.publish('set_disk_quota', userobj, 98765)
        # Then quota return a value
        self.assertEqual([98765], results)


class QuotaPluginTestWithFailure(test.WebCase):

    default_config = {
        'quota-get-cmd': 'exit 1',
        'quota-used-cmd': 'exit 2',
        'quota-set-cmd': 'exit 3',
    }

    def test_set_disk_quota_with_failure(self):
        # Given a user object
        userobj = UserObject.add_user('bob')
        userobj.commit()
        # When settings the quota
        results = cherrypy.engine.publish('set_disk_quota', userobj, 98765)
        # Then False is returned
        self.assertEqual([False], results)


class QuotaPluginTestWithUndefinedCmd(test.WebCase):
    def test_get_disk_usage_unsupported(self):
        # Given a user object with a valid user_root
        userobj = UserObject.get_user(self.USERNAME)
        # When getting disk usage
        results = cherrypy.engine.publish('get_disk_usage', userobj)
        # Then default disk usage is return
        self.assertEqual([mock.ANY], results)

    def test_get_disk_quota_unsupported(self):
        # Given a user object
        userobj = UserObject.get_user(self.USERNAME)
        # When gettings the quota
        results = cherrypy.engine.publish('get_disk_quota', userobj)
        # Then default disk usage is return
        self.assertEqual([mock.ANY], results)

    def test_set_disk_quota_unsupported(self):
        # Given a user object
        userobj = UserObject.get_user(self.USERNAME)
        # When settings the quota
        results = cherrypy.engine.publish('set_disk_quota', userobj, 98765)
        # Then no response is returned
        self.assertEqual([], results)

    def test_get_disk_usage_with_empty_user_root(self):
        # Given a user with an empty user_root.
        userobj = UserObject.add_user('bob')
        userobj.user_root = ''
        userobj.commit()
        # When getting disk usage
        results = cherrypy.engine.publish('get_disk_usage', userobj)
        # Then default disk usage is return
        self.assertEqual([0], results)

    def test_get_disk_usage_with_invalid_user_root(self):
        # Given a user with an invalid user_root.
        userobj = UserObject.add_user('bob')
        userobj.user_root = 'invalid'
        userobj.commit()
        # When getting disk usage
        results = cherrypy.engine.publish('get_disk_usage', userobj)
        # Then default disk usage is return
        self.assertEqual([0], results)


class UserObjectQuotaTest(test.WebCase):
    def setUp(self):
        self.listener = MagicMock()
        cherrypy.engine.subscribe("set_disk_quota", self.listener.set_disk_quota, priority=40)
        cherrypy.engine.subscribe("get_disk_quota", self.listener.get_disk_quota, priority=40)
        cherrypy.engine.subscribe("get_disk_usage", self.listener.get_disk_usage, priority=40)
        return super().setUp()

    def tearDown(self):
        cherrypy.engine.unsubscribe("set_disk_quota", self.listener.set_disk_quota)
        cherrypy.engine.unsubscribe("get_disk_quota", self.listener.get_disk_quota)
        cherrypy.engine.unsubscribe("get_disk_usage", self.listener.get_disk_usage)
        return super().tearDown()

    def test_get_disk_usage(self):
        # Given a mock quota
        self.listener.get_disk_usage.return_value = 12345
        # Given a user object
        userobj = UserObject.get_user(self.USERNAME)
        # When getting disk usage
        value = userobj.disk_usage
        # Then disk usage value is return
        self.assertEqual(12345, value)
        # Then listener was called
        self.listener.get_disk_usage.assert_called_once_with(userobj)

    def test_get_disk_quota(self):
        # Given a mock quota
        self.listener.get_disk_quota.return_value = 23456
        # Given a user object
        userobj = UserObject.get_user(self.USERNAME)
        # When getting disk quota
        value = userobj.disk_quota
        # Then disk quota value is return
        self.assertEqual(23456, value)
        # Then listener was called
        self.listener.get_disk_quota.assert_called_once_with(userobj)

    def test_set_disk_quota(self):
        # Given a user object
        userobj = UserObject.get_user(self.USERNAME)
        # When setting disk quota
        userobj.disk_quota = 345678
        # Then listener was called
        self.listener.set_disk_quota.assert_called_once_with(userobj, 345678)
