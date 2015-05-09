#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 rdiffweb contributors
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

import smtplib

import rdw_config
import db
import librdiff
import rdw_helpers
import rdw_templating
import datetime
import threading
import time


def startEmailNotificationThread(killEvent):
    newThread = emailNotifyThread(killEvent)
    newThread.start()


class emailNotifyThread(threading.Thread):

    def __init__(self, killEvent):
        self.killEvent = killEvent
        threading.Thread.__init__(self)

    def run(self):
        self.notifier = emailNotifier()
        if not self.notifier.notificationsEnabled():
            return
        emailTimeStr = rdw_config.get_config("emailNotificationTime")
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

    def __init__(self):
        self.userDB = db.userDB().get_userdb_module()

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
