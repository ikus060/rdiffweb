#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

import base64
import binascii
import logging

from builtins import str
import cherrypy
from cherrypy._cptools import HandlerTool
from future.utils import native_str

from rdiffweb.controller import Controller
from rdiffweb.core import RdiffError, RdiffWarning
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.rdw_helpers import quote_url
from rdiffweb.core.config import Option

# Define the logger
logger = logging.getLogger(__name__)


def base64_decode(params):
    bytes_params = base64.b64decode(params.encode('ascii'))
    decoded_params = bytes_params.decode('ascii', errors='replace')
    for e in ['utf-8', 'ISO-8859-1']:
        try:
            decoded_params = bytes_params.decode(e)
            break
        except ValueError:
            pass
    return decoded_params


class BaseAuth(HandlerTool):

    session_key = 'user'

    def check_username_and_password(self, username, password):
        """Validate user credentials."""
        logger.debug("check credentials for [%s]", username)
        try:
            userobj = cherrypy.request.app.userdb.login(username, password)  # @UndefinedVariable
        except:
            logger.exception("fail to validate user credential")
            raise RdiffWarning(_("Fail to validate user credential."))
        if not userobj:
            logger.warning("invalid username [%s] or password", username)
            raise RdiffWarning(_("Invalid username or password."))
        return userobj

    def do_login(self, login, password, **kwargs):
        """Login. May raise redirect, or return True if request handled."""
        # Validate username password. Raise an exception if invalid.
        userobj = self.check_username_and_password(login, password)
        # User successfully login.
        logger.debug('setting request.login to %s', userobj)
        cherrypy.serving.request.login = userobj
        cherrypy.session[self.session_key] = userobj.username  # @UndefinedVariable
        self.on_login(userobj.username)
        return True

    def do_logout(self, **kwargs):
        """Logout. Return True if request handled."""
        sess = cherrypy.session  # @UndefinedVariable
        username = sess.get(self.session_key)
        sess[self.session_key] = None
        cherrypy.serving.request.login = None
        if username:
            self.on_logout(username)
        return True

    def is_login(self):
        """Validate if the current user session is login."""
        username = cherrypy.session.get(self.session_key)  # @UndefinedVariable
        if not username:
            return False
        userobj = cherrypy.request.app.userdb.get_user(username)  # @UndefinedVariable
        if not userobj:
            return False
        logger.debug('setting request.login to %s', userobj)
        cherrypy.serving.request.login = userobj
        return userobj

    def on_login(self, username):
        """Called when user is login."""
        pass

    def on_logout(self, username):
        """Called when user is logout."""
        pass


class AuthFormTool(BaseAuth):
    """
    Tool used to control authentication to various ressources.
    """

    def __init__(self):
        BaseAuth.__init__(self, self.run, name='authform')
        # Make sure to run after session tool (priority 50)
        # Make sure to run after i18n tool (priority 60)
        self._priority = 71

    def do_check(self):
        """Assert username. Raise redirect, or return True if request handled."""
        request = cherrypy.serving.request
        response = cherrypy.serving.response

        if not self.is_login():
            url = cherrypy.url(qs=request.query_string)
            logger.debug('no username, routing to login_screen with from_page %(url)r', locals())
            response.body = LoginPage().index(url)
            if "Content-Length" in response.headers:
                # Delete Content-Length header so finalize() recalcs it.
                del response.headers["Content-Length"]
            return True

    def do_login(self, login, password, redirect=b'/', **kwargs):
        """Login. May raise redirect, or return True if request handled."""
        response = cherrypy.serving.response
        try:
            super(AuthFormTool, self).do_login(login, password, **kwargs)
        except RdiffError as e:
            body = LoginPage().index(redirect, login, str(e))
            response.body = body
            if "Content-Length" in response.headers:
                # Delete Content-Length header so finalize() recalcs it.
                del response.headers["Content-Length"]
            return True
        # Redirect user.
        logger.debug('redirect user to %r', redirect or b"/")
        raise cherrypy.HTTPRedirect(redirect or b"/")

    def do_logout(self, redirect=b'/', **kwargs):
        """Logout. May raise redirect, or return True if request handled."""
        super(AuthFormTool, self).do_logout(**kwargs)
        raise cherrypy.HTTPRedirect(redirect)

    def run(self):
        """Called to execute this tool."""
        request = cherrypy.serving.request
        response = cherrypy.serving.response

        path = request.path_info
        if path.startswith(native_str('/login')):
            if request.method != 'POST':
                response.headers['Allow'] = "POST"
                logger.debug('/login requires POST, redirect to /')
                # Redirect to / instead of showing error.
                raise cherrypy.HTTPRedirect(b'/')
            logger.debug('routing %(path)r to do_login', locals())
            return self.do_login(**request.params)

        elif path.startswith(native_str('/logout')):
            logger.debug('routing %(path)r to do_logout', locals())
            return self.do_logout(**request.params)

        # No special path, validate session.
        return self.do_check()


cherrypy.tools.authform = AuthFormTool()


class BasicAuth(BaseAuth):
    """
    Tool used to control authentication to various ressources.
    """

    def __init__(self):
        BaseAuth.__init__(self, self.run, name='authbasic')
        # Make sure to run before authform (priority 71)
        self._priority = 70

    def run(self):
        """
        Filter used to restrict access to resource via HTTP basic auth.
        """

        # Proceed with basic authentication.
        request = cherrypy.serving.request
        path = request.path_info
        ah = request.headers.get('authorization')
        if ah:
            try:
                scheme, params = ah.split(' ', 1)
                if scheme.lower() == 'basic':
                    # Validate user credential.
                    login, password = base64_decode(params).split(':', 1)
                    try:
                        self.do_login(login, password)
                        # Return False to call default page handler.
                        return False
                    except RdiffError as e:
                        logger.info('basic auth fail for user: %s', login, exc_info=1)
                        raise cherrypy.HTTPError(403)

            except (ValueError, binascii.Error):
                raise cherrypy.HTTPError(400, 'Bad Request')

        logger.debug('no authorization header, running is_login')
        if not self.is_login():
            # Inform the user-agent this path is protected.
            cherrypy.serving.response.headers['www-authenticate'] = (
                'Basic realm="%s"%s' % ('rdiffweb', 'utf-8')
            )
            raise cherrypy.HTTPError(401, "You are not authorized to access that resource")


cherrypy.tools.authbasic = BasicAuth()


class LoginPage(Controller):
    """
    This page is used by the authentication to display enter a user/pass.
    """
    
    _welcome_msg = Option("WelcomeMsg")
    
    def index(self, redirect=b'/', username='', error_msg='', **kwargs):
        # Re-encode the redirect for display in HTML
        redirect = quote_url(redirect, safe=";/?:@&=+$,%")

        params = {
            'redirect': redirect,
            'login': username,
            'warning': error_msg
        }

        # Add welcome message to params. Try to load translated message.
        params["welcome_msg"] = self._welcome_msg
        if hasattr(cherrypy.response, 'i18n'):
            lang = cherrypy.response.i18n.locale.language
            params["welcome_msg"] = Option("WelcomeMsg[%s]" % (lang), default=params["welcome_msg"]).get()

        return self._compile_template("login.html", **params).encode("utf-8")
