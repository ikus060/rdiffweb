#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

from __future__ import absolute_import
from __future__ import unicode_literals

from datetime import timedelta
import logging
from rdiffweb.controller import Controller, validate_isinstance
from rdiffweb.core import librdiff
from rdiffweb.core import rdw_helpers
from rdiffweb.core.rdw_helpers import unquote_url

from builtins import bytes
from builtins import str
import cherrypy


# Define the logger
logger = logging.getLogger(__name__)


class StatusPage(Controller):

    def _cp_dispatch(self, vpath):
        """Used to handle permalink URL.
        reference http://cherrypy.readthedocs.org/en/latest/advanced.html"""
        # Notice path contains bytes.
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
        return self._compileStatusPageTemplate(True, userMessages,
                                               failures != "")

    @cherrypy.expose
    def entry(self, path_b=b"", date=""):
        validate_isinstance(path_b, bytes)
        validate_isinstance(date, str)
        # Validate date
        try:
            entry_time = librdiff.RdiffTime(int(date))
        except:
            logger.exception("invalid date")
            raise cherrypy.HTTPError(400, _("Invalid date."))

        if not path_b:
            userMessages = self._get_user_messages_for_day(entry_time)
        else:
            # Validate repo parameter
            repo_obj = self.app.currentuser.get_repo(path_b)

            userMessages = self._getUserMessages(
                [repo_obj.path], False, True, entry_time, entry_time)

        return self._compileStatusPageTemplate(False, userMessages, False)

    @cherrypy.expose
    def feed(self, failures=""):
        cherrypy.response.headers["Content-Type"] = "text/xml"
        userMessages = self._get_recent_user_messages(failures != "")
        statusUrl = self._buildAbsolutePageUrl(failures != "")
        return self._compile_template(
            "status.xml",
            link=statusUrl,
            messages=userMessages)

    def _compileStatusPageTemplate(self, isMainPage, messages, failuresOnly):

        if isMainPage:
            feedLink = self._buildStatusFeedUrl(failuresOnly)
            feedTitle = "Backup status for " + self.app.currentuser.username
        else:
            feedLink = ""
            feedTitle = ""
        return self._compile_template(
            "status.html",
            messages=messages,
            feedLink=feedLink,
            failuresOnly=failuresOnly,
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
        userRepos = self.app.currentuser.repos

        # Set the start and end time to be the start and end of the day,
        # respectively, to get all entries for that day
        startTime = librdiff.RdiffTime(date)
        startTime.set_time(0, 0, 0)

        endTime = librdiff.RdiffTime(date)
        endTime.set_time(23, 59, 59)

        return self._getUserMessages(userRepos, True, False,
                                     startTime, endTime)

    def _get_recent_user_messages(self, failuresOnly):
        user_repos = self.app.currentuser.repos

        asOfDate = librdiff.RdiffTime() - timedelta(days=5)

        return self._getUserMessages(user_repos, not failuresOnly, True,
                                     asOfDate, None)

    def _getUserMessages(self,
                         repos,
                         includeSuccess,
                         includeFailure,
                         earliest_date,
                         latest_date):

        user_root = self.app.currentuser.user_root

        repoErrors = []
        allBackups = []
        for repo in repos:
            repo = repo.lstrip("/")
            try:
                repo_obj = librdiff.RdiffRepo(user_root, repo)
                backups = repo_obj.get_history_entries(-1, earliest_date,
                                                       latest_date)
                allBackups += [{"repo_path": repo_obj.path,
                                "repo_name": repo_obj.display_name,
                                "date": backup.date,
                                "size": backup.size,
                                "errors": backup.errors} for backup in backups]
            except librdiff.FileError:
                logger.exception("invalid user path %s" % repo)

        allBackups.sort(key=lambda x: x["date"])
        failedBackups = [x for x in allBackups if x["errors"]]

        # group successful backups by day
        successfulBackups = [x for x in allBackups if not x["errors"]]
        if successfulBackups:
            lastSuccessDate = successfulBackups[0]["date"]
        successfulBackups = rdw_helpers.groupby(
            successfulBackups, lambda x: x["date"].get_local_day_since_epoch())

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
            for day in list(successfulBackups.keys()):
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
        userMessages.sort(key=lambda x: x["date"])
        return userMessages
