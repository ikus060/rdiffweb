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

import datetime
import logging
import urllib.parse

import cherrypy

AUTH_LAST_PASSWORD_AT = '_auth_last_password_at'
AUTH_METHOD = '_auth_method'
AUTH_ORIGINAL_URL = '_auth_original_url'

AUTH_DEFAULT_REDIRECT = "/login/"
AUTH_DEFAULT_SESSION_KEY = "_auth_session_key"
AUTH_DEFAULT_REAUTH_TIMEOUT = 60  # minutes


logger = logging.getLogger(__name__)


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

    # ---- Config helpers ----

    @staticmethod
    def _reauth_timeout_minutes() -> int:
        # How long until we force a full username/password re-login regardless of session timeout.
        return int(cherrypy.request.config.get('tools.auth.reauth_timeout', AUTH_DEFAULT_REAUTH_TIMEOUT))

    @staticmethod
    def _session_user_key() -> int:
        return cherrypy.request.config.get('tools.auth.session_user_key', AUTH_DEFAULT_SESSION_KEY)

    # ---- Tool entrypoints ----

    def _restore_from_session(self, **kwargs):
        """
        Run early, let try to "authenticate" the user by restoring information from session.
        """
        # Verify if session is enabled, if not the user is not authenticated.
        if not hasattr(cherrypy.serving, 'session'):
            return
        # Check if a username is stored in session.
        session = cherrypy.serving.session
        login = session.get(self._session_user_key())
        if not login:
            return

        # Check if re-auth is required.
        last = session.get(AUTH_LAST_PASSWORD_AT)
        if last is None:
            return  # never had a password login in this session
        timeout = self._reauth_timeout_minutes()
        if (last + datetime.timedelta(minutes=timeout)) < session.now():
            return

        # User is authenticated and doesn't need to re-authenticate.
        cherrypy.serving.request.login = login

    def _forbidden_or_redirect(self, userobj_func, redirect=AUTH_DEFAULT_REDIRECT, **kwargs):
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

    # ---- API for the login page handlers ----

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
        # If we reach here, authentication failed
        if hasattr(cherrypy.serving, 'session'):
            cherrypy.serving.session.regenerate()  # Prevent session analysis

        logger.warning('Failed login attempt for user=%s from ip=%s', login, cherrypy.serving.request.remote.ip)

        return None

    def login_with_result(self, login=None, user_info={}, auth_method='password'):
        """
        Could be called directly to authentication user.
        """
        conf = self._merged_args()
        userobj_func = conf.get('userobj_func')

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
            session_user_key = self._session_user_key()
            session[session_user_key] = username
            session[AUTH_METHOD] = auth_method
            session[AUTH_LAST_PASSWORD_AT] = session.now()
            # Generate a new session id
            session.regenerate()

        # When authenticated, store current login name in request.
        cherrypy.serving.request.login = username

        return userobj

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
        return cherrypy.serving.session.get(AUTH_ORIGINAL_URL)

    def get_user_key(self):
        """Return the last username."""
        if not hasattr(cherrypy.serving, 'session'):
            return False
        session = cherrypy.serving.session
        session_user_key = self._session_user_key()
        return session.get(session_user_key)

    def redirect_to_original_url(self):
        # Redirect user to original URL
        redirect_url = self.get_original_url() or '/'
        return cherrypy.HTTPRedirect(redirect_url)

    def save_original_url(self):
        """
        Save the current URL to user's session.
        """
        # Extract URL including query-string.
        request = cherrypy.serving.request
        uri_encoding = getattr(request, 'uri_encoding', 'utf-8')
        original_url = urllib.parse.quote(request.path_info, encoding=uri_encoding)
        query_string = request.query_string

        # Store value in session
        session = cherrypy.serving.session
        session[AUTH_ORIGINAL_URL] = cherrypy.url(original_url, qs=query_string, base='')


cherrypy.tools.auth = AuthManager()
