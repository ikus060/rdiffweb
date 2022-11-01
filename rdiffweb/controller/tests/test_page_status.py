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
Created on Aug 30, 2019

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import rdiffweb.test
from rdiffweb.core.model import UserObject


class StatusTest(rdiffweb.test.WebCase):

    login = True

    def test_page(self):
        # When browsing the status page
        self.getPage("/status/")
        # Then no error are raised
        self.assertStatus(200)
        self.assertInBody('Backup Status')

    def test_page_with_broken_repo(self):
        # Given a user's with broken repo
        userobj = UserObject.get_user('admin')
        userobj.user_root = '/invalid/'
        userobj.commit()
        # When browsing the status page
        self.getPage("/status/")
        # Then not error should be raised
        self.assertStatus(200)
        self.assertInBody('Backup Status')
