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

import page_main
import librdiff
import rdw_helpers

from rdw_helpers import encode_s, decode_s, unquote_url

# Define the logger
logger = logging.getLogger(__name__)


class rdiffStatusPage(page_main.rdiffPage):

    def _cp_dispatch(self, vpath):
        """Used to handle permalink URL.
        ref http://cherrypy.readthedocs.org/en/latest/advanced.html"""
        # Notice vpath contains bytes.
        if len(vpath) > 0:
            # /the/full/path/
            path = []
            while len(vpath) > 0:
                path.append(unquote_url(vpath.pop(0)))
            cherrypy.request.params['path_b'] = b"/".join(path)
            return self

        return vpath

    @cherrypy.expose
    def index(self, failures=""):
        userMessages = self._get_recent_user_messages(failures != "")
        return self._compileStatusPageTemplate(True, userMessages, failures != "")

    @cherrypy.expose
    def entry(self, path_b=b"", date=""):
        assert isinstance(path_b, str)
        assert isinstance(date, unicode)
        # Validate date
        try:
            entry_time = rdw_helpers.rdwTime()
            entry_time.initFromInt(int(date))
        except ValueError:
            logger.exception("invalid date parameter")
            return self._writeErrorPage("Invalid date parameter.")

        if not path_b:
            userMessages = self._get_user_messages_for_day(entry_time)
        else:
            # Validate repo parameter
            try:
                (repo_obj, path_obj) = self.validate_user_path(path_b)
            except rdw_helpers.accessDeniedError:
                logger.exception("access is denied")
                return self._writeErrorPage("Access is denied.")

            userMessages = self._getUserMessages(
                [repo_obj.path], False, True, entry_time, entry_time)

        return self._compileStatusPageTemplate(False, userMessages, False)

    @cherrypy.expose
    def feed(self, failures=""):
        cherrypy.response.headers["Content-Type"] = "text/xml"
        userMessages = self._get_recent_user_messages(failures != "")
        statusUrl = self._buildAbsolutePageUrl(failures != "")
        return self._writePage("status.xml", link=statusUrl, messages=userMessages)

    def _compileStatusPageTemplate(self, isMainPage, messages, failuresOnly):

        if isMainPage:
            title = "Backup Status"
            feedLink = self._buildStatusFeedUrl(failuresOnly)
            feedTitle = "Backup status for " + self.getUsername()
        else:
            title = "Backup Status Entry"
            feedLink = ""
            feedTitle = ""
        return self._writePage("status.html",
                               messages=messages,
                               feedLink=feedLink,
                               failuresOnly=failuresOnly,
                               title=title,
                               rssUrl=feedLink,
                               rssTitle=feedTitle,
                               isEntry=not isMainPage)

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

    def _get_user_messages_for_day(self, date):
        userRepos = self.getUserDB().getUserRepoPaths(self.getUsername())

        # Set the start and end time to be the start and end of the day,
        # respectively, to get all entries for that day
        startTime = rdw_helpers.rdwTime()
        startTime.timeInSeconds = date.timeInSeconds
        startTime.tzOffset = date.tzOffset
        startTime.setTime(0, 0, 0)

        endTime = rdw_helpers.rdwTime()
        endTime.timeInSeconds = date.timeInSeconds
        endTime.tzOffset = date.tzOffset
        endTime.setTime(23, 59, 59)

        return self._getUserMessages(userRepos, True, False, startTime, endTime)

    def _get_recent_user_messages(self, failuresOnly):
        user_repos = self.getUserDB().getUserRepoPaths(self.getUsername())
        asOfDate = rdw_helpers.rdwTime()
        asOfDate.initFromMidnightUTC(-5)

        return self._getUserMessages(user_repos, not failuresOnly, True, asOfDate, None)

    def _getUserMessages(self,
                         repos,
                         includeSuccess,
                         includeFailure,
                         earliest_date,
                         latest_date):
        user_root_b = encode_s(self.getUserDB().getUserRoot(self.getUsername()))

        repoErrors = []
        allBackups = []
        for repo in repos:
            # Get binary representation of the repo
            repo_b = encode_s(repo) if isinstance(repo, unicode) else repo
            repo_b = repo_b.lstrip(b"/")
            try:
                repo_obj = librdiff.RdiffRepo(user_root_b, repo_b)
                backups = repo_obj.get_history_entries(-1, earliest_date, latest_date)
                allBackups += [{"repo_path": repo_obj.path,
                                "repo_name": repo_obj.display_name,
                                "date": backup.date,
                                "size": backup.size,
                                "errors": backup.errors} for backup in backups]
            except librdiff.FileError as error:
                repoErrors.append(
                    {"repo_path": repo_b,
                     "repo_name": decode_s(repo_b, 'replace'),
                     "error": error.getErrorString()})

        allBackups.sort(lambda x, y: cmp(y["date"], x["date"]))
        failedBackups = filter(lambda x: x["errors"], allBackups)

        # group successful backups by day
        successfulBackups = filter(lambda x: not x["errors"], allBackups)
        if successfulBackups:
            lastSuccessDate = successfulBackups[0]["date"]
        successfulBackups = rdw_helpers.groupby(
            successfulBackups, lambda x: x["date"].getLocalDaysSinceEpoch())

        userMessages = []

        # generate failure messages
        if includeFailure:
            for job in failedBackups:
                date = job["date"]
                job.update(
                    {"is_success": False,
                     "date": date,
                     "repoErrors": [],
                     "backups": [],
                     "repo_path": job["repo_path"],
                     "repo_name": job["repo_name"]})
                userMessages.append(job)

        # generate success messages (publish date is most recent backup date)
        if includeSuccess:
            for day in successfulBackups.keys():
                date = successfulBackups[day][0]["date"]

                # include repository errors in most recent entry
                if date == lastSuccessDate:
                    repoErrorsForMsg = repoErrors
                else:
                    repoErrorsForMsg = []

                userMessages.append(
                    {"is_success": True,
                     "date": date,
                     "repoErrors": repoErrorsForMsg,
                     "backups": successfulBackups[day]})

        # sort messages by date
        userMessages.sort(lambda x, y: cmp(y["date"], x["date"]))
        return userMessages
