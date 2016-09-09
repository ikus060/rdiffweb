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
from builtins import str
import cherrypy
from cherrypy._cpcompat import base64_decode
from cherrypy._cptools import HandlerTool
from future.utils import native_str
import logging

from rdiffweb.core import RdiffError, RdiffWarning
from rdiffweb.i18n import ugettext as _
from rdiffweb.page_main import MainPage
from rdiffweb.rdw_helpers import quote_url


# Define the logger
logger = logging.getLogger(__name__)


class AuthFormTool(HandlerTool):
    """
    Tool used to control authentication to various ressources.
    """
    session_key = 'user'

    def __init__(self):
        HandlerTool.__init__(self, self.run, name='authform')
        # Make sure to run after session tool (priority 50)
        # Make sure to run after i18n tool (priority 60)
        self._priority = 70

    def check_username_and_password(self, username, password):
        """Validate user credentials."""
        logger.debug("check credentials for [%s]", username)
        try:
            userobj = cherrypy.request.app.userdb.login(username, password)  # @UndefinedVariable
        except:
            logger.exception("fail to validate user credential.",)
            raise RdiffWarning(_("Fail to validate user credential."))
        if not userobj:
            logger.warning("invalid username or password")
            raise RdiffWarning(_("Invalid username or password."))
        return userobj

    def do_check(self):
        """Assert username. Raise redirect, or return True if request handled."""
        request = cherrypy.serving.request
        response = cherrypy.serving.response

        if not self.is_login():
            url = cherrypy.url(qs=request.query_string)

            # If browser requesting text/plain. It's probably an Ajax call, don't
            # redirect and raise an exception.
            mtype = cherrypy.tools.accept.callable(['text/html', 'text/plain'])  # @UndefinedVariable
            if mtype == 'text/plain':
                logger.debug('No username, requesting plain text, routing to 403 error from_page %(url)r', locals())
                raise cherrypy.HTTPError(403, _("Not logged in"))

            logger.debug('No username, routing to login_screen with from_page %(url)r', locals())
            response.body = self.login_screen(url)
            if "Content-Length" in response.headers:
                # Delete Content-Length header so finalize() recalcs it.
                del response.headers["Content-Length"]
            return True

        # Define the value of request.login to later in code we can reuse it.
        username = cherrypy.session[self.session_key]  # @UndefinedVariable
        userobj = cherrypy.request.app.userdb.get_user(username)  # @UndefinedVariable
        if not userobj:
            raise cherrypy.HTTPError(403)
        logger.debug('Setting request.login to %r', userobj)
        cherrypy.serving.request.login = userobj

    def do_login(self, login, password, redirect=b'/', **kwargs):
        """Login. May raise redirect, or return True if request handled."""
        response = cherrypy.serving.response
        try:
            userobj = self.check_username_and_password(login, password)
        except RdiffError as e:
            body = self.login_screen(redirect, login, str(e))
            response.body = body
            if "Content-Length" in response.headers:
                # Delete Content-Length header so finalize() recalcs it.
                del response.headers["Content-Length"]
            return True
        # User successfully login.
        logger.debug('Setting request.login to %r', userobj)
        cherrypy.serving.request.login = userobj
        cherrypy.session[self.session_key] = userobj.username  # @UndefinedVariable
        self.on_login(userobj.username)
        logger.debug('Redirect user to %r', redirect or b"/")
        raise cherrypy.HTTPRedirect(redirect or b"/")

    def do_logout(self, redirect=b'/', **kwargs):
        """Logout. May raise redirect, or return True if request handled."""
        sess = cherrypy.session  # @UndefinedVariable
        username = sess.get(self.session_key)
        sess[self.session_key] = None
        cherrypy.serving.request.login = None
        if username:
            self.on_logout(username)
        raise cherrypy.HTTPRedirect(redirect)

    def is_login(self):
        """Validate if the current user session is login."""
        username = cherrypy.session.get(self.session_key)  # @UndefinedVariable
        return username is not None

    def login_screen(self, redirect=b'/', username='', error_msg='', **kwargs):
        app = cherrypy.request.app
        main_page = MainPage(app)

        # Re-encode the redirect for display in HTML
        redirect = quote_url(redirect, safe=";/?:@&=+$,%")

        params = {
            'redirect': redirect,
            'login': username,
            'warning': error_msg
        }

        # Add welcome message to params. Try to load translated message.
        params["welcome_msg"] = app.cfg.get_config("WelcomeMsg")
        if hasattr(cherrypy.response, 'i18n'):
            lang = cherrypy.response.i18n._lang
            params["welcome_msg"] = app.cfg.get_config("WelcomeMsg[%s]" % (lang), params["welcome_msg"])

        return main_page._compile_template("login.html", **params).encode("utf-8")

    def on_login(self, username):
        """Called when user is login."""
        pass

    def on_logout(self, username):
        """Called when user is logout."""
        pass

    def run(self):
        """Called to execute this tool."""
        request = cherrypy.serving.request
        response = cherrypy.serving.response

        path = request.path_info
        if path.startswith(native_str('/login')):
            if request.method != 'POST':
                response.headers['Allow'] = "POST"
                logger.info('do_login requires POST')
                # Redirect to / instead of showing error.
                raise cherrypy.HTTPRedirect(b'/')
            logger.info('routing %(path)r to do_login', locals())
            return self.do_login(**request.params)

        elif path.startswith(native_str('/logout')):
            logger.info('routing %(path)r to do_logout', locals())
            return self.do_logout(**request.params)

        # No special path, validate session.
        logger.info('No special path, running do_check')
        return self.do_check()


cherrypy.tools.authform = AuthFormTool()


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
