# Ratelimit tools for cherrypy
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
import hashlib
import os
import tempfile
import threading
import time
from collections import namedtuple

import cherrypy

Tracker = namedtuple('Tracker', ['token', 'hits', 'timeout'])


class _DataStore:
    """
    Base class for rate limit data store
    """

    def __init__(self, **kwargs):
        self._locks = {}

    def get_and_increment(self, token, delay, hit=1):
        lock = self._locks.setdefault(token, threading.RLock())
        with lock:
            tracker = self._load(token)
            if tracker is None or tracker.timeout < time.time():
                tracker = Tracker(token=token, hits=0, timeout=int(time.time() + delay))
            tracker = tracker._replace(hits=tracker.hits + hit)
            self._save(tracker)
        return tracker.hits, tracker.timeout

    def _save(self, tracker):
        raise NotImplementedError

    def _load(self, token):
        raise NotImplementedError


class RamRateLimit(_DataStore):
    """
    Store rate limit information in memory.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._data = {}

    def _load(self, token):
        return self._data.get(token)

    def _save(self, tracker):
        self._data[tracker.token] = tracker

    def reset(self):
        self._data = {}


class FileRateLimit(_DataStore):
    PREFIX = 'ratelimit-'

    def __init__(self, storage_path, **kwargs):
        super().__init__(**kwargs)
        assert storage_path, 'FileRateLimit requires storage_path'
        self.storage_path = os.path.abspath(storage_path)
        os.makedirs(self.storage_path, exist_ok=True)

    def _path(self, token):
        # Hash the token to avoid max path limit and invalid chars.
        digest = hashlib.sha256(token.encode('utf-8')).hexdigest()
        return os.path.join(self.storage_path, self.PREFIX + digest + '.txt')

    def _load(self, token):
        path = self._path(token)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                line = f.readline().strip()
        except FileNotFoundError:
            return None
        except OSError:
            return None

        if not line:
            return None

        parts = line.split()
        if len(parts) != 2:
            return None

        try:
            hits = int(parts[0])
            timeout = int(parts[1])
            if hits < 0 or timeout < 0:
                return None
        except ValueError:
            return None

        return Tracker(token=token, hits=hits, timeout=timeout)

    def _save(self, tracker):
        path = self._path(tracker.token)
        # Atomic write: temp file in same directory
        fd, tmp = tempfile.mkstemp(dir=self.storage_path)
        try:
            with os.fdopen(fd, 'w', encoding='utf-8') as f:
                f.write(f"{tracker.hits} {int(tracker.timeout)}\n")
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp, path)
            # On POSIX, chmod on first write
            try:
                os.chmod(path, 0o600)
            except OSError:
                pass
        finally:
            try:
                if os.path.exists(tmp):
                    os.remove(tmp)
            except Exception:
                pass

    def reset(self):
        for item in os.listdir(self.storage_path):
            if not item.startswith(self.PREFIX):
                continue
            fn = os.path.join(self.storage_path, item)
            if not os.path.isfile(fn):
                continue
            try:
                os.remove(fn)
            except OSError:
                pass


class Ratelimit(cherrypy.Tool):
    CONTEXT = 'TOOLS.RATELIMIT'

    def __init__(self, priority=60):
        super().__init__('before_handler', self.check_ratelimit, 'ratelimit', priority)

    def check_ratelimit(
        self,
        delay=3600,
        limit=25,
        return_status=429,
        logout=False,
        scope=None,
        methods=None,
        debug=False,
        hit=1,
        **conf,
    ):
        """
        Verify the ratelimit. By default return a 429 HTTP error code (Too Many Request). After 25 request within the same hour.

        Arguments:
            delay:         Time window for analysis in seconds
            limit:         Number of request allowed for an entry point
            return_status: HTTP Error code to return.
            logout:        True to logout user when limit is reached
            scope:         if specify, define the scope of rate limit. Default to path_info.
            methods:       if specify, only the methods in the list will be rate limited.
        """
        assert delay > 0, 'invalid delay'

        # Check if limit is enabled
        if limit <= 0:
            return

        # Check if this 'method' should be rate limited
        request = cherrypy.request
        if methods is not None and request.method not in methods:
            if debug:
                cherrypy.log(f'skip rate limit for HTTP method {request.method}', context=self.CONTEXT)
            return

        # If datastore is not pass as configuration, create it for the first time.
        datastore = getattr(self, '_ratelimit_datastore', None)
        if datastore is None:
            # Create storage using storage class
            storage_class = conf.get('storage_class', RamRateLimit)
            datastore = storage_class(**conf)
            self._ratelimit_datastore = datastore

        # Identifier: prefer authenticated user; else client IP
        identifier = getattr(cherrypy.serving.request, 'login', None) or cherrypy.request.remote.ip

        # Include method unless methods is explicitly a single method
        method_part = request.method
        if methods and len(methods) == 1:
            method_part = next(iter(methods))

        # Scope: allow explicit; else normalized path (e.g., strip trailing slash)
        path = request.path_info.rstrip('/') or '/'
        scope_value = scope or path

        token = f"{identifier}|{method_part}|{scope_value}"

        # Get hits count using datastore.
        hits, timeout = datastore.get_and_increment(token, delay, hit)
        if debug:
            cherrypy.log(f'check and increase limit token={token} limit={limit} hits={hits}', context=self.CONTEXT)

        # Verify user has not exceeded rate limit
        remaining = max(0, limit - hits)

        # Define headers
        cherrypy.response.headers['X-RateLimit-Limit'] = str(limit)
        cherrypy.response.headers['X-RateLimit-Remaining'] = str(remaining)
        cherrypy.response.headers['X-RateLimit-Reset'] = str(timeout)

        if limit < hits:  # block only after 'limit' successful requests
            cherrypy.log(f'block access to path_info={request.path_info}', context=self.CONTEXT)
            if logout:
                if hasattr(cherrypy.serving, 'session'):
                    cherrypy.serving.session.clear()
                raise cherrypy.HTTPRedirect("/")
            raise cherrypy.HTTPError(return_status)

    def increase_hit(self, hit=1):
        """
        May be called directly by handlers to add a hit for the given request.
        """
        conf = cherrypy.tools.ratelimit._merged_args()
        conf['hit'] = hit
        cherrypy.tools.ratelimit.callable(**conf)

    def reset(self):
        """
        Used to reset the ratelimit.
        """
        datastore = getattr(self, '_ratelimit_datastore', False)
        if not datastore:
            return
        datastore.reset()


cherrypy.tools.ratelimit = Ratelimit()
