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

import datetime

import cherrypy

from rdiffweb.controller import Controller
from rdiffweb.controller.page_admin_logs import AdminLogsPage
from rdiffweb.controller.page_admin_repos import AdminReposPage
from rdiffweb.controller.page_admin_session import AdminSessionPage
from rdiffweb.controller.page_admin_sysinfo import AdminSysinfoPage
from rdiffweb.controller.page_admin_users import AdminUsersPage
from rdiffweb.core.model import RepoObject, SessionObject, UserObject


@cherrypy.tools.is_admin()
class AdminPage(Controller):
    """Administration pages. Allow to manage users database."""

    logs = AdminLogsPage()
    repos = AdminReposPage()
    session = AdminSessionPage()
    sysinfo = AdminSysinfoPage()
    users = AdminUsersPage()

    @cherrypy.expose
    def default(self):
        last_hour = datetime.datetime.now() - datetime.timedelta(hours=1)
        params = {
            "user_count": UserObject.query.count(),
            "repo_count": RepoObject.query.count(),
            "session_count": SessionObject.query.filter(SessionObject.access_time > last_hour).count(),
        }
        return self._compile_template("admin.html", **params)
