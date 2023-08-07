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


import cherrypy

from rdiffweb.controller import Controller, validate_int
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject


@cherrypy.tools.poppath()
class HistoryPage(Controller):
    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    def default(self, path=b"", limit='10', **kwargs):
        limit = validate_int(limit)

        repo, path = RepoObject.get_repo_path(path)

        # Set up warning about in-progress backups, if necessary
        path_obj = repo.fstat(path)
        parms = {
            "limit": limit,
            "repo": repo,
            "path": path,
            "path_obj": path_obj,
        }

        return self._compile_template("history.html", **parms)
