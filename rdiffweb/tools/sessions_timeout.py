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
import math
import time

import cherrypy
from cherrypy.lib import httputil

SESSION_PERSISTENT = '_session_persistent'
SESSION_START_TIME = '_session_start_time'


class SessionsTimeout(cherrypy.Tool):
    """
    Fine-grained control over session timeouts.

    Config keys:
      - tools.sessions.timeout (int, minutes)  -> idle timeout (CherryPy built-in)
      - tools.sessions_timeout.absolute_timeout (int, minutes)  -> absolute cap for non-persistent sessions, default=60
      - tools.sessions_timeout.persistent_timeout (int, minutes) -> absolute cap for persistent sessions, default=43200
      - tools.sessions.name (str) -> session cookie name (default: 'session_id')
    """

    def __init__(self, priority: int = 75):
        super().__init__(point='before_handler', callable=self.run, priority=priority)

    @staticmethod
    def _cookie_name() -> str:
        return cherrypy.request.config.get('tools.sessions.name', 'session_id')

    @staticmethod
    def _get_config_timeouts() -> tuple:
        cfg = cherrypy.request.config
        idle_timeout = int(cfg.get('tools.sessions.timeout', 60))
        persistent_timeout = int(cfg.get('tools.sessions_timeout.persistent_timeout', 43200))
        absolute_timeout = int(cfg.get('tools.sessions_timeout.absolute_timeout', 60))
        return idle_timeout, persistent_timeout, absolute_timeout

    def _set_cookie_max_age(self, max_age: int) -> None:
        """Adjust only Max-Age and Expires for the session cookie, keep other flags intact."""
        cookie_name = self._cookie_name()
        cookie = cherrypy.serving.response.cookie
        # Ensure the cookie key exists (CherryPy will set it when the session id is issued/regenerated).
        if cookie_name not in cookie:
            # Create the key so we can set attributes; value will be supplied by CherryPy on regenerate/open.
            cookie[cookie_name] = cherrypy.serving.session.id
        cookie[cookie_name]['max-age'] = str(max(0, max_age))
        cookie[cookie_name]['expires'] = httputil.HTTPDate(time.time() + max(0, max_age))

    def _compute_minutes(self, seconds: int) -> int:
        if seconds <= 0:
            return 0
        return int(math.ceil(seconds / 60.0))

    def _update_session_timeout(self) -> None:
        session = cherrypy.serving.session
        if SESSION_START_TIME not in session:
            session[SESSION_START_TIME] = session.now()

        now: datetime.datetime = session.now()
        start: datetime.datetime = session[SESSION_START_TIME]

        # Pull configured values with supplied defaults as fallbacks
        idle_timeout, persistent_timeout, absolute_timeout = self._get_config_timeouts()

        if session.get(SESSION_PERSISTENT, False):
            # Persistent session: fixed absolute lifetime from start
            expiration = start + datetime.timedelta(minutes=persistent_timeout)
            max_age = int((expiration - now).total_seconds())
            minutes = self._compute_minutes(max_age)

            if minutes <= 0:
                # Expired: replace session and start a new persistent window
                session.clear()
                session.regenerate()
                session[SESSION_START_TIME] = session.now()
                session[SESSION_PERSISTENT] = True
                # Set a fresh timeout for the new session
                session.timeout = persistent_timeout
                # Update cookie with full persistent lifetime
                self._set_cookie_max_age(persistent_timeout * 60)
                return

            session.timeout = minutes
            # Keep cookie aligned with remaining time
            self._set_cookie_max_age(max_age)
        else:
            # Non-persistent: sliding idle timeout but capped by absolute since start
            expiration_idle = now + datetime.timedelta(minutes=idle_timeout)
            expiration_absolute = start + datetime.timedelta(minutes=absolute_timeout)
            expiration = min(expiration_idle, expiration_absolute)

            max_age = int((expiration - now).total_seconds())
            minutes = self._compute_minutes(max_age)

            if minutes <= 0:
                session.clear()
                # After expiry, new session starts with fresh idle window; up to you to gate auth elsewhere
                session.timeout = int(idle_timeout)
                session.regenerate()
                return

            session.timeout = minutes
            # For non-persistent sessions, let CherryPy manage the cookie; no explicit Max-Age.

    def run(self, persistent_timeout: int = 43200, absolute_timeout: int = 60) -> None:
        # Skip if sessions are not enabled
        if not hasattr(cherrypy.serving, 'session'):
            return

        # Use the configured values
        self._update_session_timeout()

    def set_persistent(self, value: bool = True) -> None:
        """Mark current session as persistent (or not) and reset the start window."""
        session = cherrypy.serving.session
        session[SESSION_PERSISTENT] = value
        session[SESSION_START_TIME] = session.now()
        # Apply updated policy immediately using configured values
        self._update_session_timeout()

    def is_persistent(self) -> bool:
        """Return True if the session is marked persistent."""
        return bool(cherrypy.serving.session.get(SESSION_PERSISTENT, False))

    def get_session_start_time(self) -> datetime.datetime:
        """Return the session start time if any."""
        return cherrypy.serving.session.get(SESSION_START_TIME, None)


cherrypy.tools.sessions_timeout = SessionsTimeout()
