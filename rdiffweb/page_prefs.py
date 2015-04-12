#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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
import rdw_spider_repos

# Define the logger
logger = logging.getLogger(__name__)


class PreferencesPage(page_main.MainPage):

    sampleEmail = 'joe@example.com'

    @cherrypy.expose
    def index(self, action=u"", current=u"", new=u"", confirm=u""):

        params = {}

        # Process the parameters.
        if self._is_submit():
            try:
                if action == "set_password":
                    params = self._set_password(current, new, confirm)
                elif action == "update_repos":
                    params = self._update_repos()
                elif action == 'set_notifications':
                    params = self._setNotifications()
            except ValueError as e:
                params['error'] = unicode(e)
            except Exception as e:
                logger.exception("unknown error processing action")
                params['error'] = unicode(e)

        # Get page params
        try:
            params.update(self._get_parms_for_page())
        except Exception as e:
            params['error'] = unicode(e)

        return self._compile_template("prefs.html", **params)

    def _set_password(self, old_password, new_password, confirm_password):
        # Check if current database support it.
        if not self.app.userdb.is_modifiable():
            return {'error': """Password changing is not
                              supported with the active user
                              database."""}

        # Check if confirmation is valid.
        if new_password != confirm_password:
            return {'error': "The passwords do not match."}

        self.app.userdb.set_password(self.get_username(),
                                      old_password,
                                      new_password)
        return {'success': "Password updated successfully."}

    def _update_repos(self):
        rdw_spider_repos.findReposForUser(self.get_username(), self.app.userdb)
        return {'success': """Successfully updated repositories."""}

    def _setNotifications(self, parms):
        if not self.app.userdb.is_modifiable():
            return self._writePrefsPage(error="""Email notification is not
                                              supported with the active user
                                              database.""")

        repos = self.app.userdb.get_repos(self.get_username())

        for parmName in parms.keys():
            if parmName == "userEmail":
                if parms[parmName] == self.sampleEmail:
                    parms[parmName] = ''
                self.app.userdb.set_email(
                    self.get_username(), parms[parmName])
            if parmName.endswith("numDays"):
                backupName = parmName[:-7]
                if backupName in repos:
                    if parms[parmName] == "Don't notify":
                        maxDays = 0
                    else:
                        maxDays = int(parms[parmName][0])
                    self.app.userdb.set_repo_maxage(
                        self.get_username(), backupName, maxDays)

        return self._writePrefsPage(success="""Successfully changed
                                            notification settings.""")

    def _get_parms_for_page(self):
        email = self.app.userdb.get_email(self.get_username())
        parms = {
            "userEmail": email,
            "notificationsEnabled": False,
            "backups": [],
            "sampleEmail": self.sampleEmail
        }
        # if email_notification.emailNotifier().notificationsEnabled():
        #    repos = self.app.userdb.get_repos(self.get_username())
        #    backups = []
        #    for repo in repos:
        #        maxAge = self.app.userdb.get_repo_maxage(
        #            self.get_username(), repo)
        #        notifyOptions = []
        #        for i in range(0, 8):
        #            notifyStr = "Don't notify"
        #            if i == 1:
        #                notifyStr = "1 day"
        #            elif i > 1:
        #                notifyStr = str(i) + " days"
        #            selectedStr = ""
        #            if i == maxAge:
        #                selectedStr = "selected"
        #            notifyOptions.append(
        #                {"optionStr": notifyStr, "selectedStr": selectedStr})
        #        backups.append(
        #            {"backupName": repo, "notifyOptions": notifyOptions})
        #    parms.update({"notificationsEnabled": True, "backups": backups})

        return parms
