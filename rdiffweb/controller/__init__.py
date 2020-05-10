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
from collections import namedtuple

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


FlashMessage = namedtuple('FlashMessage', ['message', 'level'])


def flash(message, level='info'):
    """
    Add a flashin message to the session.
    """
    assert message
    assert level in ['info', 'error', 'warning', 'success']
    if 'flash' not in cherrypy.session:  # @UndefinedVariable
        cherrypy.session['flash'] = []  # @UndefinedVariable
    flash_message = FlashMessage(message, level)
    cherrypy.session['flash'].append(flash_message)


def get_flashed_messages():
    if 'flash' in cherrypy.session:  # @UndefinedVariable
        messages = cherrypy.session['flash']  # @UndefinedVariable
        del cherrypy.session['flash']  # @UndefinedVariable
        return messages
    return []


class Controller(object):

    _header_name = Option("HeaderName", "rdiffweb")

    _footername = Option("FooterName", "rdiffweb")

    _footerurl = Option("FooterUrl", "https://www.ikus-soft.com/en/rdiffweb/")

    _default_theme = Option("DefaultTheme", "default")

    @property
    def app(self):
        return cherrypy.request.app

    def _compile_template(self, template_name, **kwargs):
        """
        Used to generate a standard HTML page using the given template.
        This method should be used by subclasses to provide default template
        value.
        """
        loc = cherrypy.response.i18n.locale
        parms = {
            "lang": loc.language,
            "header_name" : self._header_name,
            "theme" : self._default_theme,
            "footername" : self._footername,
            "footerurl" : self._footerurl,
            "get_flashed_messages": get_flashed_messages,
        }
        if self.app.currentuser:
            parms.update({
                'username': self.app.currentuser.username,
                'is_admin': self.app.currentuser.is_admin,
                'is_maintainer': self.app.currentuser.is_maintainer,
            })

        # Append custom branding
        if hasattr(self.app.root, "header_logo"):
            parms["header_logo"] = '/header_logo'

        # Append template parameters.
        parms.update(kwargs)

        return self.app.templates.compile_template(template_name, **parms)

