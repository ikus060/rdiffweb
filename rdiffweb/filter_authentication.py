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

import binascii
import cherrypy
import logging

from cherrypy._cpcompat import base64_decode

from rdw_helpers import quote_url

# Define the logger
logger = logging.getLogger(__name__)


def authform():

    """Filter used to redirect user to login page if not logged in."""

    # Check if logged-in.
    if cherrypy.session.get("username"):  # @UndefinedVariable
        # page passes credentials; allow to be processed
        return False

    # Sending the redirect URL as bytes
    redirect = cherrypy.request.path_info
    if cherrypy.request.query_string:
        redirect += b"?"
        redirect += cherrypy.request.query_string
    redirect = "?redirect=" + quote_url(redirect)

    # write login page
    logger.info("user not logged in, redirect to /login/")
    raise cherrypy.HTTPRedirect("/login/" + redirect)

cherrypy.tools.authform = cherrypy._cptools.HandlerTool(authform)


def authbasic(checkpassword, authmethod=""):

    """Filter used to restrict access to resource via HTTP basic auth."""

    # Check if logged-in.
    if cherrypy.session.get("username"):  # @UndefinedVariable
        # page passes credentials; allow to be processed
        return False

    # Proceed with basic authentication.
    request = cherrypy.serving.request
    auth_header = request.headers.get('authorization')
    if auth_header is not None:
        try:
            scheme, params = auth_header.split(' ', 1)
            if scheme.lower() == 'basic':
                username, password = base64_decode(params).split(':', 1)
                if checkpassword(username, password):
                    logger.debug('Auth succeeded')
                    request.login = username
                    return  # successful authentication
        # split() error, base64.decodestring() error
        except (ValueError, binascii.Error):
            raise cherrypy.HTTPError(400, 'Bad Request')

    # Respond with 401 status and a WWW-Authenticate header
    cherrypy.serving.response.headers['www-authenticate'] = 'Basic realm="rdiffweb"'
    raise cherrypy.HTTPError(401, "You are not authorized to access that resource")

cherrypy.tools.authbasic = cherrypy._cptools.HandlerTool(authbasic)

