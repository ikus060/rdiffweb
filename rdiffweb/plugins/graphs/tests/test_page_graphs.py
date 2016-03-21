#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

@author: ikus060
"""
from __future__ import unicode_literals

import logging
import unittest

from rdiffweb.test import WebCase


class SettingsTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    @classmethod
    def setup_server(cls):
        WebCase.setup_server(enabled_plugins=['SQLite', 'Graphs'])

    def _stats(self, repo):
        return self.getPage("/graphs/data/" + repo + "/")

    def test_stats(self):
        self._stats(self.REPO)
        self.assertStatus('200 OK')
        # Check header
        expected = b"""date,starttime,endtime,elapsedtime,sourcefiles,sourcefilesize,mirrorfiles,mirrorfilesize,newfiles,newfilesize,deletedfiles,deletedfilesize,changedfiles,changedsourcesize,changedmirrorsize,incrementfiles,incrementfilesize,totaldestinationsizechange,errors
1414871387,1414871387.0,1414871388.07,1.07,10,0,1,0,9,0,0,0,1,0,0,0,0,0,0
1414871426,1414871426.0,1414871426.65,0.65,10,13,10,0,0,0,0,0,2,13,0,2,73,86,0
1414871448,1414871448.0,1414871448.62,0.62,10,27,10,13,0,0,0,0,3,14,0,3,83,97,0
1414871475,1414871475.0,1414871475.91,0.91,10,67,10,27,0,0,0,0,5,40,0,5,155,195,0
1414871489,1414871489.0,1414871489.74,0.74,5,13,10,67,0,0,5,54,2,0,0,7,371,317,0
1414873822,1414873822.0,1414873783.07,-38.93,8,15001,5,13,3,14988,0,0,1,0,0,4,0,14988,0
1414873850,1414873850.0,1414873811.34,-38.66,8,15147,8,15001,0,0,0,0,2,286,140,2,212,358,0
1414879639,1414879639.0,1414879600.43,-38.57,10,15373,8,15147,2,226,0,0,1,0,0,3,0,226,0
1414887165,1414887165.0,1414887125.38,-39.62,10,15373,10,15373,0,0,0,0,0,0,0,0,0,0,0
1414887491,1414887491.0,1414887451.36,-39.64,12,30221,10,15373,2,14848,0,0,1,0,0,3,0,14848,0
1414889478,1414889478.0,1414889437.8,-40.2,13,30242,12,30221,1,21,0,0,2,0,0,3,0,21,0
1414937803,1414937803.0,1414937764.82,-38.18,14,3666973,13,30242,1,3636731,0,0,1,0,0,2,0,3636731,0
1414939853,1414939853.0,1414939811.91,-41.09,15,3666973,14,3666973,1,0,0,0,1,0,0,2,0,0,0
1414967021,1414967021.0,1414966979.29,-41.71,15,3666973,15,3666973,0,0,0,0,0,0,0,0,0,0,0
1415047607,1415047607.0,1415047561.68,-45.32,15,3666991,15,3666973,0,0,0,0,2,18,0,2,100,118,0
1415059497,1415059497.0,1415059451.25,-45.75,17,3667001,15,3666991,2,10,0,0,1,0,0,3,0,10,0
1415221262,1415221262.0,1415221211.58,-50.42,17,3667001,17,3667001,3,14869,3,14869,14,3652132,3652132,20,3660,3660,0
1415221470,1415221470.0,1415221417.53,-52.47,19,3667010,17,3667001,2,9,0,0,1,0,0,3,0,9,0
1415221495,1415221495.0,1415221442.45,-52.55,19,3667010,19,3667010,0,0,0,0,3,9,9,3,72,72,0
1415221507,1415221507.0,1415221453.86,-53.14,19,3667010,19,3667010,0,0,0,0,3,9,9,3,72,72,0
1453304541,1453304541.0,1453304542.27,1.27,22,3667068,19,3667010,6,14927,3,14869,16,3652141,3652141,25,3724,3782,0
1454448640,1454448640.0,1454448640.93,0.93,25,3667068,22,3667068,6,14869,3,14869,2,0,0,11,2915,2915,0
"""
        self.assertEquals(expected, self.body)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
