# -*- coding: utf-8 -*-
# udb, A web interface to manage IT network
# Copyright (C) 2022 IKUS Software inc.
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

    def get_and_increment(self, token, delay, hit=1):
        lock = self._locks.setdefault(token, threading.RLock())
        with lock:
            tracker = self._load(token)
            if tracker is None or tracker.timeout < time.time():
                tracker = Tracker(token=token, hits=0, timeout=int(time.time() + delay))
            tracker = tracker._replace(hits=tracker.hits + hit)
            self._save(tracker)
        return tracker.hits

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
        except Exception:
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


def check_ratelimit(
    delay=3600, limit=25, return_status=429, logout=False, scope=None, methods=None, debug=False, hit=1, **conf
):
    """
    Verify the ratelimit. By default return a 429 HTTP error code (Too Many Request). After 25 request within the same hour.

    Arguments:
        delay:         Time window for analysis in seconds. Default per hour (3600 seconds)
        limit:         Number of request allowed for an entry point. Default 25
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
            cherrypy.log(
                'skip rate limit for HTTP method %s' % (request.method,),
                'TOOLS.RATELIMIT',
            )
        return

    # If datastore is not pass as configuration, create it for the first time.
    datastore = getattr(cherrypy.request.app, '_ratelimit_datastore', None)
    if datastore is None:
        # Create storage using storage class
        storage_class = conf.get('storage_class', RamRateLimit)
        datastore = storage_class(**conf)
        cherrypy.request.app._ratelimit_datastore = datastore

    # If user is authenticated, use the username else use the ip address
    identifier = request.remote.ip
    if hasattr(cherrypy.serving, 'session') and cherrypy.serving.session.get('_cp_username', None):
        identifier = cherrypy.serving.session.get('_cp_username', None)
    token = identifier + '.' + (scope or request.path_info)

    # Get hits count using datastore.
    hits = datastore.get_and_increment(token, delay, hit)
    if debug:
        cherrypy.log(
            'check and increase rate limit for scope %s, limit %s, hits %s' % (token, limit, hits), 'TOOLS.RATELIMIT'
        )

    # Verify user has not exceeded rate limit
    if limit <= hits:
        if logout:
            if hasattr(cherrypy.serving, 'session'):
                cherrypy.serving.session.clear()
            raise cherrypy.HTTPRedirect("/")

        raise cherrypy.HTTPError(return_status)


def hit(hit=1):
    """
    May be called directly by handlers to add a hit for the given request.
    """
    conf = cherrypy.tools.ratelimit._merged_args()
    conf['hit'] = hit
    cherrypy.tools.ratelimit.callable(**conf)


cherrypy.tools.ratelimit = cherrypy.Tool('before_handler', check_ratelimit, priority=60)


cherrypy.tools.ratelimit.hit = hit
