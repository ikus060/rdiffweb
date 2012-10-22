#!/usr/bin/python

import rdw_helpers
import page_main
import rdw_templating
import cherrypy
import rdw_spider_repos


class rdiffAdminPage(page_main.rdiffPage):
   def index(self, **kwargs):
      if not self._userIsAdmin(): return self.writeErrorPage("Access denied.")
      
      # If we're just showing the initial page, just do that
      if not self._isSubmit():
         return self._generatePageHtml("", "")
      
      # We need to change values. Change them, then give back that main page again, with a message
      action = cherrypy.request.params["action"]
      username = cherrypy.request.params["username"]
      userRoot = cherrypy.request.params["userRoot"]
      userIsAdmin = cherrypy.request.params.get("isAdmin", False) != False
      
      if action == "edit":
         if not self.getUserDB().userExists(username):
            return self._generatePageHtml("", "The user does not exist.")
         
         self.getUserDB().setUserInfo(username, userRoot, userIsAdmin)
         return self._generatePageHtml("User information modified successfully", "")
      elif action == "add":
         if self.getUserDB().userExists(username):
            return self._generatePageHtml("", "The specified user already exists.", username, userRoot, userIsAdmin)
         if username == "":
            return self._generatePageHtml("", "The username is invalid.", username, userRoot, userIsAdmin)
         self.getUserDB().addUser(username)
         self.getUserDB().setUserPassword(username, cherrypy.request.params["password"])
         self.getUserDB().setUserInfo(username, userRoot, userIsAdmin)
         return self._generatePageHtml("User added successfully.", "")
      
   index.exposed = True

   def deleteUser(self, user):
      if not self._userIsAdmin(): return self.writeErrorPage("Access denied.")

      if not self.getUserDB().userExists(user):
         return self._generatePageHtml("", "The user does not exist.")

      if user == self.getUsername():
         return self._generatePageHtml("", "You cannot remove your own account!.")

      self.getUserDB().deleteUser(user)
      return self._generatePageHtml("User account removed.", "")
   deleteUser.exposed = True

   ############### HELPER FUNCTIONS #####################
   def _userIsAdmin(self):
      return self.getUserDB().userIsAdmin(self.getUsername())

   def _isSubmit(self):
      return cherrypy.request.method == "POST"

   def _generatePageHtml(self, message, error, username="", userRoot="", isAdmin=False):
      userNames = self.getUserDB().getUserList()
      users = [ { "username" : user, "isAdmin" : self.getUserDB().userIsAdmin(user), "userRoot" : self.getUserDB().getUserRoot(user) } for user in userNames ]
      parms = { "users" : users, 
                "username" : username, 
                "userRoot" : userRoot, 
                "isAdmin" : isAdmin,
                "message" : message,
                "error" : error }
      return self.startPage("Administration") + self.compileTemplate("admin_main.html", **parms) + self.endPage()

