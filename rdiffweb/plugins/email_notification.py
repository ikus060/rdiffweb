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

import smtplib

import rdw_config
import librdiff
import rdw_helpers
import rdw_templating
import datetime
import threading
import time

# This stuff was taken from user prefs
#
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

def startEmailNotificationThread(killEvent, app):
    newThread = emailNotifyThread(killEvent, app)
    newThread.start()


class emailNotifyThread(threading.Thread):

    def __init__(self, killEvent, app):
        self.killEvent = killEvent
        self.app = app
        threading.Thread.__init__(self)

    def run(self):
        userdb = self.app.userdb
        self.notifier = emailNotifier(userdb)
        if not self.notifier.notificationsEnabled():
            return
        emailTimeStr = self.app.config.get_config("emailNotificationTime")
        while True:
            emailTime = time.strptime(emailTimeStr, "%H:%M")
            now = datetime.datetime.now()
            nextEmailTime = now.replace(
                hour=emailTime.tm_hour, minute=emailTime.tm_min, second=0, microsecond=0)
            if nextEmailTime < now:
                nextEmailTime = nextEmailTime.replace(
                    day=nextEmailTime.day + 1)
            delta = (nextEmailTime - now).seconds
            self.killEvent.wait(delta)
            if self.killEvent.isSet():
                return

            self.notifier.sendEmails()


class emailNotifier:

    def __init__(self, userdb):
        self.userDB = userdb

    def notificationsEnabled(self):
        return self._getEmailHost() != "" and\
               self._getEmailSender() != "" and\
               self._getNotificationTimeStr() != "" and\
               self.userDB.is_modifiable()

    def sendEmails(self):
        for user in self.userDB.list():
            userRepos = self.userDB.get_repos(user)
            oldRepos = []
            for repo in userRepos:
                maxDaysOld = self.userDB.get_repo_maxage(user, repo)
                if maxDaysOld != 0:
                    # get the last backup date
                    try:
                        lastBackup = librdiff.getLastBackupHistoryEntry(
                            os.path.join(self.userDB.get_root_dir(user), repo), False)
                    except librdiff.FileError:
                        pass  # Skip repos that have never been successfully backed up
                    else:
                        if lastBackup:
                            oldestGoodBackupTime = rdw_helpers.rdwTime()
                            oldestGoodBackupTime.initFromMidnightUTC(
                                -maxDaysOld)
                            if lastBackup.date < oldestGoodBackupTime:
                                oldRepos.append(
                                    {"repo": repo, "lastBackupDate": lastBackup.date.getDisplayString(), "maxAge": maxDaysOld})

            if oldRepos:
                userEmailAddress = self.userDB.get_email(user)
                emailText = rdw_templating.compile_template(
                    "email_notification.txt", repos=oldRepos, sender=self._getEmailSender(), user=user)

                session = smtplib.SMTP(self._getEmailHost())
                session.login(
                    self._getEmailUsername(), self._getEmailPassword())
                smtpresult = session.sendmail(
                    self._getEmailSender(), userEmailAddress.split(";"), emailText)
                session.quit()

    def _getEmailHost(self):
        return rdw_config.get_config("emailHost")

    def _getEmailSender(self):
        return rdw_config.get_config("emailSender")

    def _getEmailUsername(self):
        return rdw_config.get_config("emailUsername")

    def _getEmailPassword(self):
        return rdw_config.get_config("emailPassword")

    def _getNotificationTimeStr(self):
        return rdw_config.get_config("emailNotificationTime")
