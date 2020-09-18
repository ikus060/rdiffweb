# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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
import os
from rdiffweb.controller import Controller, validate_isinstance, validate_int
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.i18n import ugettext as _

import cherrypy

# Define the logger
logger = logging.getLogger(__name__)


@poppath()
class BrowsePage(Controller):

    """This contoller provide a browser view to the user. It displays file in a
    repository."""

    @cherrypy.expose
    def default(self, path=b"", restore="", limit='10'):
        validate_isinstance(restore, str)
        limit = validate_int(limit)
        restore = bool(restore)

        # Check user access to the given repo & path
        (repo_obj, path_obj) = self.app.store.get_repo_path(path)

        # Build the parameters
        # Build "parent directories" links
        # TODO This Should to me elsewhere. It contains logic related to librdiff encoding.
        parents = []
        parents.append({"path": b"", "name": repo_obj.display_name})
        parent_path_b = b""
        for part_b in path_obj.path.split(b'/'):
            if part_b:
                parent_path_b = os.path.join(parent_path_b, part_b)
                display_name = repo_obj._decode(repo_obj.unquote(part_b))
                parents.append({"path": parent_path_b,
                                "name": display_name})

        # Set up warning about in-progress backups, if necessary
        warning = False
        status = repo_obj.status
        if status[0] != 'ok':
            warning = status[1] + ' ' + _("The displayed data may be inconsistent.")

        dir_entries = []
        restore_dates = []
        if restore:
            restore_dates = path_obj.change_dates[:-limit - 1:-1]
        else:
            # Get list of actual directory entries
            dir_entries = path_obj.dir_entries[::-1]

        parms = {
            "repo" : repo_obj,
            "path" : path_obj,
            "limit": limit,
            "dir_entries": dir_entries,
            "parents": parents,
            "restore_dates": restore_dates,
            "warning": warning}
        return self._compile_template("browse.html", **parms)
