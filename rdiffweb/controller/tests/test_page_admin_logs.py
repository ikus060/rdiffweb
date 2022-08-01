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

import os

import rdiffweb.test


class AdminWithNoLogsTest(rdiffweb.test.WebCase):

    login = True

    def test_logs(self):
        self.getPage("/admin/logs/")
        self.assertStatus(200)
        self.assertInBody("No log files")


class AdminWithLogsTest(rdiffweb.test.WebCase):

    login = True
    default_config = {'logfile': '/tmp/rdiffweb.log', 'logaccessfile': '/tmp/rdiffweb-access.log'}

    def test_logs(self):
        with open('/tmp/rdiffweb.log', 'w') as f:
            f.write("content of log file")
        with open('/tmp/rdiffweb-access.log', 'w') as f:
            f.write("content of log file")
        try:
            self.getPage("/admin/logs/")
            self.assertStatus(200)
            self.assertInBody("rdiffweb.log")
            self.assertInBody("content of log file")
            self.assertInBody("rdiffweb-access.log")
            self.assertNotInBody("Error getting file content")
        finally:
            os.remove('/tmp/rdiffweb.log')
            os.remove('/tmp/rdiffweb-access.log')


class AdminWithLogMissingTest(rdiffweb.test.WebCase):

    login = True
    default_config = {'logfile': './rdiffweb.log', 'logaccessfile': './rdiffweb-access.log'}

    def test_logs_with_no_file(self):
        self.getPage("/admin/logs/")
        self.assertStatus(200)
        self.assertInBody("rdiffweb.log")
        self.assertInBody("Error getting file content")

    def test_logs_with_invalid_file(self):
        self.getPage("/admin/logs/invalid")
        self.assertStatus(404)
