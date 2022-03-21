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
import os
import pickle
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

    def get_and_increment(self, token, delay):
        lock = self._locks.setdefault(token, threading.RLock())
        with lock:
            tracker = self._load(token)
            if tracker is None or tracker.timeout < time.time():
                tracker = Tracker(token=token, hits=0, timeout=int(time.time() + delay))
            tracker = tracker._replace(hits=tracker.hits + 1)
            self._save(tracker)
        return tracker.hits

    def _save(self, token, hits, timeout):
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
        return self._data.get(token, None)

    def _save(self, tracker):
        self._data[tracker.token] = tracker


class FileRateLimit(_DataStore):
    """
    Store rate limit information in files.
    """

    PREFIX = 'ratelimit-'
    pickle_protocol = pickle.HIGHEST_PROTOCOL

    def __init__(self, storage_path, **kwargs):
        super().__init__(**kwargs)
        # The 'storage_path' arg is required for file-based datastore.
        assert (
            storage_path
        ), 'FileRateLimit required a storage_path `tools.ratelimit.storage_path = "/home/site/ratelimit"`'
        self.storage_path = os.path.abspath(storage_path)

    def _path(self, token):
        assert token
        f = os.path.join(self.storage_path, self.PREFIX + token.strip('/').replace('/', '-'))
        if not os.path.abspath(f).startswith(self.storage_path):
            raise ValueError('invalid token')
        return f

    def _load(self, token):
        path = self._path(token)
        try:
            f = open(path, 'rb')
            try:
                return pickle.load(f)
            finally:
                f.close()
        except (IOError, EOFError):
            # Drop session data if invalid
            pass
        return None

    def _save(self, tracker):
        path = self._path(tracker.token)
        f = open(path, 'wb')
        try:
            pickle.dump(tracker, f, self.pickle_protocol)
        finally:
            f.close()


def check_ratelimmit(delay=60, anonymous_limit=0, registered_limit=0, rate_exceed_status=429, debug=False, **conf):
    """
    Verify the ratelimit. By default return a 429 HTTP error code (Too Many Request).

    Usage:

    @cherrypy.tools.ratelimit(on=True, anonymous_limit=5, registered_limit=50, storage_class=FileRateLimit, storage_path='/tmp')
    def index(self):
        pass
    """

    # If datastore is not pass as configuration, create it for the first time.
    datastore = getattr(cherrypy, '_ratelimit_datastore', None)
    if datastore is None:
        # Create storage using storage class
        storage_class = conf.get('storage_class', RamRateLimit)
        datastore = storage_class(**conf)
        cherrypy._ratelimit_datastore = datastore

    # If user is authenticated, use the username else use the ip address
    token = cherrypy.request.login or cherrypy.request.remote.ip

    # Get the real limit depending of user login.
    limit = registered_limit if cherrypy.request.login else anonymous_limit
    if limit is None or limit <= 0:
        return

    # Get hits count using datastore.
    hits = datastore.get_and_increment(token, delay)
    if debug:
        cherrypy.log(
            'check and increase rate limit for token %s, limit %s, hits %s' % (token, limit, hits), 'TOOLS.RATELIMIT'
        )

    # Verify user has not exceeded rate limit
    if limit <= hits:
        raise cherrypy.HTTPError(rate_exceed_status)


cherrypy.tools.ratelimit = cherrypy.Tool('before_handler', check_ratelimmit, priority=60)
