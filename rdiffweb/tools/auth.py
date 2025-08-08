# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging
import urllib.parse

import cherrypy

DEFAULT_REDIRECT = "/login/"

DEFAULT_SESSION_KEY = "_auth_session_key"

ORIGINAL_URL = '_auth_original_url'

logger = logging.getLogger(__name__)


def _get_current_url():
    """
    Get reference to current URL.
    """
    request = cherrypy.serving.request
    uri_encoding = getattr(request, 'uri_encoding', 'utf-8')
    original_url = urllib.parse.quote(request.path_info, encoding=uri_encoding)
    qs = request.query_string
    return cherrypy.url(original_url, qs=qs, base='')


class AuthManager(cherrypy.Tool):
    """
    This tools handle authentication of users.
    """

    def __init__(self):
        super().__init__(point='before_handler', callable=self._restore_from_session, priority=70)

    def _setup(self):
        cherrypy.Tool._setup(self)
        # Attach additional hooks as different priority to update preferred lang with more accurate preferences.
        conf = self._merged_args()
        conf.pop('priority', None)
        cherrypy.serving.request.hooks.attach('before_handler', self._forbidden_or_redirect, priority=74, **conf)

    def _restore_from_session(self, session_user_key=DEFAULT_SESSION_KEY, **kwargs):
        """
        Run early, let try to "authenticate" the user by restoring information from session.
        """
        # Verify if session is enabled, if not the user is not authenticated.
        if not hasattr(cherrypy.serving, 'session'):
            return
        # Check if a username is stored in session.
        login = cherrypy.serving.session.get(session_user_key)
        if not login:
            return
        cherrypy.serving.request.login = login

    def _forbidden_or_redirect(self, userobj_func, redirect=DEFAULT_REDIRECT, **kwargs):
        """
        If we reach this point, the user is not authenticated. Raise a 403 Forbidden or redirect the user.
        """
        # Do nothing if user request the login page.
        if cherrypy.serving.request.path_info == redirect:
            return

        # Previous hooks should define 'login'. If not we raise Error 403.
        login = getattr(cherrypy.serving.request, 'login', False)
        if login:
            # Query user object
            currentuser = userobj_func(login, None)
            if currentuser:
                cherrypy.serving.request.currentuser = currentuser
                return

        # Determine which exception need to be raised.
        if redirect:
            self.save_original_url()
            raise cherrypy.HTTPRedirect(redirect)
        raise cherrypy.HTTPError(403)

    def login_with_credentials(self, login, password):
        """
        Delegate validation of username password to authenticate plugins.
        If valid, let the user login.
        """
        if not login or not password:
            logger.warning('empty login or password provided')
            return None
        # Validate credentials using checkpassword function(s).
        conf = self._merged_args()
        checkpassword = conf.get('checkpassword')
        if not isinstance(checkpassword, (list, tuple)):
            checkpassword = [checkpassword]
        for func in checkpassword:
            try:
                valid = func(login, password)
                if not valid:
                    continue
                # Support various return value: tuple, string with username, boolean value
                if isinstance(valid, (list, tuple)) and len(valid) >= 2:
                    login, user_info = valid
                elif isinstance(valid, str):
                    login, user_info = valid, None
                else:
                    login, user_info = login, None
                # If authentication is successful, initiate login process.
                return self.login_with_result(
                    login=login,
                    user_info=user_info,
                )
            except Exception as e:
                logger.exception(
                    'unexpected error during authentication for [%s] with [%s]: %s', login, func.__qualname__, e
                )
        return None

    def login_with_result(self, login=None, user_info={}, auth_method='password'):
        """
        Could be called directly to authentication user.
        """
        conf = self._merged_args()
        userobj_func = conf.get('userobj_func')
        session_user_key = conf.get('session_user_key', DEFAULT_SESSION_KEY)

        # Get or create user object - this function should handle both username and email lookups
        userobj = userobj_func(login=login, user_info=user_info)
        if not userobj:
            logger.warning('failed to get/create user object for login=%s', login)
            return None

        # Notify plugins about user login
        cherrypy.engine.publish('user_login', userobj)

        # Store data into session
        username = getattr(userobj, 'username', login)
        if hasattr(cherrypy.serving, 'session'):
            session = cherrypy.serving.session
            session[session_user_key] = username
            session['auth_method'] = auth_method
            # Generate a new session id
            session.regenerate()

        # When authenticated, store current login name in request.
        cherrypy.serving.request.login = username

        return userobj

    def clear_login_identity(self):
        """
        Clear the login information, and generate a new session id.
        """
        conf = self._merged_args()
        session_user_key = conf.get('session_user_key', DEFAULT_SESSION_KEY)
        session = cherrypy.serving.session
        session.pop(session_user_key, None)
        session.regenerate()

    def clear_session(self):
        """
        Clear session data and generate a new session id.
        """
        session = cherrypy.serving.session
        session.clear()
        session.regenerate()

    def get_original_url(self):
        """
        Return the original URL browsed by the user before authentication.
        """
        return cherrypy.serving.session.get(ORIGINAL_URL)

    def redirect_to_original_url(self):
        # Redirect user to original URL
        redirect_url = self.get_original_url() or '/'
        return cherrypy.HTTPRedirect(redirect_url)

    def save_original_url(self):
        """
        Save the current URL to user's session.
        """
        session = cherrypy.serving.session
        session[ORIGINAL_URL] = _get_current_url()

    def redirect_to_form_url(self):
        """
        Called to redirect user to login form.
        """
        conf = self._merged_args()
        # Store original URL in user session.
        redirect = conf.get('redirect', DEFAULT_REDIRECT)
        return cherrypy.HTTPRedirect(redirect)


cherrypy.tools.auth = AuthManager()
