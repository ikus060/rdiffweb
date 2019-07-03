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

from builtins import bytes
import logging

import cherrypy
from future.utils.surrogateescape import encodefilename
from rdiffweb.core.config import Option
from rdiffweb.core.librdiff import RdiffRepo


# Define the logger
logger = logging.getLogger(__name__)


def validate(value, message=None):
    """Raise HTTP error if value is not true."""
    if not value:
        raise cherrypy.HTTPError(400, message)


def validate_int(value, message=None):
    """Raise HTTP Error if the value is not an integer"""
    try:
        return int(value)
    except:
        raise cherrypy.HTTPError(400, message)


def validate_isinstance(value, cls, message=None):
    """Raise HTTP error if value is not cls."""
    if not isinstance(value, cls):
        raise cherrypy.HTTPError(400, message)


class Controller(object):

    _header_name = Option("HeaderName", "rdiffweb")
    
    _default_theme = Option("DefaultTheme", "default")

    @property
    def app(self):
        return cherrypy.request.app
    
    @property
    def currentuser(self):
        """
        Get the current user.
        """
        return cherrypy.serving.request.login
    
    def _compile_template(self, template_name, **kwargs):
        """
        Used to generate a standard HTML page using the given template.
        This method should be used by subclasses to provide default template
        value.
        """
        loc = cherrypy.response.i18n.locale
        parms = {
            "lang": loc.language,
        }
        if self.currentuser:
            parms.update({
                "is_login": False,
                'username': self.currentuser.username,
                'is_admin': self.currentuser.is_admin,
            })

        # Append custom branding
        if hasattr(self.app.root, "header_logo"):
            parms["header_logo"] = '/header_logo'
        parms["header_name"] = self._header_name
        parms["theme"] = self._default_theme

        # Append template parameters.
        parms.update(kwargs)

        return self.app.templates.compile_template(template_name, **parms)
    
    def _is_submit(self):
        """
        Check if the cherrypy request is a POST.
        """
        return cherrypy.request.method == "POST"
    