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
import os
import urllib

from . import librdiff
from . import page_main
from . import rdw_helpers

from .rdw_helpers import encode_s, decode_s, os_path_join


class rdiffHistoryPage(page_main.rdiffPage):

    @cherrypy.expose
    def index(self, repo):
        try:
            self.validateUserPath(repo)
        except rdw_helpers.accessDeniedError as error:
            return self._writeErrorPage(str(error))

        if not repo:
            logger.warn("Backup location not specified.")
            return self._writeErrorPage("Backup location not specified.")
        if repo not in self.getUserDB().getUserRepoPaths(self.getUsername()):
            logger.warn("Access is denied.")
            return self._writeErrorPage("Access is denied.")

        parms = {}
        try:
            parms = self.getParmsForPage(repo)
        except librdiff.FileError as error:
            logger.exception(str(error))
            return self._writeErrorPage(error.getErrorString())

        return self._writePage("history.html", **parms)

    def getParmsForPage(self, repo):
        assert isinstance(repo, unicode)
        
        # Get reference to repository
        user_root = self.getUserDB().getUserRoot(self.getUsername())
        repo_obj = librdiff.RdiffRepo(encode_s(os_path_join(user_root, repo)))
        
        # Get history for the repo.
        history_entries = repo_obj.get_history_entries()
        
        return {"title": "Backup history", "history_entries": history_entries}


class historyPageTest(page_main.pageTest, rdiffHistoryPage):

    def getTemplateName(self):
        return "history_template.txt"

    def getExpectedResultsName(self):
        return "history_results.txt"

    def getParmsForTemplate(self, repoParentPath, repoName):
        return self.getParmsForPage(rdw_helpers.os_path_join(repoParentPath, repoName), repoName)
