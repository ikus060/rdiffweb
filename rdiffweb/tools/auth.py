# Authentication tools for cherrypy
# Copyright (C) 2025 IKUS Software
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


class AuthManager(cherrypy.Tool):
    """
    CherryPy tool handling authentication.

    Required config:
      - tools.auth.user_lookup_func(login, user_info) -> (user_key, userobj)
      - tools.auth.user_from_key_func(user_key) -> userobj | None
      - tools.auth.checkpassword: callable or list of callables (login, password) ->
          False | (login, user_info) | str(login)
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
        Early hook: attempt to restore 'authenticated' state from session.
        """
        # Verify if session is enabled, if not the user is not authenticated.
        if not hasattr(cherrypy.serving, 'session'):
            return
        # Check if a user_key is stored in session.
        session = cherrypy.serving.session
        user_key = session.get(self._session_user_key())
        if not user_key:
            return

        last = session.get(AUTH_LAST_PASSWORD_AT)
        if last is None:
            return  # never had a password login in this session
        timeout = self._reauth_timeout_minutes()
        if (last + datetime.timedelta(minutes=timeout)) < session.now():
            return

        # Mark request as authenticated by key; user object will be resolved later.
        cherrypy.serving.request.login = user_key

    def _forbidden_or_redirect(self, user_from_key_func, redirect=AUTH_DEFAULT_REDIRECT, **kwargs):
        """
        If authenticated via session, resolve user object; else redirect/403.
        """
        # Allow access to the login page itself
        if cherrypy.serving.request.path_info == redirect:
            return

        user_key = getattr(cherrypy.serving.request, 'login', False)
        if user_key:
            try:
                currentuser = user_from_key_func(user_key)
            except Exception:
                cherrypy.log(
                    f'unexpected error searching for user_key={user_key}',
                    context='AUTH',
                    severity=logging.ERROR,
                    traceback=True,
                )
                currentuser = None

            if currentuser:
                cherrypy.serving.request.currentuser = currentuser
                return

        # Not authenticated or user not found.
        if redirect:
            self.save_original_url()
            raise cherrypy.HTTPRedirect(redirect)
        raise cherrypy.HTTPError(403)

    # ---- Login flows ----

    def login_with_credentials(self, login, password):
        """
        Validate credentials with configured checkers; on success, call login_with_result.
        """
        if not login or not password:
            cherrypy.log('authentication failed reason=empty_credentials', context='AUTH', severity=logging.WARNING)
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
                return self.login_with_result(login=login, user_info=user_info)
            except Exception:
                cherrypy.log(
                    f'unexpected error checking password login={login} checkpassword={func.__qualname__} - continue with next function',
                    context='AUTH',
                    severity=logging.ERROR,
                    traceback=True,
                )
        # If we reach here, authentication failed
        if hasattr(cherrypy.serving, 'session'):
            cherrypy.serving.session.regenerate()  # Prevent session analysis

        remote_ip = cherrypy.serving.request.remote.ip
        cherrypy.log(
            f'authentication failed login={login} ip={remote_ip} reason=wrong_credentials',
            context='AUTH',
            severity=logging.WARNING,
        )

        return None

    def login_with_result(self, login=None, user_info=None, auth_method='password'):
        """
        Called after credentials were validated or via SSO.
        Resolves user via user_lookup_func and establishes the session.
        """
        conf = self._merged_args()
        user_lookup_func = conf.get('user_lookup_func')

        try:
            user_key, userobj = user_lookup_func(login=login, user_info=user_info or {})
        except Exception:
            cherrypy.log(
                f"unexpected error searching user login={login} user_info={user_info}",
                context='AUTH',
                severity=logging.ERROR,
                traceback=True,
            )
            return None

        if not userobj:
            cherrypy.log(
                f"authentication failed login={login} reason=not_found", context='AUTH', severity=logging.WARNING
            )
            return None

        # Notify plugins about user login
        cherrypy.engine.publish('user_login', userobj)

        # Store in session
        if hasattr(cherrypy.serving, 'session'):
            session = cherrypy.serving.session
            session_user_key = self._session_user_key()
            session[session_user_key] = user_key
            session[AUTH_METHOD] = auth_method
            session[AUTH_LAST_PASSWORD_AT] = session.now()
            # Generate a new session id
            session.regenerate()

        # When authenticated, store user_key in request.
        cherrypy.serving.request.login = user_key
        return userobj

    # ---- Session helpers ----

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
        if not hasattr(cherrypy.serving, 'session'):
            return None
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
        # Skip this step if session is not enabled
        if not hasattr(cherrypy.serving, 'session'):
            return
        # Extract URL including query-string.
        request = cherrypy.serving.request
        uri_encoding = getattr(request, 'uri_encoding', 'utf-8')
        original_url = urllib.parse.quote(request.path_info, encoding=uri_encoding)
        query_string = request.query_string

        # Store value in session
        session = cherrypy.serving.session
        session[AUTH_ORIGINAL_URL] = cherrypy.url(original_url, qs=query_string, base='')


cherrypy.tools.auth = AuthManager()
