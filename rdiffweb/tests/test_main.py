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


import contextlib
import io
import unittest
from unittest.mock import patch

import pkg_resources

from rdiffweb.main import main


@patch('cherrypy.quickstart')
class Test(unittest.TestCase):
    def test_main_with_config(self, *args):
        config = pkg_resources.resource_filename('rdiffweb.tests', 'rdw.conf')  # @UndefinedVariable
        main(['-f', config])

    def test_main_without_config(self, *args):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            main([])

    def test_main_help(self, *args):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            with self.assertRaises(SystemExit):
                main(['--help'])
        self.assertTrue(f.getvalue().startswith('usage: rdiffweb'), msg='%s is not a help message' % f.getvalue())

    def test_main_version(self, *args):
        f = io.StringIO()
        with contextlib.redirect_stdout(f):
            with self.assertRaises(SystemExit):
                main(['--version'])
        self.assertRegex(f.getvalue(), r'rdiffweb (DEV|[0-9].*)')
