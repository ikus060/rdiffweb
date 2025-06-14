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

import logging

import cherrypy

import rdiffweb.tools.errors  # noqa
from rdiffweb.controller import Controller
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject

# Define the logger
logger = logging.getLogger(__name__)


@cherrypy.tools.poppath()
class BrowsePage(Controller):
    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    def default(self, path):
        """
        Browser view displaying files and folders in user's repository
        """
        # Check user access to the given repo & path
        repo, path = RepoObject.get_repo_path(path, refresh=True)

        # Get list of actual directory entries
        if repo.status[0] == 'failed':
            dir_entries = []
        else:
            dir_entries = repo.listdir(path)
        parms = {"repo": repo, "path": path, "dir_entries": dir_entries}
        return self._compile_template("browse.html", **parms)
