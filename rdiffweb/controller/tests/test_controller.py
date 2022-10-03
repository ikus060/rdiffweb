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
Created on Mar 13, 2019

@author: Patrik Dufresne
"""

from parameterized import parameterized

import rdiffweb.test


class ControllerTest(rdiffweb.test.WebCase):

    login = True

    default_config = {'HeaderName': 'MyTest'}

    def test_headername(self):
        """
        Check if the headername is used in the page.
        """
        self.getPage("/")
        self.assertStatus('200 OK')
        self.assertInBody('MyTest')

    def test_theme(self):
        """
        Check if the theme is properly configure.
        """
        self.getPage("/")
        self.assertStatus('200 OK')
        self.assertInBody('/static/default.css')

    @parameterized.expand(
        [
            '/favicon.ico',
            '/static/default.css',
            '/static/js/rdiffweb.js',
            '/static/orange.css',
        ]
    )
    def test_static_files(self, path):
        """
        Check if the theme is properly configure.
        """
        self.getPage('/logout')
        self.getPage(path)
        self.assertStatus(200)

    def test_path_traversal(self):
        self.getPage('/static//../../test.txt')
        self.assertStatus(403)


class ControllerOrangeThemeTest(rdiffweb.test.WebCase):

    login = True

    default_config = {'DefaultTheme': 'orange'}

    from parameterized import parameterized

    def test_static(self):
        """
        Check if the theme is properly configure.
        """
        self.getPage("/")
        self.assertStatus('200 OK')
        self.assertInBody('/static/orange.css')


class ControllerBlueThemeTest(rdiffweb.test.WebCase):

    login = True

    default_config = {'DefaultTheme': 'blue'}

    def test_theme(self):
        """
        Check if the theme is properly configure.
        """
        self.getPage("/")
        self.assertInBody('/static/blue.css')
