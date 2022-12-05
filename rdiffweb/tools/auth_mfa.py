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
import secrets
import string
import urllib.parse

import cherrypy

from rdiffweb.core.passwd import check_password, hash_password

from .auth_form import LOGIN_PERSISTENT, LOGIN_TIME

MFA_USERNAME = '_auth_mfa_username'
MFA_VERIFICATION_TIME = '_auth_mfa_time'
MFA_TRUSTED_IP_LIST = '_auth_mfa_trusted_ip_list'
MFA_REDIRECT_URL = '_auth_mfa_redirect_url'
MFA_CODE = '_auth_mfa_code'
MFA_CODE_TIME = '_auth_mfa_code_time'
MFA_CODE_ATTEMPT = '_auth_mfa_code_attempt'

MFA_DEFAULT_LENGTH = 8
MFA_CODE_MAX_ATTEMPT = 3


class CheckAuthMfa(cherrypy.Tool):
    def __init__(self, priority=74):
        super().__init__(point='before_handler', callable=self.run, priority=priority)

    def _get_code_length(self):
        """
        Return the configured code length.
        """
        length = cherrypy.request.config.get('tools.auth_mfa.code_length')
        return MFA_DEFAULT_LENGTH if length is None else int(length)

    def _get_redirect_url(self):
        """
        Return the original URL the user browser before getting redirect to mfa.
        """
        return cherrypy.session.get(MFA_REDIRECT_URL) or '/'

    def generate_code(self):
        """
        Generate a random code of given length.
        """
        # Get verification code length
        length = self._get_code_length()
        assert length > 0, 'length must be greater than zero'

        # Generate random code
        code = ''.join(secrets.choice(string.digits) for i in range(length))

        # Store hash code in session
        session = cherrypy.session
        session[MFA_USERNAME] = cherrypy.request.login
        session[MFA_CODE] = hash_password(code)
        session[MFA_CODE_TIME] = cherrypy.session.now()
        session[MFA_CODE_ATTEMPT] = 0
        return code

    def _is_verified(self):
        # Check if user is login
        assert cherrypy.request.login, 'auth_mfa requires auth_form tools'
        # Verify if session is enabled
        assert cherrypy.request.config.get('tools.sessions.on', False), 'auth_mfa requires sessions tools'

        # Verify session
        session = cherrypy.session
        return bool(
            session.get(MFA_USERNAME) == cherrypy.request.login
            and session.get(MFA_VERIFICATION_TIME, None)
            and session[MFA_VERIFICATION_TIME] + datetime.timedelta(minutes=session.timeout) > session.now()
            and session.get(MFA_TRUSTED_IP_LIST, [])
            and cherrypy.serving.request.remote.ip in session[MFA_TRUSTED_IP_LIST]
        )

    def is_code_expired(self):
        """
        Return True if the verification code expired and must be re-generate.
        """
        code_timeout = cherrypy.request.config.get('tools.sessions.timeout', 60)
        session = cherrypy.session
        return (
            not hasattr(cherrypy.serving, 'session')
            or session.get(MFA_USERNAME) != cherrypy.request.login
            or session.get(MFA_CODE) is None
            or session.get(MFA_CODE_TIME) is None
            or session.get(MFA_CODE_TIME) + datetime.timedelta(minutes=code_timeout) < session.now()
            or session.get(MFA_CODE_ATTEMPT) >= MFA_CODE_MAX_ATTEMPT
        )

    def run(self, mfa_url='/mfa/', mfa_enabled=True, debug=False, **kwargs):
        """
        A tool that verify Multi-Factor authentication.
        """
        # Check if MFA is enabled. `mfa_enabled` could be a function.
        enabled = mfa_enabled(cherrypy.request.login) if hasattr(mfa_enabled, '__call__') else mfa_enabled

        # Check if `/mfa/` us request
        request = cherrypy.serving.request
        if request.path_info == mfa_url:
            # If MFA is disable or user already verified, redirect user to root page.
            if not enabled or self._is_verified():
                raise cherrypy.HTTPRedirect('/')
            # Otherwise, skip verification.
            return

        # Skip verification if MFA is disabled.
        if not enabled:
            return

        # Check MFA is enabled with persistent session. We want to check user crendetials every "session.timeout"
        session = cherrypy.session
        if session.get(LOGIN_PERSISTENT, False) and session.get(LOGIN_TIME, False):
            session_timeout = cherrypy.request.config.get('tools.sessions.timeout', 60)
            if session[LOGIN_TIME] + datetime.timedelta(minutes=session_timeout) < session.now():
                # Clear login_time to force login
                del session[LOGIN_TIME]
                self._set_redirect_url()
                self.redirect_to_original_url()

        # Check if verified
        if not self._is_verified():
            # Store original URL
            self._set_redirect_url()
            # And redirect to mfa page
            raise cherrypy.HTTPRedirect(mfa_url)

    def redirect_to_original_url(self):
        # Redirect user to original URL
        raise cherrypy.HTTPRedirect(self._get_redirect_url())

    def _set_redirect_url(self):
        # Keep reference to the current URL
        request = cherrypy.serving.request
        original_url = urllib.parse.quote(request.path_info, encoding=request.uri_encoding)
        qs = request.query_string
        new_url = cherrypy.url(original_url, qs=qs, base='')
        if hasattr(cherrypy.serving, 'session'):
            cherrypy.session[MFA_REDIRECT_URL] = new_url

    def verify_code(self, code, persistent=False):
        """
        Must be called by the page handler to verify MFA.
        """
        # Check if code expired
        if self.is_code_expired():
            return False

        # Verify code.
        session = cherrypy.session
        if not check_password(code, session.get(MFA_CODE)):
            # If invalid increase attempt
            session[MFA_CODE_ATTEMPT] = session.get(MFA_CODE_ATTEMPT, 0) + 1
            return False

        # Store information in session
        session[LOGIN_PERSISTENT] = persistent
        session[MFA_VERIFICATION_TIME] = session.now()
        session[MFA_TRUSTED_IP_LIST] = session.get(MFA_TRUSTED_IP_LIST, []) + [cherrypy.serving.request.remote.ip]
        session[MFA_CODE] = None
        session[MFA_CODE_TIME] = None
        session.regenerate()
        return True


cherrypy.tools.auth_mfa = CheckAuthMfa()
