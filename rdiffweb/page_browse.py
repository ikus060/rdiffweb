#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffweb contributors
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

from __future__ import unicode_literals

import cherrypy
import logging
import os
import page_main
import librdiff

from rdw_helpers import decode_s, unquote_url

# Define the logger
logger = logging.getLogger(__name__)


class rdiffBrowsePage(page_main.rdiffPage):

    """This contoller provide a browser view to the user. It displays file in a
    repository."""

    def _cp_dispatch(self, vpath):
        """Used to handle permalink URL.
        ref http://cherrypy.readthedocs.org/en/latest/advanced.html"""
        # Notice vpath contains bytes.
        if len(vpath) > 0:
            # /the/full/path/
            path = []
            while len(vpath) > 0:
                path.append(unquote_url(vpath.pop(0)))
            cherrypy.request.params['path_b'] = b"/".join(path)
            return self

        return vpath

    @cherrypy.expose
    def index(self, path_b=b"", restore=""):
        assert isinstance(path_b, str)
        assert isinstance(restore, unicode)

        logger.debug("browsing [%s]" % decode_s(path_b, 'replace'))

        # Check user access to the given repo & path
        try:
            (repo_obj, path_obj) = self.validate_user_path(path_b)
        except page_main.AccessDeniedError:
            logger.exception("access is denied")
            return self._writeErrorPage("Access is denied.")
        except librdiff.FileError:
            logger.exception("invalid backup location")
            return self._writeErrorPage("The backup location does not exist.")

        # Build the parameters
        try:
            parms = self.get_parms_for_page(repo_obj,
                                            path_obj,
                                            restore == b"T")
        except librdiff.FileError:
            logger.exception("invalid backup location")
            return self._writeErrorPage("The backup location does not exist.")

        return self._writePage("browse.html", **parms)

    def get_parms_for_page(self, repo_obj, path_obj, restore):
        assert isinstance(repo_obj, librdiff.RdiffRepo)
        assert isinstance(path_obj, librdiff.RdiffPath)

        # Build "parent directories" links
        parents = []
        parents.append({"path": b"", "name": repo_obj.display_name})
        parent_path_b = b""
        for part_b in path_obj.path.split(b"/"):
            if part_b:
                parent_path_b = os.path.join(parent_path_b, part_b)
                display_name = decode_s(repo_obj.unquote(part_b), 'replace')
                parents.append({"path": parent_path_b,
                                "name": display_name})

        # Set up warning about in-progress backups, if necessary
        warning = ""
        if repo_obj.in_progress:
            warning = """Warning: a backup is currently in progress to this
                      location. The displayed data may be inconsistent."""

        dir_entries = []
        restore_dates = []
        if restore:
            restore_dates = path_obj.restore_dates
        else:
            # Get list of actual directory entries
            dir_entries = path_obj.dir_entries

        return {"repo_name": repo_obj.display_name,
                "repo_path": repo_obj.path,
                "path": path_obj.path,
                "dir_entries": dir_entries,
                "parents": parents,
                "restore_dates": restore_dates,
                "warning": warning}
