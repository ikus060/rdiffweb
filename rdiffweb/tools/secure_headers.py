# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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

import http.cookies
import logging

import cherrypy

# Define the logger
logger = logging.getLogger(__name__)

#
# Patch Morsel prior to 3.8
# Allow SameSite attribute to be define on the cookie.
#
if not http.cookies.Morsel().isReservedKey("samesite"):
    http.cookies.Morsel._reserved['samesite'] = 'SameSite'


def set_headers():
    """
    This tool provide CSRF mitigation.

    * Define X-Frame-Options = DENY
    * Define Cookies SameSite=Lax
    * Define Cookies Secure when https is detected
    * Validate `Origin` and `Referer` on POST, PUT, PATCH, DELETE

    Ref.:
    https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
    https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
    """
    if cherrypy.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        # Check if Origin matches our target.
        origin = cherrypy.request.headers.get('Origin', None)
        if origin and not origin.startswith(cherrypy.request.base):
            raise cherrypy.HTTPError(403, 'Unexpected Origin header')

    response = cherrypy.serving.response
    # Define X-Frame-Options to avoid Clickjacking
    response.headers['X-Frame-Options'] = 'DENY'

    # Enforce security on cookies
    cookie = response.cookie.get('session_id', None)
    if cookie:
        # Awaiting bug fix in cherrypy
        # https://github.com/cherrypy/cherrypy/issues/1767
        # Force SameSite to Lax
        cookie['samesite'] = 'Lax'
        # Check if https is enabled
        https = cherrypy.request.base.startswith('https')
        if https:
            cookie['secure'] = 1


cherrypy.tools.secure_headers = cherrypy.Tool('before_request_body', set_headers, priority=71)
