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


def check_auth_form(login_url='/login/', session_key=SESSION_KEY):
    """
    A tool that verify if the session is associated to a user by tracking
    a session key. If session is not authenticated, redirect him to login page.
    """
    # Session is required for this tools
    username = cherrypy.session.get(session_key)
    if not username:
        redirect = cherrypy.serving.request.path_info
        query_string = cherrypy.serving.request.query_string
        if query_string:
            redirect = redirect + '?' + query_string
        new_url = cherrypy.url(login_url, qs={'redirect': redirect})
        raise cherrypy.HTTPRedirect(new_url)


cherrypy.tools.auth_form = cherrypy.Tool('before_handler', check_auth_form, priority=72)
