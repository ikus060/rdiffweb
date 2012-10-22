#!/usr/bin/python

import cherrypy
import page_main
import rdw_helpers
import base64

_loginUrl = "/login"
_logoutUrl = "/logout"
_sessionUserNameKey = "username"

def handle_authentication(authMethod='', checkAuth=None):
   checkLoginAndPassword = checkAuth
   if not checkLoginAndPassword:
      checkLoginAndPassword = (lambda username, password: u"Invalid username or password")

   if cherrypy.request.path_info == _logoutUrl:
      cherrypy.session[_sessionUserNameKey] = None
      cherrypy.request.user = None
      raise cherrypy.HTTPRedirect("/")

   elif cherrypy.session.get(_sessionUserNameKey):
      # page passes credentials; allow to be processed
      if cherrypy.request.path_info == _loginUrl:
         raise cherrypy.HTTPRedirect("/")
      return False

   if authMethod == "HTTP Header":
      # if not already authenticated, authenticate via the Authorization header
      httpAuth = _getHTTPAuthorizationCredentials(cherrypy.request.headers.get("Authorization", ""))
      if httpAuth:
         error = checkLoginAndPassword(httpAuth["login"], httpAuth["password"])
         if not error:
            return False
      else:
         error = ""

      cherrypy.response.status = "401 Unauthorized"
      cherrypy.response.body = "Not Authorized\n" + error
      cherrypy.response.headers["WWW-Authenticate"] = 'Basic realm="rdiffWeb"'
      return True

   loginKey = "login"
   passwordKey = "password"
   redirectKey = "redirect"

   loginParms = {"message": "", "action": _loginUrl,
      "loginKey": loginKey, "passwordKey": passwordKey, "redirectKey": redirectKey,
      "loginValue": "", "redirectValue": cherrypy.request.path_info + "?" + cherrypy.request.query_string }

   if cherrypy.request.path_info == _loginUrl and cherrypy.request.method == "POST":
      # check for login credentials
      loginValue = cherrypy.request.params[loginKey]
      passwordValue = cherrypy.request.params[passwordKey]
      redirectValue = cherrypy.request.params[redirectKey]
      errorMsg = checkLoginAndPassword(loginValue, passwordValue)
      if not errorMsg:
         cherrypy.session[_sessionUserNameKey] = loginValue
         if not redirectValue:
            redirectValue = "/"
         raise cherrypy.HTTPRedirect(redirectValue)

      # update form values
      loginParms["message"] = errorMsg
      loginParms["loginValue"] = loginValue
      loginParms["redirectValue"] = redirectValue

   # write login page
   loginPage = page_main.rdiffPage()
   cherrypy.response.body = loginPage.compileTemplate("page_start.html", title="Login Required - rdiffWeb", rssLink='', rssTitle='', **loginParms) + loginPage.compileTemplate("login.html", **loginParms)
   return True

cherrypy.tools.authenticate = cherrypy._cptools.HandlerTool(handle_authentication)


def _getHTTPAuthorizationCredentials(authHeader):
   try:
      (realm, authEnc) = authHeader.split()
   except ValueError:
      return None

   if realm.lower() == "basic":
      auth = base64.decodestring(authEnc)
      colon = auth.find(":")
      if colon != -1:
         return { "login": auth[:colon], "password": auth[colon+1:] }
      else:
         return { "login": auth, "password": "" }

   return None

##################### Unit Tests #########################

import unittest, os
class rdwAuthenticationFilterTest(unittest.TestCase):
   """Unit tests for the rdwAuthenticationFilter class"""

   def testAuthorization(self):
      assert not _getHTTPAuthorizationCredentials("")
      assert not _getHTTPAuthorizationCredentials("Basic Username Password")
      assert not _getHTTPAuthorizationCredentials("Digest " + base64.encodestring("username"))
      assert _getHTTPAuthorizationCredentials("Basic " + base64.encodestring("username")) == { "login": "username", "password": "" }
      assert _getHTTPAuthorizationCredentials("Basic " + base64.encodestring("user:pass")) == { "login": "user", "password": "pass" }
      assert _getHTTPAuthorizationCredentials("Basic " + base64.encodestring("user:pass:word")) == { "login": "user", "password": "pass:word" }
