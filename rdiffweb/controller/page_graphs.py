# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

import logging

import cherrypy

from rdiffweb.controller import Controller, validate_isinstance, validate_int
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.librdiff import SessionStatisticsEntry

_logger = logging.getLogger(__name__)


@poppath('graph')
class GraphsPage(Controller):

    def _data(self, repo_obj, limit='30', **kwargs):
        limit = validate_int(limit)

        # Return a generator
        def func():
            # Header
            yield 'date'
            for attr in SessionStatisticsEntry.ATTRS:
                yield ','
                yield attr
            yield '\n'
            # Content
            for stat in repo_obj.session_statistics[-limit:]:
                yield str(stat.date.epoch())
                for attr in SessionStatisticsEntry.ATTRS:
                    yield ','
                    yield str(getattr(stat, attr))
                yield '\n'

        return func()

    def _page(self, repo_obj, graph, limit='30', **kwargs):
        """
        Generic method to show graphs.
        """
        # Check if any action to process.
        params = {
            'repo': repo_obj,
            'graphs': graph,
            'limit': limit,
        }
        # Generate page.
        return self._compile_template("graphs_%s.html" % graph, **params)

    @cherrypy.expose
    def default(self, graph, path, **kwargs):
        """
        Called to show every graphs
        """
        validate_isinstance(graph, bytes)
        graph = graph.decode('ascii', 'replace')
        repo_obj = self.app.store.get_repo(path)

        # check if data should be shown.
        if graph == 'data':
            return self._data(repo_obj, **kwargs)
        elif graph in ['activities', 'errors', 'files', 'sizes', 'times']:
            return self._page(repo_obj, graph, **kwargs)
        # Raise error.
        raise cherrypy.NotFound()
