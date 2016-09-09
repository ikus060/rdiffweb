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

from __future__ import absolute_import
from __future__ import unicode_literals

from builtins import bytes
import cherrypy
from future.utils.surrogateescape import encodefilename
import logging
import os.path

from rdiffweb.core import Component
from rdiffweb.i18n import get_current_lang
from rdiffweb.librdiff import RdiffRepo, AccessDeniedError, DoesNotExistError
from rdiffweb.rdw_plugin import ITemplateFilterPlugin


# Define the logger
logger = logging.getLogger(__name__)


SEP = b'/'


def normpath(val):
    "Normalize path value"
    if not val.endswith(SEP):
        val += SEP
    if val.startswith(SEP):
        val = val[1:]
    return val


class MainPage(Component):

    def assertTrue(self, value, message=None):
        """Raise HTTP error if value is not true."""
        if not value:
            raise cherrypy.HTTPError(400, message)

    def assertIsInt(self, value, message=None):
        """Raise HTTP Error if the value is not an integer"""
        try:
            int(value)
        except:
            raise cherrypy.HTTPError(400, message)

    def assertIsInstance(self, value, cls, message=None):
        """Raise HTTP error if value is not cls."""
        if not isinstance(value, cls):
            raise cherrypy.HTTPError(400, message)

    # TODO Should be moved to different location. e.g.: user.py
    def validate_user_path(self, path_b):
        '''
        Takes a path relative to the user's root dir and validates that it
        is valid and within the user's root.

        Uses bytes path to avoid any data lost in encoding/decoding.
        '''
        assert isinstance(path_b, bytes)

        # Add a ending slash (/) to avoid matching wrong repo. Ref #56
        path_b = normpath(path_b)

        # NOTE: a blank path is allowed, since the user root directory might be
        # a repository.

        logger.debug("checking user access to path %r", path_b)

        # Get reference to user repos (as bytes)
        user_repos = [
            normpath(encodefilename(r))
            for r in self.app.currentuser.repos]

        # Check if any of the repos matches the given path.
        repo_b = next((
            user_repo
            for user_repo in user_repos
            if path_b.startswith(user_repo)), None)
        if repo_b is None:
            # No repo matches
            logger.error("user doesn't have access to [%r]", path_b)
            raise cherrypy.HTTPError(404)

        # Get reference to user_root
        user_root_b = encodefilename(self.app.currentuser.user_root)

        # Check path vs real path value
        full_path_b = os.path.join(user_root_b, path_b.lstrip(b'/')).rstrip(b"/")
        real_path_b = os.path.realpath(full_path_b).rstrip(b"/")
        if full_path_b != real_path_b:
            # We can safely assume the realpath contains a symbolic link. If
            # the symbolic link is valid, we display the content of the "real"
            # path.
            if real_path_b.startswith(os.path.join(user_root_b, repo_b)):
                path_b = os.path.relpath(real_path_b, user_root_b)
            else:
                logger.warning("access is denied [%r] vs [%r]", full_path_b, real_path_b)
                raise cherrypy.HTTPError(404)

        try:
            # Get reference to the repository (this ensure the repository does
            # exists and is valid.)
            repo_obj = RdiffRepo(user_root_b, repo_b)

            # Get reference to the path.
            path_b = path_b[len(repo_b):]
            path_obj = repo_obj.get_path(path_b)

            return (repo_obj, path_obj)

        except AccessDeniedError as e:
            logger.warning("access is denied", exc_info=1)
            raise cherrypy.HTTPError(404)
        except DoesNotExistError as e:
            logger.warning("doesn't exists", exc_info=1)
            raise cherrypy.HTTPError(404)

    def _is_submit(self):
        """
        Check if the cherrypy request is a POST.
        """
        return cherrypy.request.method == "POST"

    def _compile_template(self, template_name, **kwargs):
        """
        Used to generate a standard HTML page using the given template.
        This method should be used by subclasses to provide default template
        value.
        """
        parms = {
            "lang": get_current_lang(),
            "version": self.app.get_version(),
            "extra_head_templates": [],
        }
        if self.app.currentuser:
            parms.update({
                "is_login": False,
                'username': self.app.currentuser.username,
                'is_admin': self.app.currentuser.is_admin,
            })

        # Append custom branding
        parms["header_logo"] = hasattr(self.app.root.static, "header_logo")
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
