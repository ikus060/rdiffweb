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
import os
import threading
import time

import cherrypy
from cherrypy.process.plugins import Monitor

logger = logging.getLogger(__name__)


class DirCache(Monitor):
    """
    Warm up directory listings by caching 'sorted(names)' and refreshing them
    periodically in the background so listdir() rarely needs to rescan.

    frequency: seconds between maintenance cycles (default 1 min).
    """

    frequency = 60  # default cadence (1 min)

    max_refresh_per_cycle = 10

    def __init__(self, bus, frequency=frequency, max_refresh_per_cycle=max_refresh_per_cycle):
        self._lock = threading.RLock()
        # Ordered "set+cache": path -> None or (mtime_ns, tuple(names))
        self._cache_entries = {}
        self._max_refresh = max_refresh_per_cycle
        self._round_robin_idx = 0
        super().__init__(bus, self.run, frequency or self.frequency, "dir-cache")

    # ------------- public API -------------

    def add_path(self, path):
        path = os.path.abspath(path)
        with self._lock:
            # Insert only if absent; keep position otherwise
            self._cache_entries.setdefault(path, None)

    def remove_path(self, path):
        path = os.path.abspath(path)
        with self._lock:
            self._cache_entries.pop(path, None)

    def listdir(self, path, _update=False):
        try:
            mtime = os.lstat(path).st_mtime_ns
        except OSError:
            self.remove_path(path)
            raise

        with self._lock:
            entry = self._cache_entries.get(path)

        # Fast path: have cache and mtime matches
        if entry is not None and entry[0] == mtime:
            if not _update:
                logger.debug("using cached entries for %s", path)
            # return a copy as list to avoid exposing our tuple
            return False if _update else list(entry[1])

        # Miss or stale: refresh on caller’s thread (avoid holding the lock during I/O)
        if not _update:
            logger.debug("cache miss for %s", path)
        names = sorted(e.name for e in os.scandir(path))
        try:
            mtime2 = os.lstat(path).st_mtime_ns
        except OSError:
            self.remove_path(path)
            raise

        with self._lock:
            # Only publish if not changed during scan; otherwise let background run catch up
            if mtime == mtime2:
                self._cache_entries[path] = (mtime2, tuple(names))

        return True if _update else names

    # ------------- background maintenance -------------

    def run(self):
        t0 = time.time()

        # Snapshot keys and compute the batch in round-robin order
        with self._lock:
            if not self._cache_entries:
                return
            keys = list(self._cache_entries.keys())
            n_total = len(keys)
            start = self._round_robin_idx % n_total
            n = n_total if self._max_refresh is None else min(self._max_refresh, n_total)
            batch_idx = [(start + i) % n_total for i in range(n)]
            batch_paths = [keys[i] for i in batch_idx]

        # Process batch without holding the lock
        last_path = None
        refreshed = 0
        for path in batch_paths:
            # Refresh by calling listdir
            try:
                if self.listdir(path, _update=True):
                    last_path = path
                    refreshed += 1
            except OSError as e:
                logger.debug("scan failed for %s: %s (removing from watch)", path, e)
                self.remove_path(path)
                continue

        # Apply removals and advance the RR index
        if last_path:
            # Advance to the element after the last processed path that still exists.
            keys_now = list(self._cache_entries.keys())
            next_idx = (keys_now.index(last_path) + 1) % len(keys_now)
            self._round_robin_idx = next_idx

        if refreshed:
            logger.debug("dir-cache refreshed %d/%d dirs in %.3fs", refreshed, len(batch_paths), time.time() - t0)


cherrypy.dircache = DirCache(cherrypy.engine)
cherrypy.dircache.subscribe()

cherrypy.config.namespaces['dircache'] = lambda key, value: setattr(cherrypy.dircache, key, value)
