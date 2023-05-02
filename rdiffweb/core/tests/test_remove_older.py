# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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
from unittest.mock import MagicMock, patch

import cherrypy

import rdiffweb.core.remove_older
import rdiffweb.test
from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import RepoObject, UserObject


class RemoveOlderTest(rdiffweb.test.WebCase):
    def test_check_schedule(self):
        # Given the application is started
        # Then remove_older job should be schedule
        self.assertEqual(1, len([job for job in cherrypy.scheduler.list_jobs() if job.name == 'remove_older_job']))

    @patch("rdiffweb.core.model.RepoObject.query")
    def test_remove_older_job_without_last_backup_date(self, mock_query):
        # Given a store with repos with last_backup_date undefined
        repo = MagicMock()
        repo.keepdays = 0
        repo.last_backup_date = None
        mock_query.filter.return_value.all.return_value = [repo]
        # When the job is running.
        cherrypy.remove_older.remove_older_job()
        # Then remove_older function is not called.
        mock_query.filter.return_value.all.assert_called()
        repo.remove_older.assert_not_called()

    @patch("rdiffweb.core.model.RepoObject.query")
    def test_remove_older_job_with_keepdays(self, mock_query):
        # Given a store with repos with keepdays equals to 30
        repo = MagicMock()
        repo.keepdays = 30
        repo.last_backup_date = RdiffTime('2014-11-02T17:23:41-05:00')
        mock_query.filter.return_value.all.return_value = [repo]
        # When the job is running.
        cherrypy.remove_older.remove_older_job()
        # Then remove_older function get called on the repo.
        mock_query.filter.return_value.all.assert_called()
        repo.remove_older.assert_called()

    def test_remove_older_without_mock(self):
        # Given two repo with keepdays
        userobj = UserObject.get_user(self.USERNAME)
        repo = RepoObject.get_repo('admin/testcases', userobj)
        repo.keepdays = 1
        repo.commit()
        self.assertEqual(2, RepoObject.query.count())
        self.assertEqual(1, RepoObject.query.filter(RepoObject.keepdays > 0).count())
        # When the job is running.
        cherrypy.remove_older.remove_older_job()
        # Then history get deleted
        repo = RepoObject.get_repo('admin/testcases', userobj)
        self.assertEqual(1, len(repo.backup_dates))
