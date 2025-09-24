# Session timeout tool for cherrypy
# Copyright (C) 2012-2025 IKUS Software
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

SESSION_DEFAULT_ABSOLUTE_TIMEOUT = 43200  # 30 days
SESSION_DEFAULT_PERSISTENT_TIMEOUT = 10080  # 7 days
SESSION_DEFAULT_TIMEOUT = 60  # 60 minutes (from cherrypy default)


class SessionsTimeout(cherrypy.Tool):
    """
    Fine-grained control over session timeouts.

    Config keys:
      - tools.sessions.timeout (int, minutes)  -> base idle timeout (CherryPy built-in, used for non-persistent)
      - tools.sessions_timeout.absolute_timeout (int, minutes)  -> hard cap for all sessions (default=43200 = 30d)
      - tools.sessions_timeout.persistent_timeout (int, minutes) -> sliding window for persistent sessions (default=10080 = 7d)
      - tools.sessions.name (str) -> session cookie name (default: 'session_id')
    """

    def __init__(self, priority: int = 75):
        super().__init__(point='before_handler', callable=self.run, priority=priority)

    @staticmethod
    def _cookie_name() -> str:
        return cherrypy.request.config.get('tools.sessions.name', 'session_id')

    @staticmethod
    def _get_config_timeouts() -> tuple[int, int, int]:
        cfg = cherrypy.request.config
        idle_timeout = int(cfg.get('tools.sessions.timeout', SESSION_DEFAULT_TIMEOUT))
        persistent_timeout = int(
            cfg.get('tools.sessions_timeout.persistent_timeout', SESSION_DEFAULT_PERSISTENT_TIMEOUT)
        )
        absolute_timeout = int(cfg.get('tools.sessions_timeout.absolute_timeout', SESSION_DEFAULT_ABSOLUTE_TIMEOUT))
        return idle_timeout, persistent_timeout, absolute_timeout

    def _set_cookie_max_age(self, max_age: int) -> None:
        """Adjust only Max-Age and Expires for the session cookie, keep other flags intact."""
        cookie_name = self._cookie_name()
        cookie = cherrypy.serving.response.cookie
        # Ensure the cookie key exists (CherryPy sets it when session id is issued/regenerated).
        if cookie_name not in cookie:
            cookie[cookie_name] = cherrypy.serving.session.id
        cookie[cookie_name]['max-age'] = str(max(0, max_age))
        cookie[cookie_name]['expires'] = httputil.HTTPDate(time.time() + max(0, max_age))

    @staticmethod
    def _ceil_minutes(seconds: int) -> int:
        if seconds <= 0:
            return 0
        return int(math.ceil(seconds / 60.0))

    def _ensure_start_time(self) -> None:
        """Ensure the session has a stable start time anchor for absolute timeout."""
        session = cherrypy.serving.session
        if SESSION_START_TIME not in session or not isinstance(session.get(SESSION_START_TIME), datetime.datetime):
            session[SESSION_START_TIME] = session.now()

    def _expire_and_restart(self, make_persistent: bool | None = None) -> None:
        """Expire current session and start a fresh one. Optionally set persistent flag."""
        session = cherrypy.serving.session
        session.clear()
        session.regenerate()
        session[SESSION_START_TIME] = session.now()
        if make_persistent is not None:
            session[SESSION_PERSISTENT] = bool(make_persistent)

    def _update_session_timeout(self) -> None:
        session = cherrypy.serving.session
        self._ensure_start_time()

        now: datetime.datetime = session.now()
        start: datetime.datetime = session[SESSION_START_TIME]

        idle_timeout_min, persistent_timeout_min, absolute_timeout_min = self._get_config_timeouts()

        is_persistent = bool(session.get(SESSION_PERSISTENT, False))

        # Compute absolute remaining (hard cap from start, never slides)
        abs_expiration = start + datetime.timedelta(minutes=absolute_timeout_min)
        abs_remaining_sec = int((abs_expiration - now).total_seconds())

        if is_persistent:
            # Sliding window for persistent sessions
            sliding_exp = now + datetime.timedelta(minutes=persistent_timeout_min)
        else:
            # Sliding window for non-persistent sessions (idle timeout)
            sliding_exp = now + datetime.timedelta(minutes=idle_timeout_min)

        sliding_remaining_sec = int((sliding_exp - now).total_seconds())

        # Effective remaining is the minimum of the sliding window and absolute cap
        remaining_sec = min(abs_remaining_sec, sliding_remaining_sec)
        remaining_min = self._ceil_minutes(remaining_sec)

        if remaining_min <= 0:
            # Expired due to either sliding window or absolute cap
            # Start a fresh session; do NOT automatically re-mark persistent here.
            # Authentication/Remember me logic elsewhere can call set_persistent(True) again after login.
            self._expire_and_restart()
            # After regeneration, set a sensible session.timeout baseline:
            cherrypy.serving.session.timeout = idle_timeout_min
            return

        # Apply per-request remaining minutes to CherryPy's session timeout
        session.timeout = remaining_min

        if is_persistent:
            # Keep cookie lifetime aligned with remaining time so it can survive browser restarts.
            self._set_cookie_max_age(remaining_sec)
        else:
            # For non-persistent, let CherryPy manage the session cookie (session or transient cookie).
            # If you want strict enforcement client-side too, uncomment the next line:
            # self._set_cookie_max_age(remaining_sec)
            pass

    def run(self, persistent_timeout: int = 10080, absolute_timeout: int = 43200) -> None:
        # Skip if sessions are not enabled
        if not hasattr(cherrypy.serving, 'session'):
            return

        # Ensure configured values are honored (method signature kept for CherryPy Tool interface)
        self._update_session_timeout()

    def set_persistent(self, value: bool = True) -> None:
        """Mark current session as persistent (or not) and reset the start window."""
        session = cherrypy.serving.session
        session[SESSION_PERSISTENT] = bool(value)
        # Reset absolute window anchor when the persistence policy changes
        session[SESSION_START_TIME] = session.now()
        self._update_session_timeout()

    def is_persistent(self) -> bool:
        """Return True if the session is marked persistent."""
        return bool(cherrypy.serving.session.get(SESSION_PERSISTENT, False))

    def get_session_start_time(self) -> datetime.datetime | None:
        """Return the session start time if any."""
        return cherrypy.serving.session.get(SESSION_START_TIME, None)


cherrypy.tools.sessions_timeout = SessionsTimeout()
