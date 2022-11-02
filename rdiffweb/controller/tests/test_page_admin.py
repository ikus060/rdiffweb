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
from parameterized import parameterized

import rdiffweb.test
from rdiffweb.core.model import UserObject


class AdminPagesAsUser(rdiffweb.test.WebCase):
    def setUp(self):
        super().setUp()
        # Add test user
        userobj = UserObject.add_user('test', 'test123')
        userobj.commit()
        self._login('test', 'test123')

    @parameterized.expand(
        [
            "/admin",
            "/admin/users",
            "/admin/repos",
            "/admin/session",
            "/admin/sysinfo",
            "/admin/logs",
        ]
    )
    def test_forbidden_access(self, value):
        self.getPage(value)
        self.assertStatus(403)
