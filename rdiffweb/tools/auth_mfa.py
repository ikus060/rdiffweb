# MFA tool for cherrypy
# Copyright (C) 2022-2025 Patrik Dufresne
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
import secrets
import string
from typing import Optional

import cherrypy

from rdiffweb.core.passwd import check_password, hash_password

MFA_CODE = '_auth_mfa_code'
MFA_CODE_TIME = '_auth_mfa_code_time'
MFA_CODE_ATTEMPT = '_auth_mfa_code_attempt'
MFA_REDIRECT_URL = '_auth_mfa_redirect_url'
MFA_TRUSTED_IP_LIST = '_auth_mfa_trusted_ip_list'
MFA_USER_KEY = '_auth_mfa_user_key'
MFA_VERIFICATION_TIME = '_auth_mfa_time'

MFA_DEFAULT_CODE_TIMEOUT = 10  # minutes
MFA_DEFAULT_LENGTH = 8
MFA_DEFAULT_MAX_ATTEMPT = 3
MFA_DEFAULT_MAX_TRUSTED_IPS = 5
MFA_DEFAULT_TRUST_DURATION = 43200  # 30 days


class CheckAuthMfa(cherrypy.Tool):
    def __init__(self, priority: int = 75):
        super().__init__(point='before_handler', callable=self.run, priority=priority)

    # ---- Config helpers ----

    @staticmethod
    def _code_length() -> int:
        """Return the configured code length."""
        length = cherrypy.request.config.get('tools.auth_mfa.code_length', MFA_DEFAULT_LENGTH)
        return max(1, int(length))

    @staticmethod
    def _code_timeout_minutes() -> int:
        # Lifetime for a one-time MFA code
        return int(cherrypy.request.config.get('tools.auth_mfa.code_timeout', MFA_DEFAULT_CODE_TIMEOUT))

    @staticmethod
    def _max_attempts() -> int:
        return int(cherrypy.request.config.get('tools.auth_mfa.max_attempts', MFA_DEFAULT_MAX_ATTEMPT))

    @staticmethod
    def _max_trusted_ips() -> int:
        return int(cherrypy.request.config.get('tools.auth_mfa.max_trusted_ips', MFA_DEFAULT_MAX_TRUSTED_IPS))

    @staticmethod
    def _trust_duration_minutes() -> int:
        # How long a device/IP remains “MFA-verified”
        return int(cherrypy.request.config.get('tools.auth_mfa.trust_duration', MFA_DEFAULT_TRUST_DURATION))

    # ---- Core operations ----

    def generate_code(self) -> str:
        """
        Generate a random numeric code, store its hash and metadata in the session,
        and return the cleartext so the caller can deliver it out-of-band.
        """
        if not hasattr(cherrypy.serving, 'session'):
            raise cherrypy.HTTPError(500, 'MFA requires sessions')

        if not cherrypy.request.login:
            raise cherrypy.HTTPError(401, 'MFA requires an authenticated username')

        length = self._code_length()
        code = ''.join(secrets.choice(string.digits) for _ in range(length))
        session = cherrypy.serving.session
        session[MFA_USER_KEY] = cherrypy.request.login
        session[MFA_CODE] = hash_password(code)
        session[MFA_CODE_TIME] = session.now()
        session[MFA_CODE_ATTEMPT] = 0
        return code

    def _is_verified(self) -> bool:
        """Return True if current user/IP is within the MFA trust window."""
        if not cherrypy.request.login or not hasattr(cherrypy.serving, 'session'):
            return False

        # Check if our username match current login user.
        session = cherrypy.serving.session
        if session.get(MFA_USER_KEY) != cherrypy.request.login:
            return False

        # Check if the current IP is trusted
        ip_list = session.get(MFA_TRUSTED_IP_LIST) or []
        if cherrypy.request.remote.ip not in ip_list:
            return False

        # Check if user ever pass the verification.
        verified_at: Optional[datetime.datetime] = session.get(MFA_VERIFICATION_TIME)
        if not verified_at:
            return False

        # Check trusted duration time
        trust_minutes = self._trust_duration_minutes()
        if (verified_at + datetime.timedelta(minutes=trust_minutes)) <= session.now():
            return False

        return True

    def is_code_expired(self) -> bool:
        """
        Return True if the current user's MFA code is absent, expired, or attempts exceeded.
        """
        # Check session existence first to avoid AttributeError
        if not hasattr(cherrypy.serving, 'session'):
            return True

        session = cherrypy.serving.session
        if session.get(MFA_USER_KEY) != cherrypy.request.login:
            return True

        # Check if code is defined.
        hash_ = session.get(MFA_CODE)
        if not hash_:
            return True

        # Check issued time.
        issued_at: Optional[datetime.datetime] = session.get(MFA_CODE_TIME)
        if not issued_at or ((issued_at + datetime.timedelta(minutes=self._code_timeout_minutes())) < session.now()):
            return True

        # Check number of attempt.
        attempts = int(session.get(MFA_CODE_ATTEMPT, 0))
        if attempts >= self._max_attempts():
            return True

        return False

    # ---- Tool entrypoint ----

    def run(self, mfa_url: str = '/mfa/', mfa_enabled=True, **_):
        """
        Gate requests for users who have MFA enabled but are not yet verified.
        mfa_enabled can be a bool or a callable returning bool.
        """
        enabled = mfa_enabled() if callable(mfa_enabled) else bool(mfa_enabled)

        # Normalize request path
        request = cherrypy.serving.request
        req_path = request.path_info or '/'
        mfa_path = mfa_url if mfa_url.startswith('/') else '/' + mfa_url

        # If the current request is the MFA page itself:
        if req_path.rstrip('/') == mfa_path.rstrip('/'):
            # If disabled or already verified, send user back to the original URL (or home)
            if not enabled or self._is_verified():
                raise cherrypy.tools.auth.redirect_to_original_url()
            return  # Allow the MFA page handler to render

        # If MFA is globally disabled for this user/realm, allow through
        if not enabled:
            return

        # Final gate: redirect to MFA if not verified
        if not self._is_verified():
            cherrypy.tools.auth.save_original_url()
            # Use a relative, safe redirect
            raise cherrypy.HTTPRedirect(mfa_path)

    # ---- Verification API for the MFA page handler ----

    def verify_code(self, code: str, persistent: bool = False) -> bool:
        """
        Verify the supplied one-time code. On success:
          - mark session persistent if requested
          - stamp verification time
          - add client IP to trusted list (dedup, cap)
          - clear the code, rotate session id
        """
        if not hasattr(cherrypy.serving, 'session'):
            return False

        session = cherrypy.serving.session
        stored_hash = session.get(MFA_CODE)
        is_expired = self.is_code_expired()
        if self.is_code_expired():
            return False

        # Always perform the hash check regardless of expiration
        # to prevent timing attacks
        code_valid = False
        if stored_hash:
            code_valid = check_password(code, stored_hash)

        # Check all conditions after hash verification
        if is_expired or not code_valid:
            if not is_expired:  # Only increment if not expired
                session[MFA_CODE_ATTEMPT] = attempts = int(session.get(MFA_CODE_ATTEMPT, 0)) + 1
            cherrypy.log(
                f'verification failed user={cherrypy.request.login} ip={cherrypy.request.remote.ip} attempts={attempts}',
                context='MFA',
                severity=logging.WARNING,
            )
            return False

        # Success: trust this device/IP for the configured duration
        session[MFA_VERIFICATION_TIME] = session.now()
        ip_list = list({*(session.get(MFA_TRUSTED_IP_LIST) or []), cherrypy.request.remote.ip})
        # Cap the list to avoid unbounded growth (keep most recent N)
        max_ips = self._max_trusted_ips()
        if len(ip_list) > max_ips:
            ip_list = ip_list[-max_ips:]
        session[MFA_TRUSTED_IP_LIST] = ip_list

        # Clear the one-time code
        session[MFA_CODE] = None
        session[MFA_CODE_TIME] = None
        session[MFA_CODE_ATTEMPT] = 0

        # Honor “remember this device” option by making the session persistent
        if hasattr(cherrypy.tools, 'sessions_timeout'):
            try:
                cherrypy.tools.sessions_timeout.set_persistent(bool(persistent))
            except Exception:
                pass

        # Rotate session id to prevent fixation
        session.regenerate()
        cherrypy.log(
            f'verification successful user={cherrypy.request.login} ip={cherrypy.request.remote.ip}', context='MFA'
        )
        return True


cherrypy.tools.auth_mfa = CheckAuthMfa()
