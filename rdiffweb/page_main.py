# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffweb contributors
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
import urllib
import os.path

from . import db
from . import rdw_templating
from . import rdw_helpers
from . import rdw_config


class rdiffPage:

    # HELPER FUNCTIONS #

    def buildBrowseUrl(self, repo, path, isRestoreView):
        url = "/browse/?repo=" + rdw_helpers.encodeUrl(
            repo, "/") + "&path=" + rdw_helpers.encodeUrl(path, "/")
        if isRestoreView:
            url = url + "&restore=T"
        return url

    def buildRestoreUrl(self, repo, path, date):
        return "/restore/?repo=" + rdw_helpers.encodeUrl(repo, "/") + "&path=" + rdw_helpers.encodeUrl(path, "/") + "&date=" + rdw_helpers.encodeUrl(date.getUrlString())

    def buildHistoryUrl(self, repo):
        return "/history/?repo=" + rdw_helpers.encodeUrl(repo, "/")

    def validateUserPath(self, path):
        '''Takes a path relative to the user's root dir and validates that it is valid and within the user's root'''
        path = rdw_helpers.joinPaths(self.getUserDB().getUserRoot(
            self.getUsername()), rdw_helpers.encodePath(path))
        path = path.rstrip("/")
        realPath = os.path.realpath(path)
        if realPath != path:
            raise rdw_helpers.accessDeniedError

        # Make sure that the path starts with the user root
        # This check should be accomplished by ensurePathValid, but adding for
        # a sanity check
        if realPath.find(rdw_helpers.encodePath(self.getUserDB().getUserRoot(self.getUsername()))) != 0:
            raise rdw_helpers.accessDeniedError

    def getUserDB(self):
        if not hasattr(cherrypy.thread_data, 'db'):
            cherrypy.thread_data.db = db.userDB().getUserDBModule()
        return cherrypy.thread_data.db

    # PAGE HELPER FUNCTIONS #

    def _is_submit(self):
        return cherrypy.request.method == "POST"

    def _writeErrorPage(self, error):
        return self._writePage("error.html", title="Error", error=error)

    def _writePage(self, template_name, **kwargs):
        """Used to generate a standard html page using the given template.
        This method should be used by subclasses to provide default template
        value."""
        parms = {"title": "rdiffweb",
                 "is_login": True,
                 "is_admin": self._user_is_admin(),
                 "username": self.getUsername()}
        parms.update(kwargs)
        return rdw_templating.compileTemplate(template_name, **parms)

    # SESSION INFORMATION #
    def checkAuthentication(self, username, password):
        # Check credential using local database.
        if self.getUserDB().areUserCredentialsValid(username, password):
            cherrypy.session['username'] = username
            return None
        return "Invalid username or password."

    def getUsername(self):
        try:
            return cherrypy.session['username']
        except:
            return None

    def _user_is_admin(self):
        """Check if current user is administrator. Return True or False."""
        if self.getUsername():
            return self.getUserDB().userIsAdmin(self.getUsername())
        return False

import unittest
import shutil
import tempfile
import os.path


class pageTest(unittest.TestCase):
    # The dirs containing source data for automated tests are set up in the following format:
    # one folder for each test, named to describe the test
        # one folder, called repo. This contains the sample rdiff-backup repository
        # expected results for each of the page templates
    # templates for each of the pages to test

    def _getBackupTests(self):
        tests = sorted(filter(lambda x: not x.startswith(".") and os.path.isdir(
            rdw_helpers.joinPaths(self.destRoot, x)), os.listdir(self.destRoot)))
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
        self.destRoot = rdw_helpers.joinPaths(
            os.path.realpath(tempfile.gettempdir()), "rdiffweb")
        self.masterDirPath = os.path.realpath("tests")
        self.tearDown()

        # Copy and set up each test
        self._copyDirWithoutSvn(self.masterDirPath, self.destRoot)

    def tearDown(self):
        if (os.access(self.destRoot, os.F_OK)):
            rdw_helpers.removeDir(self.destRoot)
