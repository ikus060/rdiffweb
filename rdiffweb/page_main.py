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
from __future__ import absolute_import

import cherrypy
from rdiffweb import librdiff
import logging
import os.path

from rdiffweb.rdw_helpers import encode_s, decode_s
from rdiffweb.core import Component
from rdiffweb.rdw_plugin import ITemplateFilterPlugin

# Define the logger
logger = logging.getLogger(__name__)


class MainPage(Component):

    def validate_user_path(self, path_b):
        '''Takes a path relative to the user's root dir and validates that it
        is valid and within the user's root'''
        assert isinstance(path_b, str)

        # Add a ending slash (/) to avoid matching wrong repo. Ref #56
        path_b = path_b.strip(b'/') + b'/'

        # NOTE: a blank path is allowed, since the user root directory might be
        # a repository.

        logger.debug("check user access to path [%s]" %
                     decode_s(path_b, 'replace'))

        # Get reference to user repos
        user_repos = self.app.currentuser.repos

        # Check if any of the repos matches the given path.
        user_repos_matches = [
            encode_s(user_repo).strip(b'/')
            for user_repo in user_repos
            if path_b.startswith(encode_s(user_repo).strip(b'/') + b'/')]
        if not user_repos_matches:
            # No repo matches
            logger.error("user doesn't have access to [%s]" %
                         decode_s(path_b, 'replace'))
            raise librdiff.AccessDeniedError
        repo_b = user_repos_matches[0]

        # Get reference to user_root
        user_root_b = encode_s(self.app.currentuser.root_dir)

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

    def _is_submit(self):
        """
        Check if the cherrypy request is a POST.
        """
        return cherrypy.request.method == "POST"

    def _compile_error_template(self, error):
        """
        Compile an error template.
            `error` the error message.
        """
        assert isinstance(error, unicode)
        return self._compile_template("error.html", error=error)

    def _compile_template(self, template_name, **kwargs):
        """
        Used to generate a standard HTML page using the given template.
        This method should be used by subclasses to provide default template
        value.
        """
        parms = {
            "is_login": True,
            "version": self.app.get_version(),
        }
        if self.app.currentuser:
            parms['username'] = self.app.currentuser.username
            parms['is_admin'] = self.app.currentuser.is_admin

        # Append custom branding
        if hasattr(self.app, "favicon"):
            parms["favicon"] = self.app.favicon  # See main,py
        if hasattr(self.app, "header_logo"):
            parms["header_logo"] = self.app.header_logo  # See main,py
        header_name = self.app.cfg.get_config("HeaderName")
        if header_name:
            parms["header_name"] = header_name

        # Append template parameters.
        parms.update(kwargs)

        # Filter params using plugins
        self.app.plugins.run(
            lambda x: x.filter_data(template_name, parms),
            category=ITemplateFilterPlugin.CATEGORY)

        return self.app.templates.compile_template(template_name, **parms)
