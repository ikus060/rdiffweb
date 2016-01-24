#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

from __future__ import unicode_literals

import cProfile
import cherrypy
import os


_count = 0


class ProfilingApplication(cherrypy.Application):
    """
    Application wrapper to enabled profiling of an application.
    """

    def __init__(self, nextapp, path, aggregate=False):
        """Make a WSGI middleware app which wraps 'nextapp' with profiling.

        nextapp
            the WSGI application to wrap, usually an instance of
            cherrypy.Application.

        path
            where to dump the profiling output.

        aggregate
            if True, profile data for all HTTP requests will go in
            a single file. If False (the default), each HTTP request will
            dump its profile data into a separate file.

        """
        assert nextapp
        assert path

        self.nextapp = nextapp
        self.aggregate = aggregate
        if aggregate:
            global _count
            c = _count = _count + 1
            self.path = os.path.join(path, "rdiffweb_%04d.prof" % c)
            self.prof = cProfile.Profile()
            self._run = self._run_aggregated

    def __getattr__(self, name):
        return getattr(self.nextapp, name)

    def __call__(self, environ, start_response):
        def gather():
            result = []
            for line in self.nextapp(environ, start_response):
                result.append(line)
            return result
        return self._run(gather)

    def _run(self, func, *args, **params):
        """Dump profile data into self.path."""
        global _count
        c = _count = _count + 1
        path = os.path.join(self.path, "rdiffweb_%04d.prof" % c)
        prof = cProfile.Profile()
        result = prof.runcall(func, *args, **params)
        prof.dump_stats(path)
        return result

    def _run_aggregated(self, func, *args, **params):
        """Dump profile data into self.path."""
        result = self.prof.runcall(func, *args, **params)
        self.prof.dump_stats(self.path)
        return result
