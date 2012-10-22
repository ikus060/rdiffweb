#!/usr/bin/python

from cherrypy.lib.static import serve_file, serve_download
import rdw_helpers, page_main, librdiff
import os


class autoDeleteDir:
   def __init__(self, dirPath):
      self.dirPath = dirPath

   def __del__(self):
      rdw_helpers.removeDir(self.dirPath)

class rdiffRestorePage(page_main.rdiffPage):
   _cp_config = {"response.stream": True, "response.timeout": 3000 }
   
   def index(self, repo, path, date):
      try:
         self.validateUserPath(rdw_helpers.joinPaths(repo, path))
      except rdw_helpers.accessDeniedError, error:
         return self.writeErrorPage(str(error))
      if not repo: return self.writeErrorPage("Backup location not specified.")
      if not repo in self.getUserDB().getUserRepoPaths(self.getUsername()):
         return self.writeErrorPage("Access is denied.")

      if librdiff.backupIsInProgressForRepo(rdw_helpers.joinPaths(self.getUserDB().getUserRoot(self.getUsername()), repo)):
         return self.writeErrorPage("A backup is currently in progress to this location.  Restores are disabled until this backup is complete.")

      try:
         restoreTime = rdw_helpers.rdwTime()
         restoreTime.initFromString(date)
         (path, file) = os.path.split(path)
         if not file:
            file = path
            path = "/"
         fullPath = rdw_helpers.joinPaths(self.getUserDB().getUserRoot(self.getUsername()), repo)
         useZipFormat = self.getUserDB().useZipFormat(self.getUsername())
         filePath = librdiff.restoreFileOrDir(fullPath, path, file, restoreTime, useZipFormat)
      except librdiff.FileError, error:
         return self.writeErrorPage(error.getErrorString())
      except ValueError:
         return self.writeErrorPage("Invalid date parameter.")

      (directory, filename) = os.path.split(filePath)
      filename = filename.replace("\"", "\\\"") # Escape quotes in filename
      return serve_file(filePath, None, disposition="attachment", name=filename)
   index.exposed = True

