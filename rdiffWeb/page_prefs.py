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
import page_main, librdiff
import os
import urllib
import rdw_spider_repos
import email_notification


class rdiffPreferencesPage(page_main.rdiffPage):
   
   sampleEmail = 'joe@example.com'
   
   @cherrypy.expose
   def index(self, **parms):
      if parms:
         action = parms['form']
         if action == 'setPassword':
            return self._changePassword(parms['current'], parms['new'], parms['confirm'])
         elif action == 'updateRepos':
            return self._updateRepos()
         elif action == 'setNotifications':
            return self._setNotifications(parms)
         elif action == 'setRestoreType':
            return self._setRestoreType(parms['restoreType'])
         else:
            return self._writePrefsPage(error='Invalid setting.')
         
      return self._writePrefsPage()
   
   def _changePassword(self, currentPassword, newPassword, confirmPassword):
      if not self.getUserDB().modificationsSupported():
         return self._writePrefsPage(error="Password changing is not supported with the active user database.")
      
      if not self.getUserDB().areUserCredentialsValid(self.getUsername(), currentPassword):
         return self._writePrefsPage(error="The 'Current Password' is invalid.")
      
      if newPassword != confirmPassword:
         return self._writePrefsPage(error="The passwords do not match.")

      self.getUserDB().setUserPassword(self.getUsername(), newPassword)      
      return self._writePrefsPage(success="Password updated successfully.")
   
   def _updateRepos(self):
      rdw_spider_repos.findReposForUser(self.getUsername(), self.getUserDB())
      return self._writePrefsPage(success="Successfully updated backup locations.")

   def _setNotifications(self, parms):
      if not self.getUserDB().modificationsSupported():
         return self._writePrefsPage(error="Email notification is not supported with the active user database.")
      
      repos = self.getUserDB().getUserRepoPaths(self.getUsername())
      
      for parmName in parms.keys():
         if parmName == "userEmail":
            if parms[parmName] == self.sampleEmail:
               parms[parmName] = ''
            self.getUserDB().setUserEmail(self.getUsername(), parms[parmName])
         if parmName.endswith("numDays"):
            backupName = parmName[:-7]
            if backupName in repos:
               if parms[parmName] == "Don't notify":
                  maxDays = 0
               else:
                  maxDays = int(parms[parmName][0])
               self.getUserDB().setRepoMaxAge(self.getUsername(), backupName, maxDays)
               
      return self._writePrefsPage(success="Successfully changed notification settings.")
   
   def _setRestoreType(self, restoreType):
      if not self.getUserDB().modificationsSupported():
         return self.getPrefsPage(error="Setting the restore format is not supported with the active user database.")
      
      if restoreType == 'zip' or restoreType == 'tgz':
         self.getUserDB().setUseZipFormat(self.getUsername(), restoreType == 'zip')
      else:
         return self._writePrefsPage(error='Invalid restore format.')
      return self._writePrefsPage(success="Successfully set restore format.")
   
   def getParmsForPage(self):
      email = self.getUserDB().getUserEmail(self.getUsername());
      parms = {
         "title" : "User Preferences",
         "userEmail" : email,
         "notificationsEnabled" : False,
         "backups" : [],
         "useZipFormat": self.getUserDB().useZipFormat(self.getUsername()),
         "sampleEmail": self.sampleEmail
      }
      if email_notification.emailNotifier().notificationsEnabled():
         repos = self.getUserDB().getUserRepoPaths(self.getUsername())
         backups = []
         for repo in repos:
            maxAge = self.getUserDB().getRepoMaxAge(self.getUsername(), repo)
            notifyOptions = []
            for i in range(0, 8):
               notifyStr = "Don't notify"
               if i == 1:
                  notifyStr = "1 day"
               elif i > 1:
                  notifyStr = str(i) + " days"
                  
               selectedStr = ""
               if i == maxAge:
                  selectedStr = "selected"
               
               notifyOptions.append({ "optionStr": notifyStr, "selectedStr": selectedStr })
               
            backups.append({ "backupName" : repo, "notifyOptions" : notifyOptions })
         
         parms.update({ "notificationsEnabled" : True, "backups" : backups })
         
      return parms
      
   def _writePrefsPage(self, **kwargs):
      parms = self.getParmsForPage()
      parms.update(kwargs)
      return self._writePage("prefs.html", **parms)
