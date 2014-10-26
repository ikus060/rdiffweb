#!/usr/bin/python
# rdiffWeb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffWeb contributors
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
from cherrypy.lib.static import serve_file, serve_download
from . import rdw_helpers
from . import page_main
from . import librdiff
import os
import logging


class autoDeleteDir:

    def __init__(self, dirPath):
        self.dirPath = dirPath

    def __del__(self):
        rdw_helpers.removeDir(self.dirPath)


class rdiffRestorePage(page_main.rdiffPage):
    _cp_config = {"response.stream": True, "response.timeout": 3000}

    @cherrypy.expose
    def index(self, repo, path, date):
        try:
            self.validateUserPath(rdw_helpers.joinPaths(repo, path))
        except rdw_helpers.accessDeniedError as error:
            return self._writeErrorPage(str(error))
        if not repo:
            return self._writeErrorPage("Backup location not specified.")
        if repo not in self.getUserDB().getUserRepoPaths(self.getUsername()):
            return self._writeErrorPage("Access is denied.")

        if librdiff.backupIsInProgressForRepo(rdw_helpers.joinPaths(self.getUserDB().getUserRoot(self.getUsername()), repo)):
            return self._writeErrorPage("A backup is currently in progress to this location.  Restores are disabled until this backup is complete.")

        try:
            restoreTime = rdw_helpers.rdwTime()
            restoreTime.initFromString(date)
            (path, file) = os.path.split(path)
            if not file:
                file = path
                path = "/"
            fullPath = rdw_helpers.joinPaths(
                self.getUserDB().getUserRoot(self.getUsername()), repo)
            useZipFormat = self.getUserDB().useZipFormat(self.getUsername())
            filePath = librdiff.restoreFileOrDir(
                fullPath, path, file, restoreTime, useZipFormat)
        except librdiff.FileError as error:
            return self._writeErrorPage(error.getErrorString())
        except ValueError as error:
            logging.exception("fail to restore")
            return self._writeErrorPage(str(error))

        (directory, filename) = os.path.split(filePath)
        filename = filename.replace("\"", "\\\"")  # Escape quotes in filename
        return serve_file(filePath, None, disposition="attachment", name=filename)
