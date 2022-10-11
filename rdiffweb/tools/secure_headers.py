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


def set_headers(
    xfo='DENY',
    no_cache=True,
    referrer='same-origin',
    nosniff=True,
    xxp='1; mode=block',
    csp="default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'",
):
    """
    This tool provide CSRF mitigation.

    * Define X-Frame-Options = DENY
    * Define Cookies SameSite=Lax
    * Define Cookies Secure when https is detected
    * Validate `Origin` and `Referer` on POST, PUT, PATCH, DELETE
    * Define Cache-Control by default
    * Define Referrer-Policy to 'same-origin'

    Ref.:
    https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
    https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html
    """
    request = cherrypy.request
    response = cherrypy.serving.response

    # Check if Origin matches our target.
    if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
        origin = request.headers.get('Origin', None)
        if origin and origin != request.base:
            raise cherrypy.HTTPError(403, 'Unexpected Origin header')

    # Check if https is enabled
    https = request.base.startswith('https')

    # Define X-Frame-Options to avoid Clickjacking
    if xfo:
        response.headers['X-Frame-Options'] = xfo

    # Enforce security on cookies
    cookie = response.cookie.get('session_id', None)
    if cookie:
        # Awaiting bug fix in cherrypy
        # https://github.com/cherrypy/cherrypy/issues/1767
        # Force SameSite to Lax
        cookie['samesite'] = 'Lax'
        if https:
            cookie['secure'] = 1

    # Add Cache-Control to avoid storing sensible information in Browser cache.
    if no_cache:
        response.headers['Cache-control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'

    # Add Referrer-Policy
    if referrer:
        response.headers['Referrer-Policy'] = referrer

    # Add X-Content-Type-Options to avoid browser to "sniff" to content-type
    if nosniff:
        response.headers['X-Content-Type-Options'] = 'nosniff'

    # Add X-XSS-Protection to enabled XSS protection
    if xxp:
        response.headers['X-XSS-Protection'] = xxp

    # Add Content-Security-Policy
    if csp:
        response.headers['Content-Security-Policy'] = csp

    # Add Strict-Transport-Security to force https use.
    if https:
        response.headers['Strict-Transport-Security'] = "max-age=31536000; includeSubDomains"


cherrypy.tools.secure_headers = cherrypy.Tool('before_request_body', set_headers, priority=71)
