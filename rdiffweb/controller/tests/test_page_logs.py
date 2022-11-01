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
Created on Apr 26, 2021

@author: Patrik Dufresne
"""

import os

import rdiffweb.test
from rdiffweb.core.model import UserObject
from rdiffweb.core.rdw_templating import url_for


class LogsPageTest(rdiffweb.test.WebCase):

    login = True

    def _log(self, user, repo, limit=None, date=None, file=None, raw=None):
        url = url_for('logs', user, repo, limit=limit, date=date, file=file, raw=raw)
        return self.getPage(url)

    def test_logs(self):
        self._log(self.USERNAME, self.REPO)
        # Check revisions
        self.assertInBody("Backup Log")
        self.assertInBody("Restore Log")
        # Check show more button get displayed
        self.assertInBody("Show more")

    def test_logs_with_date_notfound(self):
        self._log(self.USERNAME, self.REPO, date=1)
        self.assertStatus(404)

    def test_logs_with_date_invalid(self):
        self._log(self.USERNAME, self.REPO, date='invalid')
        self.assertStatus(400)

    def test_logs_with_file_backup(self):
        self._log(self.USERNAME, self.REPO, file='backup.log')
        self.assertStatus(200)

    def test_logs_with_file_backup_missing(self):
        os.unlink(os.path.join(self.testcases, self.REPO, 'rdiff-backup-data', 'backup.log'))
        self._log(self.USERNAME, self.REPO, file='backup.log')
        self.assertStatus(200)
        self.assertInBody("This log file is empty")

    def test_logs_with_file_restore(self):
        self._log(self.USERNAME, self.REPO, file='restore.log')
        self.assertStatus(200)
        self.assertInBody("Starting restore of")

    def test_logs_with_file_restore_missing(self):
        os.unlink(os.path.join(self.testcases, self.REPO, 'rdiff-backup-data', 'restore.log'))
        self._log(self.USERNAME, self.REPO, file='restore.log')
        self.assertStatus(200)
        self.assertInBody("This log file is empty")

    def test_logs_with_date_valid(self):
        self._log(self.USERNAME, self.REPO, date='1454448640')
        self.assertStatus(200)

    def test_logs_with_limit(self):
        self._log(self.USERNAME, self.REPO, limit=50)
        self.assertStatus(200)
        self.assertNotInBody("Show more")

    def test_logs_with_raw(self):
        self._log(self.USERNAME, self.REPO, file='restore.log', raw=1)
        self.assertStatus(200)
        self.assertHeaderItemValue('Content-Type', 'text/plain;charset=utf-8')
        self.assertInBody("Starting restore of")
        self.assertNotInBody("<html")

    def test_logs_does_not_exists(self):
        # Given an invalid repo
        repo = 'invalid'
        # When trying to get logs from it
        self._log(self.USERNAME, repo)
        # Then a 4040 error is return
        self.assertStatus(404)

    def test_browser_with_failed_repo(self):
        # Given a failed repo
        admin = UserObject.get_user('admin')
        admin.user_root = 'invalid'
        admin.commit()
        # When querying the logs
        self._log(self.USERNAME, self.REPO)
        # Then the page is return with an error message
        self.assertStatus(200)
        self.assertInBody('The repository cannot be found or is badly damaged.')
