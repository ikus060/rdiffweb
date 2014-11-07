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
import librdiff
import logging
import urllib
import os.path

import db
import rdw_templating
import rdw_helpers
import rdw_config
from rdw_helpers import encode_s, decode_s

# Define the logger
logger = logging.getLogger(__name__)

class rdiffPage:

    # HELPER FUNCTIONS #

    def validate_user_path(self, path_b):
        '''Takes a path relative to the user's root dir and validates that it
        is valid and within the user's root'''
        assert isinstance(path_b, str)
        path_b = path_b.strip(b"/")

        # NOTE: a blank path parm is allowed, since that just results in a
        # listing of the repo root
        if not path_b:
            logger.warn("backup location not specified")
            raise rdw_helpers.accessDeniedError

        logger.debug("check user access to path [%s]" %
                     decode_s(path_b, 'replace'))

        # Get reference to user repos
        user_repos = self.getUserDB().getUserRepoPaths(self.getUsername())

        # Check if any of the repos matches the given path.
        user_repos_matches = filter(
            lambda x: path_b.startswith(encode_s(x).strip(b"/")),
            user_repos)
        if not user_repos_matches:
            # No repo matches
            logger.error("user doesn't have access to [%s]" %
                         decode_s(path_b, 'replace'))
            raise rdw_helpers.accessDeniedError
        repo_b = encode_s(user_repos_matches[0]).strip(b"/")

        # Get reference to user_root
        user_root = self.getUserDB().getUserRoot(self.getUsername())
        user_root_b = encode_s(user_root)

        # Check path vs real path value
        full_path_b = os.path.join(user_root_b, path_b)
        if full_path_b != os.path.realpath(full_path_b):
            logger.warn("access is denied")
            raise rdw_helpers.accessDeniedError

        # Get reference to the repository (this ensure the repository does
        # exists and is valid.)
        repo_obj = librdiff.RdiffRepo(user_root_b, repo_b)

        # Get reference to the path.
        path_b = path_b[len(repo_b):]
        path_obj = repo_obj.get_path(path_b)

        return (repo_obj, path_obj)

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
