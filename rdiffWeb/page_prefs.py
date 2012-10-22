#!/usr/bin/python

from rdw_helpers import joinPaths
import rdw_helpers, page_main, librdiff
import os
import urllib
import rdw_spider_repos
import email_notification


class rdiffPreferencesPage(page_main.rdiffPage):
   
   sampleEmail = 'joe@example.com'
   
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
            return self._getPrefsPage(errorMessage='Invalid setting.')
         
      return self._getPrefsPage('', '')
   index.exposed = True
   
   def _changePassword(self, currentPassword, newPassword, confirmPassword):
      if not self.getUserDB().modificationsSupported():
         return self._getPrefsPage(errorMessage="Password changing is not supported with the active user database.")
      
      if not self.getUserDB().areUserCredentialsValid(self.getUsername(), currentPassword):
         return self._getPrefsPage(errorMessage="The 'Current Password' is invalid.")
      
      if newPassword != confirmPassword:
         return self._getPrefsPage(errorMessage="The passwords do not match.")

      self.getUserDB().setUserPassword(self.getUsername(), newPassword)      
      return self._getPrefsPage(statusMessage="Password updated successfully.")
   
   def _updateRepos(self):
      rdw_spider_repos.findReposForUser(self.getUsername(), self.getUserDB())
      return self._getPrefsPage(statusMessage="Successfully updated backup locations.")

   def _setNotifications(self, parms):
      if not self.getUserDB().modificationsSupported():
         return self._getPrefsPage(errorMessage="Email notification is not supported with the active user database.")
      
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
               
      return self._getPrefsPage(statusMessage="Successfully changed notification settings.")
   
   def _setRestoreType(self, restoreType):
      if not self.getUserDB().modificationsSupported():
         return self.getPrefsPage(errorMessage="Setting the restore format is not supported with the active user database.")
      
      if restoreType == 'zip' or restoreType == 'tgz':
         self.getUserDB().setUseZipFormat(self.getUsername(), restoreType == 'zip')
      else:
         return self._getPrefsPage(errorMessage='Invalid restore format.')
      return self._getPrefsPage(statusMessage="Successfully set restore format.")
   
   def _getPrefsPage(self, errorMessage="", statusMessage=""):
      title = "User Preferences"
      email = self.getUserDB().getUserEmail(self.getUsername());
      parms = {
         "title" : title,
         "error" : errorMessage,
         "message" : statusMessage,
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
         
      return self.startPage(title) + self.compileTemplate("user_prefs.html", **parms) + self.endPage()
      

