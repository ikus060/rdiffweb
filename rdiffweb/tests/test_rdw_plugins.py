#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 Patrik Dufresne Service Logiciel
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
Created on Jan 29, 2015

@author: Patrik Dufresne
"""

from __future__ import unicode_literals

import datetime
from mock.mock import Mock, MagicMock
import unittest

from rdiffweb import rdw_plugin
from rdiffweb.rdw_config import Configuration
from rdiffweb.rdw_plugin import PluginManager, JobPlugin


class PluginManagerTest(unittest.TestCase):

    def test_get_plugin_infos_with_egg(self):
        """
        Check plugin information.
        """
        # Enable a single plugin.
        config = Configuration()
        config.set_config('SQLiteEnabled', 'true')
        plugins = PluginManager(config)
        infos = plugins.get_plugin_infos()
        # Check result.
        self.assertTrue(len(infos) > 0)
        plugin_info = next((i for i in infos if i.name == 'SQLite'), None)
        self.assertEqual('SQLite', plugin_info.name)
        # self.assertEqual('SQLite', plugin_info.version)
        self.assertEqual('Patrik Dufresne', plugin_info.author)
        self.assertEqual('http://www.patrikdufresne.com/en/rdiffweb/', infos[0].url)
        self.assertEqual(True, plugin_info.enabled)
        self.assertEqual('GPLv3', plugin_info.copyright)


class JobPluginTest(unittest.TestCase):

    def test_get_next_execution_time(self):
        """
        Check JobPLugin execution time.
        """
        p = JobPlugin()
        p.job_execution_time = '2:00'
        t = p._get_next_execution_time()
        self.assertIsInstance(t, datetime.datetime)

    def test_get_next_execution_time_invalid(self):
        """
        Check JobPLugin execution time with invalid value.
        """
        p = JobPlugin()
        p.job_execution_time = '390'
        t1 = p._get_next_execution_time()
        p.job_execution_time = '23:00'
        t2 = p._get_next_execution_time()
        self.assertEqual(t1, t2)

    def test_deamon_run(self):
        """
        Check JobPlugin execution.
        """
        rdw_plugin.time.sleep = MagicMock()
        p = JobPlugin()
        p.job_execution_time = '23:00'
        p.job_run = lambda: "c"
        p.deamon_run()
        assert rdw_plugin.time.sleep.called


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
