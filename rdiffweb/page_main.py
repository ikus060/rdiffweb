#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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
import os.path

import db
import rdw_templating
from rdw_helpers import encode_s, decode_s

# Define the logger
logger = logging.getLogger(__name__)


class rdiffPage:

    # HELPER FUNCTIONS #

    def validate_user_path(self, path_b):
        '''Takes a path relative to the user's root dir and validates that it
        is valid and within the user's root'''
        assert isinstance(path_b, str)
        path_b = path_b.strip(b"/")+b"/"

        # NOTE: a blank path is allowed, since the user root directory might be
        # a repository.

        logger.debug("check user access to path [%s]" %
                     decode_s(path_b, 'replace'))

        # Get reference to user repos
        user_repos = self.getUserDB().get_repos(self.getUsername())

        # Check if any of the repos matches the given path.
        user_repos_matches = filter(
            lambda x: path_b.startswith(encode_s(x).strip(b"/")+b"/"),
            user_repos)
        if not user_repos_matches:
            # No repo matches
            logger.error("user doesn't have access to [%s]" %
                         decode_s(path_b, 'replace'))
            raise librdiff.AccessDeniedError
        repo_b = encode_s(user_repos_matches[0]).strip(b"/")

        # Get reference to user_root
        user_root = self.getUserDB().get_root_dir(self.getUsername())
        user_root_b = encode_s(user_root)

        # Check path vs real path value
        full_path_b = os.path.join(user_root_b, path_b).rstrip(b"/")
        real_path_b = os.path.realpath(full_path_b).rstrip(b"/")
        if full_path_b != real_path_b:
            # We can safely assume the realpath contains a symbolic link. If
            # the symbolic link is valid, we display the content of the "real"
            # path.
            if real_path_b.startswith(os.path.join(user_root_b, repo_b)):
                path_b = os.path.relpath(real_path_b, user_root_b)
            else:
                logger.warn("access is denied [%s] vs [%s]" % (
                    decode_s(full_path_b, 'replace'),
                    decode_s(real_path_b, 'replace')))
                raise librdiff.AccessDeniedError

        # Get reference to the repository (this ensure the repository does
        # exists and is valid.)
        repo_obj = librdiff.RdiffRepo(user_root_b, repo_b)

        # Get reference to the path.
        path_b = path_b[len(repo_b):]
        path_obj = repo_obj.get_path(path_b)

        return (repo_obj, path_obj)

    def getUserDB(self):
        """Return the user database."""
        return db.userDB().get_userdb_module()

    # PAGE HELPER FUNCTIONS #

    def _is_submit(self):
        return cherrypy.request.method == "POST"

    def _writeErrorPage(self, error):
        assert isinstance(error, unicode)
        return self._writePage("error.html", error=error)

    def _writePage(self, template_name, **kwargs):
        """Used to generate a standard html page using the given template.
        This method should be used by subclasses to provide default template
        value."""
        parms = {"is_login": True,
                 "is_admin": self._user_is_admin(),
                 "username": self.getUsername()}
        parms.update(kwargs)
        return rdw_templating.compile_template(template_name, **parms)

    # SESSION INFORMATION #
    def checkpassword(self, username, password):
        # Check credential using local database.
        if self.getUserDB().are_valid_credentials(username, password):
            cherrypy.session['username'] = username  # @UndefinedVariable
            return None
        return "Invalid username or password."

    def getUsername(self):
        try:
            return cherrypy.session['username']  # @UndefinedVariable
        except:
            return None

    def setUsername(self, username):
        """Store the username in the user session."""
        cherrypy.session['username'] = username  # @UndefinedVariable

    def _user_is_admin(self):
        """Check if current user is administrator. Return True or False."""
        if self.getUsername():
            return self.getUserDB().is_admin(self.getUsername())
        return False
