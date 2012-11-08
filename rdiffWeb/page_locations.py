#!/usr/bin/python

import librdiff
import logging
import page_main
import rdw_helpers

class rdiffLocationsPage(page_main.rdiffPage):
   ''' Shows the locations page. Will show all available destination
   backup directories. This is the root (/) page '''
   def index(self):
      page = self.startPage("Backup Locations")
      page = page + self.compileTemplate("repo_listing.html", **self.getParmsForPage(self.getUserDB().getUserRoot(self.getUsername()), self.getUserDB().getUserRepoPaths(self.getUsername())))
      page = page + self.endPage()
      return page
   index.exposed = True
   
   def getParmsForPage(self, root, repos):
      repoList = []
      for reponame in repos:
         try:
            repoHistory = librdiff.getLastBackupHistoryEntry(rdw_helpers.joinPaths(root, reponame))
            reposize = rdw_helpers.formatFileSizeStr(repoHistory.size)
            reposizeinbytes = repoHistory.size
            if repoHistory.inProgress:
               reposize = "In Progress"
            repoDate = repoHistory.date.getDisplayString()
            repodateinseconds = repoHistory.date.getLocalSeconds()
            failed = False
         except librdiff.FileError:
            logging.exception("Can't get reference on the last backup history for %s" % reponame)
            reposize = "0"
            reposizeinbytes = 0 
            repoDate = "Error"
            repodateinseconds = 0
            failed = True
         repoList.append({ "reponame" : reponame,
                           "reposize" : reposize,
                           "reposizeinbytes" : reposizeinbytes,
                           "repodate" : repoDate,
                           "repodateinseconds" : repodateinseconds,
                           "repoBrowseUrl" : self.buildBrowseUrl(reponame, "/", False),
                           "repoHistoryUrl" : self.buildHistoryUrl(reponame),
                           'failed': failed})

      self._sortLocations(repoList)
      return { "title" : "browse", "repos" : repoList }
            
            
   def _sortLocations(self, locations):
      def compare(left, right):
         if left['failed'] != right['failed']:
            return cmp(left['failed'], right['failed'])
         return cmp(left['reponame'], right['reponame'])
      
      locations.sort(compare)
      

class locationsPageTest(page_main.pageTest, rdiffLocationsPage):
   def getTemplateName(self):
      return "locations_template.txt"
   
   def getExpectedResultsName(self):
      return "locations_results.txt"
      
   def getParmsForTemplate(self, repoParentPath, repoName):
      return self.getParmsForPage(repoParentPath, [repoName])
