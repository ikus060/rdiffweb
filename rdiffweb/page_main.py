#!/usr/bin/python
# -*- coding: utf-8 -*-
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

from __future__ import unicode_literals

import cherrypy
import urllib
import os.path

from . import db
from . import rdw_templating
from . import rdw_helpers
from . import rdw_config


class rdiffPage:

    # HELPER FUNCTIONS #

    def validateUserPath(self, path):
        '''Takes a path relative to the user's root dir and validates that it is valid and within the user's root'''
        path = rdw_helpers.os_path_join(self.getUserDB().getUserRoot(
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
        assert isinstance(error, unicode)
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
