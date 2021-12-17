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

import logging

import cherrypy
import rdiffweb.tools.errors  # noqa
from rdiffweb.controller import Controller
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.librdiff import (AccessDeniedError, DoesNotExistError,
                                    SymLinkAccessDeniedError)

# Define the logger
logger = logging.getLogger(__name__)


@poppath()
class BrowsePage(Controller):

    """This contoller provide a browser view to the user. It displays file in a
    repository."""

    @cherrypy.expose
    @cherrypy.tools.errors(error_table={
        DoesNotExistError: 404,
        AccessDeniedError: 403,
        SymLinkAccessDeniedError: 403,
    })
    def default(self, path=b""):

        # Check user access to the given repo & path
        (repo_obj, path_obj) = self.app.store.get_repo_path(path)

        # Set up warning about in-progress backups, if necessary
        warning = False
        status = repo_obj.status
        if status[0] != 'ok':
            warning = status[1] + ' ' + _("The displayed data may be inconsistent.")

        # Get list of actual directory entries
        dir_entries = path_obj.dir_entries[::-1]

        parms = {
            "repo": repo_obj,
            "path": path_obj,
            "dir_entries": dir_entries,
            "warning": warning}
        return self._compile_template("browse.html", **parms)
