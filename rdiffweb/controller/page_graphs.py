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

from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject

from . import validate_int


class Data:
    def __init__(self, repo_obj, limit):
        self.repo_obj = repo_obj
        self.limit = limit

    @property
    def labels(self):
        return [s.starttime for s in self.repo_obj.session_statistics[-self.limit :]]

    def __getattr__(self, name):
        return [getattr(s, name) for s in self.repo_obj.session_statistics[-self.limit :]]


@cherrypy.tools.poppath()
class GraphsPage:

    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    @cherrypy.tools.jinja2(template="graphs.html")
    @cherrypy.expose()
    def default(self, path, limit='7', **kwargs):
        limit = validate_int(limit, min=1)
        repo_obj = RepoObject.get_repo(path)
        data = Data(repo_obj, limit)

        # Check if any action to process.
        return {
            'repo': repo_obj,
            'limit': limit,
            'data': data,
        }
