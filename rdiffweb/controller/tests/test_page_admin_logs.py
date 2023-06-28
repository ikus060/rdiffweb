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

import os
from unittest.mock import ANY

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

    def test_data_json(self):
        # Given an application without log configuration
        # When getting the systemlog page
        self.getPage("/admin/logs/data.json")
        # Then the page is displayed
        self.assertStatus(200)


class AdminWithLogMissingTest(rdiffweb.test.WebCase):
    login = True
    default_config = {'logfile': './rdiffweb.log', 'logaccessfile': './rdiffweb-access.log'}

    def test_logs_with_no_file(self):
        # Given an application with miss-configured logs.
        # When getting the systemlog page
        self.getPage("/admin/logs/")
        # Then te page return without error
        self.assertStatus(200)

    def test_data_json_with_no_file(self):
        # Given an application with miss-configured logs.
        # When getting the systemlog page
        self.getPage("/admin/logs/data.json")
        # Then the page is displayed
        self.assertStatus(200)


class AdminWithLogsTest(rdiffweb.test.WebCase):
    login = True
    default_config = {'logfile': '/tmp/rdiffweb.log', 'logaccessfile': '/tmp/rdiffweb-access.log'}

    def setUp(self):
        super().setUp()
        with open('/tmp/rdiffweb.log', 'w') as f:
            f.write(
                "[2022-11-15 04:58:41,056][INFO   ][112.4.177.132][admin][CP Server Thread-4][activity] adding new user [oro]\n"
            )
        with open('/tmp/rdiffweb-access.log', 'w') as f:
            f.write(
                '10.255.4.46 - - [07/Feb/2023:03:49:06] "GET /login/ HTTP/1.1" 200 4539 "" "check_http/v2.3.1 (monitoring-plugins 2.3.1)"'
            )

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
        # Then the page return without error
        self.assertStatus(200)
        # Then an ajax table is displayed
        self.assertInBody('data-ajax="http://127.0.0.1:%s/admin/logs/data.json"' % self.PORT)

    def test_get_logs_selenium(self):
        # Given a user browsing the system logs.
        with self.selenium() as driver:
            # When getting web page.
            driver.get(self.baseurl + '/admin/logs/')
            # Then the web page contain a datatable
            driver.find_element('css selector', 'table[data-ajax]')
            # Then the web page is loaded without error.
            self.assertFalse(driver.get_log('browser'))
            # Then page contains system logs
            driver.implicitly_wait(10)
            driver.find_element('xpath', "//*[contains(text(), 'adding new user')]")

    def test_data_json(self):
        # Given a database with system logs
        # When getting data.json
        data = self.getJson("/admin/logs/data.json")
        # Then it contains logs data.
        self.assertEqual(2, len(data['data']))

    def test_data_json_with_limit(self):
        # Given a database with system logs
        # When getting data.json
        data = self.getJson("/admin/logs/data.json?limit=1")
        # Then it contains logs data.
        # Will contains 2 logs, because the limit is per log file.
        self.assertEqual(2, len(data['data']))

    def test_data_json_multiline(self):
        # Given a log file with multiline log
        with open('/tmp/rdiffweb.log', 'w') as f:
            f.write(
                "[2022-11-15 04:58:41,056][INFO   ][112.4.177.132][admin][CP Server Thread-4][rdiffweb.test] this is a log line \n"
                "  that is printed\n"
                "  on multiple line\n"
                "[2022-11-15 04:58:41,056][INFO   ][112.4.177.132][admin][CP Server Thread-4][activity] adding new user [oro]\n"
            )
        with open('/tmp/rdiffweb-access.log', 'w') as f:
            f.write("\n")
        # When getting data.json
        data = self.getJson("/admin/logs/data.json")
        # Then it contains a 2 entry.
        # Cannot verify epoch date, as we use local time zone
        self.assertEqual(
            data['data'],
            [
                [
                    'rdiffweb.log',
                    ANY,
                    '112.4.177.132',
                    'admin',
                    'INFO this is a log line\n  that is printed\n  on multiple line',
                    None,
                ],
                [
                    'rdiffweb.log',
                    ANY,
                    '112.4.177.132',
                    'admin',
                    'INFO adding new user [oro]',
                    'activity',
                ],
            ],
        )

    def test_data_json_invalid_pattern(self):
        # Given a log file invalid patterns
        with open('/tmp/rdiffweb.log', 'w') as f:
            f.write(
                "[ ][INFO   ][112.4.177.132][admin][CP Server Thread-4][ invalid\n"
                "[2022-11-15 04:58:41,056][INFO   ][112.4.177.132][admin][CP Server Thread-4][activity] adding new user [oro]\n"
                "[ ][INFO   ][112.4.177.132][admin][CP Server Thread-4 invalid\n"
            )
        with open('/tmp/rdiffweb-access.log', 'w') as f:
            f.write("\n")
        # When getting data.json
        data = self.getJson("/admin/logs/data.json")
        # Then it contains a 1 entry.
        self.assertEqual(
            data['data'],
            [
                [
                    'rdiffweb.log',
                    ANY,
                    '112.4.177.132',
                    'admin',
                    'INFO adding new user [oro]',
                    'activity',
                ],
            ],
        )

    @parameterized.expand(
        [
            ('-1', 400),
            ('0', 400),
            ('1', 200),
            ('5000', 200),
            ('5001', 400),
        ]
    )
    def test_data_json_with_invalid_limit(self, limit, expected_status):
        # Given a database with system logs
        # When getting data.json with a limit value
        self.getPage("/admin/logs/data.json?limit=%s" % limit)
        # Then is return appropriate error code.
        self.assertStatus(expected_status)
