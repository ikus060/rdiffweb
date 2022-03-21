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
import base64

import cherrypy

SESSION_KEY = '_cp_username'

# Monkey patch cherrypy base64 calls
base64.decodestring = base64.b64decode


def basic_auth(realm, checkpassword, debug=False, session_key=SESSION_KEY):
    """
    Tool supporting basic authentication but also support session authentication.
    If user is already authenticated, this tools will let him in.
    """
    # When session is not enable, simply validate credentials
    sessions_on = cherrypy.request.config.get('tools.sessions.on', False)
    if not sessions_on:
        cherrypy.lib.auth_basic.basic_auth(realm, checkpassword, debug)
        return

    # When session, is enabled, let check if user is already authenticated
    username = cherrypy.session.get(session_key)
    if not username:
        # User is not authenticated.
        # Verify credential, will raise an exception if credentials are invalid.
        cherrypy.lib.auth_basic.basic_auth(realm, checkpassword, debug)
        # User is authenticated, let save this into the session.
        cherrypy.session[session_key] = cherrypy.request.login


cherrypy.tools.auth_basic = cherrypy.Tool('before_handler', basic_auth, priority=70)
