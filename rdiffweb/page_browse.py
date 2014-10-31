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
import urllib

from . import rdw_helpers
from . import page_main
from . import librdiff

from .rdw_helpers import encode_s, decode_s, os_path_join

# Define the logger
logger = logging.getLogger(__name__)


class rdiffBrowsePage(page_main.rdiffPage):

    @cherrypy.expose
    def index(self, repo=u"", path=u"", restore=u""):
        assert isinstance(repo, unicode)
        assert isinstance(path, unicode)
        assert isinstance(restore, unicode)

        logger.debug("browsing repo=%s&path=%s" % (repo, path))

        try:
            self.validateUserPath(os_path_join(repo, path))
        except rdw_helpers.accessDeniedError as error:
            logger.warn("Access is denied.")
            return self._writeErrorPage(unicode(error))

        # NOTE: a blank path parm is allowed, since that just results in a
        # listing of the repo root
        if not repo:
            logger.warn("Backup location not specified.")
            return self._writeErrorPage("Backup location not specified.")
        if repo not in self.getUserDB().getUserRepoPaths(self.getUsername()):
            logger.warn("Access is denied.")
            return self._writeErrorPage("Access is denied.")

        # Build the parameters
        try:
            parms = self.get_parms_for_page(repo, path, restore)
        except librdiff.FileError as error:
            logger.exception(unicode(error))
            return self._writeErrorPage(unicode(error))

        return self._writePage("browse.html", **parms)

    def get_parms_for_page(self, repo, path, restore):
        assert isinstance(repo, unicode)
        assert isinstance(path, unicode)
        assert isinstance(restore, unicode)

        # Get reference to repository
        user_root = self.getUserDB().getUserRoot(self.getUsername())
        repo_obj = librdiff.RdiffRepo(encode_s(os_path_join(user_root, repo)))
        repo_path = repo_obj.get_path(encode_s(path))

        # Build "parent directories" links
        parents = []
        parents.append({"path": "/", "name": repo.lstrip("/")})
        parent_path = u""
        for part in path.split("/"):
            if part:
                parent_path = os_path_join(parent_path, part)
                parents.append({"path": parent_path, "name": repo_obj.unquote(part)})

        # Set up warning about in-progress backups, if necessary
        if repo_obj.in_progress:
            warning = "Warning: a backup is currently in progress to this location. The displayed data may be inconsistent."
        else:
            warning = ""

        dir_entries = []
        restore_dates = []
        if restore == "T":
            title = "Restore"
            restore_dates = repo_path.restore_dates
        else:
            title = "Browse"
            # Get list of actual directory entries
            dir_entries = repo_path.dir_entries

        return {"title": title,
                "repo": repo,
                "path": path,
                "dir_entries": dir_entries,
                "parents": parents,
                "restore_dates": restore_dates,
                "warning": warning}
