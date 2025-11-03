# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import os

from parameterized import parameterized

import rdiffweb.test


class AdminWithNoLogsTest(rdiffweb.test.WebCase):
    login = True

    def test_logs(self):
        # Given an application without log configuration
        # When getting the systemlog page
        self.getPage("/admin/logs/")
        # Then the page is displayed
        self.assertStatus(200)
        self.assertInBody('No log file available')


class AdminWithLogMissingTest(rdiffweb.test.WebCase):
    login = True
    default_config = {'log-file': './rdiffweb.log', 'log-access-file': './rdiffweb-access.log'}

    def test_logs_with_no_file(self):
        # Given an application with miss-configured logs.
        # When getting the systemlog page
        self.getPage("/admin/logs/")
        # Then the page return without error
        self.assertStatus(200)
        self.assertInBody('No log file selected')

    @parameterized.expand(
        [
            ('log_file',),
            ('log_access_file',),
        ]
    )
    def test_logs(self, name):
        # Given an application with miss-configured logs.
        # When getting the systemlog page
        self.getPage("/admin/logs/?name=%s" % name)
        # Then the page return without error
        self.assertStatus(200)
        self.assertInBody('Log file empty')

    @parameterized.expand(
        [
            ('log_file',),
            ('log_access_file',),
        ]
    )
    def test_raw(self, name):
        # When getting raw file
        self.getPage("/admin/logs/raw?name=%s" % name)
        # Then not found is returned
        self.assertStatus(404)


class AdminWithLogsTest(rdiffweb.test.WebCase):
    login = True
    default_config = {'log-file': '/tmp/rdiffweb.log', 'log-access-file': '/tmp/rdiffweb-access.log'}

    def setUp(self):
        super().setUp()
        with open('/tmp/rdiffweb.log', 'w') as f:
            f.write("FOO")
        with open('/tmp/rdiffweb-access.log', 'w') as f:
            f.write("BAR")

    def tearDown(self):
        super().tearDown()
        try:
            os.remove('/tmp/rdiffweb.log')
            os.remove('/tmp/rdiffweb-access.log')
        except Exception:
            pass

    def test_get_logs(self):
        # Given an application with log file
        # When getting the system log page
        self.getPage("/admin/logs/")
        self.assertInBody('No log file selected')
        # Then the page return without error
        self.assertStatus(200)
        # Then page include link to both log file.
        self.assertInBody('http://127.0.0.1:%s/admin/logs?limit=2000&amp;name=log_file"' % self.PORT)
        self.assertInBody('http://127.0.0.1:%s/admin/logs?limit=2000&amp;name=log_access_file"' % self.PORT)

    @parameterized.expand(
        [
            ('log_file', 'FOO'),
            ('log_access_file', 'BAR'),
        ]
    )
    def test_raw(self, name, expected_data):
        # When getting raw file
        self.getPage("/admin/logs/raw?name=%s" % name)
        # Then it contains logs data.
        self.assertInBody(expected_data)

    def test_raw_invalid(self):
        # When getting raw file
        self.getPage("/admin/logs/raw?name=invalid")
        # Then not found is returned
        self.assertStatus(404)
