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
from rdw_helpers import joinPaths, encodePath
import rdw_helpers, page_main, librdiff
import os
import urllib

class rdiffBrowsePage(page_main.rdiffPage):
   
   @cherrypy.expose
   def index(self, repo="", path="", restore=""):
      try:
         self.validateUserPath(joinPaths(repo, path))
      except rdw_helpers.accessDeniedError, error:
         return self._writeErrorPage(str(error))

      # NOTE: a blank path parm is allowed, since that just results in a listing of the repo root
      if not repo: return self._writeErrorPage("Backup location not specified.")
      if not repo in self.getUserDB().getUserRepoPaths(self.getUsername()):
         return self._writeErrorPage("Access is denied.")

      try:
         parms = self.getParmsForPage(repo, path, restore)
      except librdiff.FileError, error:
         return self._writeErrorPage(str(error))
      return self._writePage("browse.html", **parms)
   
   def getParmsForPage(self, repo="", path="", restore=""):
      userRoot = self.getUserDB().getUserRoot(self.getUsername())
      repo = encodePath(repo)
      path = encodePath(path)
      # Build "parent directories" links
      parentDirs = []
      parentDirs.append({ "parentPath" : self.buildBrowseUrl(repo, "/", False), "parentDir" : repo.lstrip("/") })
      parentDirPath = "/"
      for parentDir in path.split("/"):
         if parentDir:
            parentDirPath = joinPaths(parentDirPath, parentDir)
            parentDirs.append({ "parentPath" : self.buildBrowseUrl(repo, parentDirPath, False), "parentDir" : parentDir })
      parentDirs[-1]["parentPath"] = ""  # Clear link for last parent, so it doesn't show it as a link

      # Set up warning about in-progress backups, if necessary
      if librdiff.backupIsInProgressForRepo(joinPaths(userRoot, repo)):
         backup_warning = "Warning: a backup is currently in progress to this location. The displayed data may be inconsistent."
      else:
         backup_warning = ""

      restore_url = ""
      view_url = ""
      if restore == "T":
         title = "Restore"
         view_url = self.buildBrowseUrl(repo, path, False)
         tempDates = librdiff.getDirRestoreDates(joinPaths(userRoot, repo), path)
         tempDates.reverse()  # sort latest first
         restore_dates = []
         for x in tempDates:
            restore_dates.append({ "url" : self.buildRestoreUrl(repo, path, x),
                                 "date" : x.getLocalSeconds()})
         entries = []
      else:
         title = "Browse"
         restore_url = self.buildBrowseUrl(repo, path, True)
         restore_dates = []

         # Get list of actual directory entries
         fullRepoPath = joinPaths(userRoot, repo)
         libEntries = librdiff.getDirEntries(fullRepoPath, path)

         entries = []
         for libEntry in libEntries:
            entryLink = ""
            if libEntry.isDir:
               entryLink = self.buildBrowseUrl(repo, joinPaths(path, libEntry.name), False)
               file_type = "folder"
               size = 0 
               change_dates = []
            else:
               entryLink = self.buildRestoreUrl(repo, joinPaths(path, libEntry.name), libEntry.changeDates[-1])
               file_type = "file"
               entryChangeDates = libEntry.changeDates[:-1]
               entryChangeDates.reverse()
               size = libEntry.fileSize
               change_dates = [ { "url" : self.buildRestoreUrl(repo, joinPaths(path, libEntry.name), x),
                                 "date" : x.getLocalSeconds() } for x in entryChangeDates]

            entries.append({ "name" : libEntry.name,
                           "restore_url" : entryLink,
                           "file_type" : file_type,
                           "exists" : libEntry.exists,
                           "date" : libEntry.changeDates[-1].getLocalSeconds(),
                           "size" : size,
                           "change_dates" : change_dates})

      return { "title" : title,
              "files" : entries,
              "parentDirs" : parentDirs,
              "restore_url" : restore_url,
              "view_url" : view_url,
              "restore_dates" : restore_dates,
              "warning" : backup_warning }

class browsePageTest(page_main.pageTest, rdiffBrowsePage):
   def getTemplateName(self):
      return "browse_template.txt"
   
   def getExpectedResultsName(self):
      return "browse_results.txt"
      
   def getParmsForTemplate(self, repoParentPath, repoName):
      return self.getParmsForPage(repoParentPath, repoName)
