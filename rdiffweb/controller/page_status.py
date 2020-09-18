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

from datetime import timedelta
import logging

import cherrypy
from rdiffweb.controller import Controller, validate_isinstance
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core import librdiff
from rdiffweb.core import rdw_helpers

# Define the logger
logger = logging.getLogger(__name__)


@poppath()
class StatusPage(Controller):

    @cherrypy.expose
    def default(self, path=b"", date="", failures=""):
        validate_isinstance(date, str)

        # Validate date
        startTime = librdiff.RdiffTime() - timedelta(days=5)
        endTime = None
        if date:
            try:
                date = int(date)
            except:
                logger.exception("invalid date")
                raise cherrypy.HTTPError(400, _("Invalid date."))
            # Set the start and end time to be the start and end of the day,
            # respectively, to get all entries for that day
            startTime = librdiff.RdiffTime(date)
            startTime.set_time(0, 0, 0)
            endTime = librdiff.RdiffTime(date)
            endTime.set_time(23, 59, 59)

        # Limit the scope to the given path.
        if path:
            user_repos = [self.app.store.get_repo(path)]
        else:
            user_repos = self.app.currentuser.repo_objs

        failuresOnly = failures != ""
        messages = self._getUserMessages(user_repos, not failuresOnly, True, startTime, endTime)

        return self._compile_template(
            "status.html",
            messages=messages,
            failuresOnly=failuresOnly)

    def _getUserMessages(self,
                         repos,
                         includeSuccess,
                         includeFailure,
                         earliest_date,
                         latest_date):

        repoErrors = []
        allBackups = []
        for repo_obj in repos:
            backups = repo_obj.get_history_entries(-1, earliest_date, latest_date)
            allBackups += [{"repo": repo_obj,
                            "date": backup.date,
                            "size": backup.size,
                            "errors": backup.errors} for backup in backups]

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
                     "backups": []})
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
