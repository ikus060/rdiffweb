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

import page_main
import librdiff
import rdw_helpers
import cherrypy

class rdiffStatusPage(page_main.rdiffPage):
   def index(self, failures=""):
      userMessages = self._getRecentUserMessages(failures != "")
      return self._compileStatusPageTemplate(True, userMessages, failures != "")
   index.exposed = True

   def entry(self, date="", repo=""):
      # Validate date
      try:
         entryTime = rdw_helpers.rdwTime()
         entryTime.initFromString(date)
      except ValueError:
         return self.writeErrorPage("Invalid date parameter.")

      if not repo:
         userMessages = self._getUserMessagesForDay(entryTime)
      else:
         # Validate repo parameter
         if not repo in self.getUserDB().getUserRepoPaths(self.getUsername()):
            return self.writeErrorPage("Access is denied.")
         try:
            self.validateUserPath(repo)
         except rdw_helpers.accessDeniedError, error:
            return self.writeErrorPage(str(error))

         userMessages = self._getUserMessages([repo], False, True, entryTime, entryTime)

      return self._compileStatusPageTemplate(False, userMessages, False)
   entry.exposed = True

   def feed(self, failures=""):
      cherrypy.response.headers["Content-Type"] = "text/xml"
      userMessages = self._getRecentUserMessages(failures != "")
      statusUrl = self._buildAbsolutePageUrl(failures != "")
      return self.compileTemplate("status.xml", username=self.getUsername(), link=statusUrl, messages=userMessages)
   feed.exposed = True
   
   def _compileStatusPageTemplate(self, isMainPage, messages, failuresOnly):
      
      if isMainPage: title = "Backup Status"
      else: title = "Backup Status Entry"
      feedLink = ""
      feedTitle = ""
      if isMainPage:
         feedLink = self._buildStatusFeedUrl(failuresOnly)
         feedTitle = "Backup status for " + self.getUsername()
      
      page = self.startPage("Backup Status", rssUrl=feedLink, rssTitle=feedTitle)
      page = page + self.compileTemplate("status.html",
                                         messages=messages,
                                         feedLink=feedLink,
                                         failuresOnly=failuresOnly,
                                         title=title,
                                         isEntry=not isMainPage)
      return page + self.endPage()

   def _buildAbsolutePageUrl(self, failuresOnly):
      url = cherrypy.request.base + "/status/"
      if failuresOnly:
         url = url + "?failures=T"
      return url

   def _buildStatusFeedUrl(self, failuresOnly):
      url = "/status/feed"
      if failuresOnly:
         url = url + "?failures=T"
      return url

   def _buildStatusEntryUrl(self, repo, date):
      return "entry?repo=" + rdw_helpers.encodeUrl(repo) + "&date=" + rdw_helpers.encodeUrl(date.getUrlString())
   
   def _getUserMessagesForDay(self, date):
      userRepos = self.getUserDB().getUserRepoPaths(self.getUsername())

      # Set the start and end time to be the start and end of the day, respectively, to get all entries for that day
      startTime = rdw_helpers.rdwTime()
      startTime.timeInSeconds = date.timeInSeconds
      startTime.tzOffset = date.tzOffset
      startTime.setTime(0, 0, 0)
      
      endTime = rdw_helpers.rdwTime() 	 
      endTime.timeInSeconds = date.timeInSeconds 	 
      endTime.tzOffset = date.tzOffset
      endTime.setTime(23, 59, 59)
      
      return self._getUserMessages(userRepos, True, False, startTime, endTime)

   def _getRecentUserMessages(self, failuresOnly):
      userRepos = self.getUserDB().getUserRepoPaths(self.getUsername())
      asOfDate = rdw_helpers.rdwTime()
      asOfDate.initFromMidnightUTC(-5)

      return self._getUserMessages(userRepos, not failuresOnly, True, asOfDate, None)

   def _getUserMessages(self, repos, includeSuccess, includeFailure, earliestDate, latestDate):
      userRoot = self.getUserDB().getUserRoot(self.getUsername())

      repoErrors = []
      allBackups = []
      for repo in repos:
         try:
            backups = librdiff.getBackupHistoryForDateRange(rdw_helpers.joinPaths(userRoot, repo), earliestDate, latestDate);
            allBackups += [{"repo": repo, "date": backup.date, "displayDate": backup.date.getDisplayString(),
               "size": rdw_helpers.formatFileSizeStr(backup.size), "errors": backup.errors,
               "repoLink" : self.buildBrowseUrl(repo, "/", False)} for backup in backups]
         except librdiff.FileError, error:
            repoErrors.append({"repo": repo, "error": error.getErrorString(), "repoLink" : self.buildBrowseUrl(repo, "/", False)})

      allBackups.sort(lambda x, y: cmp(y["date"], x["date"]))
      failedBackups = filter(lambda x: x["errors"], allBackups)

      # group successful backups by day
      successfulBackups = filter(lambda x: not x["errors"], allBackups)
      if successfulBackups:
         lastSuccessDate = successfulBackups[0]["date"]
      successfulBackups = rdw_helpers.groupby(successfulBackups, lambda x: x["date"].getLocalDaysSinceEpoch())

      userMessages = []

      # generate failure messages
      if includeFailure:
         for job in failedBackups:
            date = job["date"]
            job.update({"isSuccess": False, "date": date, "dateString": date.getDisplayString(), "pubDate": date.getRSSPubDateString(),
               "link": self._buildStatusEntryUrl(job["repo"], date), "repoErrors": [], "backups": [], "repo": job["repo"]})
            userMessages.append(job)

      # generate success messages (publish date is most recent backup date)
      if includeSuccess:
         for day in successfulBackups.keys():
            date = successfulBackups[day][0]["date"]

            # include repository errors in most recent entry
            if date == lastSuccessDate: repoErrorsForMsg = repoErrors
            else: repoErrorsForMsg = []

            userMessages.append({"isSuccess": 1, "date": date, "dateString": date.getDateDisplayString(), "pubDate": date.getRSSPubDateString(),
               "link": self._buildStatusEntryUrl("", date), "repoErrors": repoErrorsForMsg, "backups":successfulBackups[day]})

      # sort messages by date
      userMessages.sort(lambda x, y: cmp(y["date"], x["date"]))
      return userMessages
