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
import datetime
import time
import urllib.parse

import cherrypy
from cherrypy.lib import httputil

SESSION_KEY = '_cp_username'
LOGIN_TIME = 'login_time'
LOGIN_REDIRECT_URL = '_auth_form_redirect_url'
LOGIN_PERSISTENT = 'login_persistent'


class CheckAuthForm(cherrypy.Tool):
    def __init__(self, priority=73):
        super().__init__(point='before_handler', callable=self.run, priority=priority)

    def _is_login(self):
        """
        Verify if the login expired and we need to prompt the user to authenticated again using either credentials and/or MFA.
        """
        # Verify if current user exists
        request = cherrypy.serving.request
        if not getattr(request, 'currentuser', None):
            return False

        # Verify if session is enabled
        sessions_on = request.config.get('tools.sessions.on', False)
        if not sessions_on:
            return False

        # Verify session
        session = cherrypy.session
        return (
            session.get(SESSION_KEY) is not None
            and session.get(LOGIN_TIME) is not None
            and session[LOGIN_TIME] + datetime.timedelta(minutes=session.timeout) > session.now()
        )

    def _get_redirect_url(self):
        """
        Return the original URL the user browser before getting redirect to login.
        """
        return cherrypy.session.get(LOGIN_REDIRECT_URL) or '/'

    def _set_redirect_url(self):
        # Keep reference to the current URL
        request = cherrypy.serving.request
        uri_encoding = getattr(request, 'uri_encoding', 'utf-8')
        original_url = urllib.parse.quote(request.path_info, encoding=uri_encoding)
        qs = request.query_string
        new_url = cherrypy.url(original_url, qs=qs, base='')
        cherrypy.session[LOGIN_REDIRECT_URL] = new_url

    def redirect_to_original_url(self):
        # Redirect user to original URL
        raise cherrypy.HTTPRedirect(self._get_redirect_url())

    def run(self, login_url='/login/', logout_url='/logout', timeout=43200):
        """
        A tool that verify if the session is associated to a user by tracking
        a session key. If session is not authenticated, redirect user to login page.
        """
        request = cherrypy.serving.request
        # Skip execution of this tools when browsing the login page.
        if request.path_info == login_url:
            if self._is_login():
                raise cherrypy.HTTPRedirect('/')
            return

        # Clear session when browsing /logout
        if request.path_info == logout_url or request.path_info.startswith(logout_url):
            self.logout()
            raise cherrypy.HTTPRedirect('/')

        # Check if login
        if not self._is_login():
            # Store original URL
            self._set_redirect_url()
            # And redirect to login page
            raise cherrypy.HTTPRedirect(login_url)

        # If login is persistent, update the cookie max-age/expires
        if cherrypy.session.get(LOGIN_PERSISTENT, False):
            cherrypy.session.timeout = timeout
            cookie = cherrypy.serving.response.cookie
            cookie['session_id']['max-age'] = timeout * 60
            cookie['session_id']['expires'] = httputil.HTTPDate(time.time() + timeout * 60)
        else:
            session_timeout = cherrypy.request.config.get('tools.sessions.timeout', 60)
            cherrypy.session.timeout = session_timeout

    def login(self, username, persistent=False):
        """
        Must be called by the page hanlder when the authentication is successful.
        """
        # Store session data
        cherrypy.session[LOGIN_PERSISTENT] = persistent
        cherrypy.session[SESSION_KEY] = username
        cherrypy.session[LOGIN_TIME] = cherrypy.session.now()
        # Generate a new session id
        cherrypy.session.regenerate()

    def logout(self):
        # Clear session date and generate a new session id
        cherrypy.session.clear()
        cherrypy.session.regenerate()


cherrypy.tools.auth_form = CheckAuthForm()
