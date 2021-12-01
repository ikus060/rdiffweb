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
from cherrypy._cptools import HandlerTool

# Define the logger
logger = logging.getLogger(__name__)

#
# Patch Morsel prior to 3.8
# Allow SameSite attribute to be define on the cookie.
#
if not http.cookies.Morsel().isReservedKey("samesite"):
    http.cookies.Morsel._reserved['samesite'] = 'SameSite'


class CsrfAuth(HandlerTool):
    """
    This tool provide CSRF mitigation.

    First, by defining `SameSite=Lax` on the cookie
    Second by validating the `Origin` and `Referer`.

    Ref.: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html
    """

    def __init__(self):
        HandlerTool.__init__(self, self.run, name='csrf')
        # Make sure to run before authform (priority 71)
        self._priority = 71

    def _setup(self):
        cherrypy.request.hooks.attach('before_finalize', self._set_same_site)
        return super()._setup()

    def _set_same_site(self):
        # Awaiting bug fix in cherrypy
        # https://github.com/cherrypy/cherrypy/issues/1767
        # Force SameSite to Lax
        cookie = cherrypy.serving.response.cookie.get('session_id', None)
        if cookie:
            cookie['samesite'] = 'Lax'

    def run(self):
        if cherrypy.request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            # Check if Origin matches our target.
            origin = cherrypy.request.headers.get('Origin', None)
            if origin and not origin.startswith(cherrypy.request.base):
                raise cherrypy.HTTPError(403, 'Unexpected Origin header')


cherrypy.tools.csrf = CsrfAuth()
