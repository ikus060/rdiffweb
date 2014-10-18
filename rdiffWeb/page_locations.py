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
import librdiff
import logging
import page_main
import rdw_helpers

class rdiffLocationsPage(page_main.rdiffPage):
   ''' Shows the locations page. Will show all available destination
   backup directories. This is the root (/) page '''
   @cherrypy.expose
   def index(self):
      return self._writePage("locations.html", **self.getParmsForPage())
   
   def getParmsForPage(self):
      root = self.getUserDB().getUserRoot(self.getUsername())
      repos = self.getUserDB().getUserRepoPaths(self.getUsername())
      repoList = []
      for name in repos:
         try:
            repoHistory = librdiff.getLastBackupHistoryEntry(rdw_helpers.joinPaths(root, name))
            size = repoHistory.size
            in_progress = repoHistory.inProgress
            last_backup = repoHistory.date.getLocalSeconds()
            failed = False
         except librdiff.FileError:
            logging.exception("Can't get reference on the last backup history for %s" % name)
            size = 0
            in_progress = false
            last_backup = 0
            failed = True
         repoList.append({ "name" : name,
                           "size" : size,
                           "last_backup" : last_backup,
                           "browse_url" : self.buildBrowseUrl(name, "/", False),
                           "history_url" : self.buildHistoryUrl(name),
                           'in_progress' : in_progress,
                           'failed': failed})

      return { "title" : "Locations", "repos" : repoList }

class locationsPageTest(page_main.pageTest, rdiffLocationsPage):
   def getTemplateName(self):
      return "locations_template.txt"
   
   def getExpectedResultsName(self):
      return "locations_results.txt"
      
   def getParmsForTemplate(self, repoParentPath, repoName):
      return self.getParmsForPage(repoParentPath, [repoName])
