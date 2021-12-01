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
import cherrypy

SESSION_KEY = '_cp_username'


def get_currentuser(session_key=SESSION_KEY):
    """
    When session is enabled and user is authenticated, get the
    current user object and store it into the session.
    """
    # Check if session is enabled
    sessions_on = cherrypy.request.config.get('tools.sessions.on', False)
    if not sessions_on:
        return
    # Check if user is authenticated
    username = cherrypy.session.get(session_key)
    if not username:
        return
    # Get reference to current user object
    app = cherrypy.request.app
    userobj = app.store.get_user(username)  # @UndefinedVariable
    if not userobj:
        # User was deleted after authenticating.
        raise cherrypy.HTTPError(403)
    cherrypy.serving.request.login = userobj.username
    cherrypy.serving.request.currentuser = userobj


cherrypy.tools.currentuser = cherrypy.Tool('before_handler', get_currentuser, priority=73)
