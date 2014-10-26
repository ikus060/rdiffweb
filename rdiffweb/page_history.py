#!/usr/bin/python
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

import cherrypy
from .rdw_helpers import joinPaths
from . import rdw_helpers
from . import page_main
from . import librdiff
import os
import urllib


class rdiffHistoryPage(page_main.rdiffPage):

    @cherrypy.expose
    def index(self, repo):
        try:
            self.validateUserPath(repo)
        except rdw_helpers.accessDeniedError as error:
            return self._writeErrorPage(str(error))

        if not repo:
            return self._writeErrorPage("Backup location not specified.")
        if repo not in self.getUserDB().getUserRepoPaths(self.getUsername()):
            return self._writeErrorPage("Access is denied.")

        parms = {}
        try:
            repoPath = joinPaths(
                self.getUserDB().getUserRoot(self.getUsername()), repo)
            parms = self.getParmsForPage(repoPath, repo)
        except librdiff.FileError as error:
            return self._writeErrorPage(error.getErrorString())

        return self._writePage("history.html", **parms)

    def getParmsForPage(self, repoPath, repoName):
        rdiffHistory = librdiff.getBackupHistory(repoPath)
        rdiffHistory.reverse()
        entries = []
        cumulative_size = 0
        if len(rdiffHistory) > 0:
            cumulative_size = rdiffHistory[0].size

        for historyItem in rdiffHistory:
            size = ""
            incrementSize = ""
            cumulativeSizeStr = ""
            if not historyItem.inProgress:
                size = historyItem.size
                incrementSize = historyItem.incrementSize
                cumulative_size += historyItem.incrementSize
            entries.append({"date": historyItem.date.getLocalSeconds(),
                            "in_progress": historyItem.inProgress,
                            "errors": historyItem.errors,
                            "cumulative_size": cumulative_size,
                            "size": size})
        return {"title": "Backup history - " + repoName, "history": entries}


class historyPageTest(page_main.pageTest, rdiffHistoryPage):

    def getTemplateName(self):
        return "history_template.txt"

    def getExpectedResultsName(self):
        return "history_results.txt"

    def getParmsForTemplate(self, repoParentPath, repoName):
        return self.getParmsForPage(rdw_helpers.joinPaths(repoParentPath, repoName), repoName)
