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

from cherrypy.lib.static import serve_file, serve_download

from . import librdiff
from . import page_main
from . import rdw_helpers

from .rdw_helpers import encode_s, decode_s, os_path_join

# Define the logger
logger = logging.getLogger(__name__)

class autoDeleteDir:

    def __init__(self, dirPath):
        self.dirPath = dirPath

    def __del__(self):
        rdw_helpers.removeDir(self.dirPath)


class rdiffRestorePage(page_main.rdiffPage):
    _cp_config = {"response.stream": True, "response.timeout": 3000, "request.query_string_encoding":"Latin-1"}

    @cherrypy.expose
    @cherrypy.tools.decode(default_encoding='Latin-1')
    def index(self, repo="", path="", date="", usetar="F"):
        # check encoding
        assert isinstance(repo, unicode)
        assert isinstance(path, unicode)
        # Redecode as bytes
        repo_b = repo.encode('Latin-1')
        path_b = path.encode('Latin-1')
        
        logger.debug("restore repo=%s&path=%s&date=%s" % (repo, path, date))
        try:
            self.validateUserPath(rdw_helpers.os_path_join(repo, path))
        except rdw_helpers.accessDeniedError as error:
            return self._writeErrorPage(str(error))
        if not repo:
            return self._writeErrorPage("Backup location not specified.")
        if repo not in self.getUserDB().getUserRepoPaths(self.getUsername()):
            return self._writeErrorPage("Access is denied.")
        
        # Get the restore date
        try:
            restore_date = rdw_helpers.rdwTime()
            restore_date.initFromInt(int(date))
        except:
            return self._writeErrorPage("Invalid date [%s]" % date)
        
        # Get user root directory
        user_root = self.getUserDB().getUserRoot(self.getUsername())

        try:
            # Get reference to repository
            repo_root = encode_s(os_path_join(user_root, repo))
            repo_obj = librdiff.RdiffRepo(repo_root)
            
            # Try to get reference to path
            (path_b, file_b) = os.path.split(path_b)
            if not file_b:
                file_b = path_b
                path_b = ("/".encode('Latin-1'))
            repo_path = repo_obj.get_path(path_b)
    
            # Get if backup in progress
            if repo_obj.in_progress:
                return self._writeErrorPage("""A backup is currently in
                    progress to this location. Restores are disabled until
                    this backup is complete.""")
            
            # Restore the file
            file_path_b = repo_path.restore(file_b, restore_date, usetar == "F")
            
        except librdiff.FileError as error:
            logger.exception("fail to restore")
            return self._writeErrorPage(error.getErrorString())
        
        except ValueError as error:
            logger.exception("fail to restore")
            return self._writeErrorPage(str(error))
        
        # The file name return by rdiff-backup is in bytes. We do not process
        # it. Cherrypy seams to handle it any weird encoding from this point.
        logger.info("restored file [%s]" % path)
        (directory, filename) = os.path.split(file_path_b)
        filename = filename.replace(b"\"", b"\\\"")  # Escape quotes in filename
        return serve_file(file_path_b, None, disposition=b"attachment", name=filename)
    
