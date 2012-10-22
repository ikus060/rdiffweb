
import cherrypy
import urllib
import os.path

import db
import rdw_templating
import rdw_helpers
import rdw_config

class rdiffPage:

   ############################## HELPER FUNCTIONS ###################################
   def buildBrowseUrl(self, repo, path, isRestoreView):
      url = "/browse/?repo="+rdw_helpers.encodeUrl(repo, "/")+"&path="+rdw_helpers.encodeUrl(path, "/")
      if isRestoreView:
         url = url + "&restore=T"
      return url

   def buildRestoreUrl(self, repo, path, date):
      return "/restore/?repo="+rdw_helpers.encodeUrl(repo, "/")+"&path="+rdw_helpers.encodeUrl(path, "/")+"&date="+rdw_helpers.encodeUrl(date.getUrlString())

   def buildHistoryUrl(self, repo):
      return "/history/?repo="+rdw_helpers.encodeUrl(repo, "/")

   def buildLocationsUrl(self):
      return "/"

   def compileTemplate(self, templatePath, **kwargs):
      return rdw_helpers.compileTemplate(templatePath, **kwargs)
         
   def validateUserPath(self, path):
      '''Takes a path relative to the user's root dir and validates that it is valid and within the user's root'''
      path = rdw_helpers.joinPaths(self.getUserDB().getUserRoot(self.getUsername()), rdw_helpers.encodePath(path))
      path = path.rstrip("/")
      realPath = os.path.realpath(path)
      if realPath != path:
         raise rdw_helpers.accessDeniedError
      
      # Make sure that the path starts with the user root
      # This check should be accomplished by ensurePathValid, but adding for a sanity check
      if realPath.find(rdw_helpers.encodePath(self.getUserDB().getUserRoot(self.getUsername()))) != 0:
         raise rdw_helpers.accessDeniedError
      
      
   def getUserDB(self):
      if not hasattr(cherrypy.thread_data, 'db'):
         cherrypy.thread_data.db = db.userDB().getUserDBModule()
      return cherrypy.thread_data.db


   ########################## PAGE HELPER FUNCTIONS ##################################
   def startPage(self, title, rssUrl = "", rssTitle = ""):
      return self.compileTemplate("page_start.html", title=title, rssLink=rssUrl, rssTitle=rssTitle) + self.writeTopLinks()

   def endPage(self):
      return self.compileTemplate("page_end.html")

   def writeTopLinks(self):
      pages = [("/status/", "Backup Status")]
      if self.getUserDB().modificationsSupported():
         pages.append(("/prefs", "Preferences"))
      if self.getUserDB().userIsAdmin(self.getUsername()):
         pages.append(("/admin", "Admin"))
      pages.append(("/logout", "Log Out"))
      links = []
      for page in pages:
         (url, title) = page
         links.append({"linkText" : title, "title": title, "linkUrl" : url})
      return self.compileTemplate("nav_bar.html", topLinks=links)

   def writeErrorPage(self, error):
      page = self.startPage("Error")
      page = page + error
      page = page + self.endPage()
      return page

   def writeMessagePage(self, title, message):
      page = self.startPage(title)
      page = page + message
      page = page + self.endPage()
      return page


   ########## SESSION INFORMATION #############
   def checkAuthentication(self, username, password):
      if self.getUserDB().areUserCredentialsValid(username, password):
         cherrypy.session['username'] = username
         return None
      return "Invalid username or password."

   def getUsername(self):
      username = cherrypy.session['username']
      return username
   

import unittest, shutil, tempfile, os.path
class pageTest(unittest.TestCase):
   # The dirs containing source data for automated tests are set up in the following format:
   # one folder for each test, named to describe the test
      # one folder, called repo. This contains the sample rdiff-backup repository
      # expected results for each of the page templates
   # templates for each of the pages to test

   def _getBackupTests(self):
      tests = filter(lambda x: not x.startswith(".") and os.path.isdir(rdw_helpers.joinPaths(self.destRoot, x)), os.listdir(self.destRoot))
      tests.sort()
      return tests
   
   def _getFileText(self, testName, templateName):
      return open(rdw_helpers.joinPaths(self.destRoot, testName, templateName)).read()
   
   def _copyDirWithoutSvn(self, src, dest):
      names = filter(lambda x: x != ".svn", os.listdir(src))
      os.makedirs(dest)
      for name in names:
         srcname = os.path.join(src, name)
         destname = os.path.join(dest, name)
         if os.path.isdir(srcname):
            self._copyDirWithoutSvn(srcname, destname)
         else:
            shutil.copy2(srcname, destname)

   def setUp(self):
      self.destRoot = rdw_helpers.joinPaths(os.path.realpath(tempfile.gettempdir()), "rdiffWeb")
      self.masterDirPath = os.path.realpath("tests")
      self.tearDown()
      
      # Copy and set up each test
      self._copyDirWithoutSvn(self.masterDirPath, self.destRoot)

   def tearDown(self):
      if (os.access(self.destRoot, os.F_OK)):
         rdw_helpers.removeDir(self.destRoot)

   def testCompileTemplate(self):
      for test in self._getBackupTests():
         parms = self.getParmsForTemplate(rdw_helpers.joinPaths(self.destRoot, test), "repo")
         #print parms
         
         encounteredText = rdw_templating.templateParser().parseTemplate(self._getFileText("", self.getTemplateName()), **parms)
         expectedText = self._getFileText(test, self.getExpectedResultsName())
         
         encounteredText = encounteredText.replace('\n', '')
         expectedText = expectedText.replace('\n', '')
         
         self.assertEquals(encounteredText, expectedText)
         assert encounteredText == expectedText, "Got:\n" + encounteredText + "\nExpected:\n" + expectedText + "\nEnd"
      
