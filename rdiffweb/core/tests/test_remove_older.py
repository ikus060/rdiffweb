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
Created on May 2, 2016

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""
from unittest.mock import MagicMock

import cherrypy

import rdiffweb.core.remove_older
import rdiffweb.test
from rdiffweb.core.librdiff import RdiffTime


class RemoveOlderTest(rdiffweb.test.WebCase):
    def test_remove_older_job_without_keepdays(self):
        # Given a store with repos with keepdays equals to 0 (forever)
        repo = MagicMock()
        repo.keepdays = 0
        repo.last_backup_date = RdiffTime('2014-11-02T17:23:41-05:00')
        self.app.store.repos = MagicMock()
        self.app.store.repos.return_value = [repo]
        # When the job is running.
        cherrypy.remove_older.remove_older_job()
        # Then remove_older function is not called.
        self.app.store.repos.assert_called()
        repo.remove_older.assert_not_called()

    def test_remove_older_job_with_keepdays(self):
        # Given a store with repos with keepdays equals to 30
        repo = MagicMock()
        repo.keepdays = 30
        repo.last_backup_date = RdiffTime('2014-11-02T17:23:41-05:00')
        self.app.store.repos = MagicMock()
        self.app.store.repos.return_value = [repo]
        # When the job is running.
        cherrypy.remove_older.remove_older_job()
        # Then remove_older function get called on the repo.
        self.app.store.repos.assert_called()
        repo.remove_older.assert_called()
