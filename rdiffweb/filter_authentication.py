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

import binascii
import cherrypy
from cherrypy._cpcompat import base64_decode
from cherrypy._cperror import HTTPError
from future.utils import native_str
import logging

from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_helpers import quote_url


# Define the logger
logger = logging.getLogger(__name__)


def authform():

    """Filter used to redirect user to login page if not logged in."""

    # Check if logged-in.
    if cherrypy.session.get("user"):  # @UndefinedVariable
        # page passes credentials; allow to be processed
        return False

    # If browser requesting text/plain. It's probably an Ajax call, don't
    # redirect and raise an exception.
    mtype = cherrypy.tools.accept.callable(['text/html', 'text/plain'])  # @UndefinedVariable
    if mtype == 'text/plain':
        raise HTTPError(403, _("Not logged in"))

    # Sending the redirect URL
    redirect = cherrypy.request.path_info
    if cherrypy.request.query_string:
        redirect = redirect + native_str("?") + cherrypy.request.query_string
    redirect = native_str("?redirect=") + quote_url(redirect)

    # write login page
    logger.debug("user not logged in, redirect to /login/")
    raise cherrypy.HTTPRedirect(native_str("/login/") + redirect)

cherrypy.tools.authform = cherrypy._cptools.HandlerTool(authform)


def authbasic(checkpassword):

    """Filter used to restrict access to resource via HTTP basic auth."""

    # Check if logged-in.
    if cherrypy.session.get("user"):  # @UndefinedVariable
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
                error_msg = checkpassword(username, password)
                if error_msg:
                    logger.info('basic auth fail for %s: %s', username, error_msg)
                else:
                    logger.info('basic auth succeeded for %s', username)
                    request.login = username
                    return  # successful authentication
        # split() error, base64.decodestring() error
        except (ValueError, binascii.Error):
            raise cherrypy.HTTPError(400, 'Bad Request')

    # Respond with 401 status and a WWW-Authenticate header
    cherrypy.serving.response.headers['www-authenticate'] = 'Basic realm="rdiffweb"'
    raise cherrypy.HTTPError(401, "You are not authorized to access that resource")

cherrypy.tools.authbasic = cherrypy._cptools.HandlerTool(authbasic)
