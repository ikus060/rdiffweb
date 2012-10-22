#!/usr/bin/python

import cherrypy
import json
import os
import stat
import crypt

import page_main
import rdw_helpers


class rdiffSetupPage(page_main.rdiffPage):
   """Helps the user through initial rdiffWeb setup.
      This page is displayed with rdiffWeb is not yet configured.
      """
   @cherrypy.expose
   def index(self):
      page = rdw_helpers.compileTemplate("page_start.html", title='Set up rdiffWeb', rssLink='', rssTitle='')
      rootEnabled = False
      error = ""
      try:
         rootEnabled = self._rootAccountEnabled()
      except KeyError:
         error = "rdiffWeb setup must be run with root privileges."
      page += rdw_helpers.compileTemplate("setup.html", rootEnabled=rootEnabled, error=error)
      page += rdw_helpers.compileTemplate("page_end.html")
      return page

   @cherrypy.expose
   def ajax(self):
      postData = cherrypy.request.body.read()
      request = json.JsonReader().read(postData)
      print request
      if not 'rootPassword' in request:
         return json.JsonWriter().write({"error": "No password specified."})
         
      try:
         self._ensureConfigFileExists()

         self._validatePassword(request['rootPassword'])
         if 'adminUsername' in request:
            self._setAdminUser(request['adminUsername'], request['adminPassword'], request['adminConfirmPassword'])
         if 'adminRoot' in request:
            self._setAdminRoot(request['adminUsername'], request['adminRoot'])
      except ValueError, error:
         return json.JsonWriter().write({"error": str(error)})

      return json.JsonWriter().write({})
         
         
   def _validatePassword(self, password):
      if self._rootAccountEnabled():
         # Check the root account
         if (self._checkSystemPassword("root", password)):
            return
      else: 
         raise ValueError, "The root account has been disabled. Web-based setup is not supported."
         # If the root account is disabled, check to see if another
         # user set up the account, in which case their password is valid.
         if password != "billfrank":
            raise ValueError, "The password is invalid."
         
   def _checkSystemPassword(self, username, password):
      cryptedpasswd = self._getCryptedPassword(username)
      if crypt.crypt(password, cryptedpasswd) != cryptedpasswd:
         raise ValueError, "Invalid password."
   
   def _setAdminUser(self, username, password, confirmPassword):
      if not username:
         raise ValueError, "A username was not specified."
      if not password:
         raise ValueError, "The administrative user must have a password."
      if password != confirmPassword:
         raise ValueError, "The passwords do not match."
      
      self.getUserDB().addUser(username)
      self.getUserDB().setUserPassword(username, password)
   
   def _setAdminRoot(self, username, userRoot):
      if not username:
         raise ValueError, "A username was not specified."
      if not userRoot:
         raise ValueError, "A root directory was not specified."
      if not os.path.exists(userRoot):
         raise ValueError, "The specified directory does not exist."
      
      self.getUserDB().setUserRoot(username, userRoot)
      
   def _rootAccountEnabled(self):
      cryptedpasswd = self._getCryptedPassword("root")
      return cryptedpasswd != '!'

   def _ensureConfigFileExists(self):
      try:
         if not os.path.exists("/etc/rdiffweb"):
            os.mkdir("/etc/rdiffweb", stat.S_IRWXU)
         if not os.path.exists("/etc/rdiffweb/rdw.conf"):
            open("/etc/rdiffweb/rdw.conf", "a").close()
            os.chmod("/etc/rdiffweb/rdw.conf", stat.S_IRWXU)
      except OSError, error:
         raise ValueError, str(error)
         
   def _getCryptedPassword(self, username):
      try:
         import spwd
      except ImportError:
         return self._manualGetCryptedPassword(username)
      else:
         return spwd.getspnam(username)[1]

   def _manualGetCryptedPassword(self, username):
      pwlines = open("/etc/shadow").readlines()
      for line in pwlines:
         entryParts = line.split(":")
         if len(entryParts) == 9 and entryParts[0] == username:
            return entryParts[1]
