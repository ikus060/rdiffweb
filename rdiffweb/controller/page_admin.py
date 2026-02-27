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

import cherrypy

from rdiffweb.controller.page_admin_activity import AdminActivityPage
from rdiffweb.controller.page_admin_logs import AdminLogsPage
from rdiffweb.controller.page_admin_repos import AdminReposPage
from rdiffweb.controller.page_admin_session import AdminSessionPage
from rdiffweb.controller.page_admin_sysinfo import AdminSysinfoPage
from rdiffweb.controller.page_admin_users import AdminUsersPage


@cherrypy.tools.is_admin()
class AdminPage:
    """
    Administration pages. Allow to manage users database.
    """

    logs = AdminLogsPage()
    repos = AdminReposPage()
    session = AdminSessionPage()
    sysinfo = AdminSysinfoPage()
    users = AdminUsersPage()
    activity = AdminActivityPage()
