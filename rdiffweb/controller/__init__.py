#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

import logging
from rdiffweb.core.librdiff import RdiffRepo, DoesNotExistError

from builtins import bytes
import cherrypy
from future.utils.surrogateescape import encodefilename

# Define the logger
logger = logging.getLogger(__name__)


def validate(value, message=None):
    """Raise HTTP error if value is not true."""
    if not value:
        raise cherrypy.HTTPError(400, message)


def validate_int(value, message=None):
    """Raise HTTP Error if the value is not an integer"""
    try:
        int(value)
    except:
        raise cherrypy.HTTPError(400, message)


def validate_isinstance(value, cls, message=None):
    """Raise HTTP error if value is not cls."""
    if not isinstance(value, cls):
        raise cherrypy.HTTPError(400, message)


class Controller(object):

    @property
    def app(self):
        return cherrypy.request.app
    
    @property
    def currentuser(self):
        """
        Get the current user.
        """
        return cherrypy.serving.request.login
    
    def validate_user_path(self, path_b):
        '''
        Takes a path relative to the user's root dir and validates that it
        is valid and within the user's root.
    
        Uses bytes path to avoid any data lost in encoding/decoding.
        '''
        # NOTE: a blank path is allowed, since the user root directory might be
        # a repository.
        logger.debug("checking user access to path %r", path_b)
    
        # Query database for a matching repository.
        try:
            return self.app.currentuser.get_repo_path(path_b)
        except KeyError:
            # No repo matches
            logger.error("user doesn't have access to [%r]", path_b)
            raise DoesNotExistError(path_b)
