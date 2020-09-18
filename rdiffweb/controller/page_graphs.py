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

from rdiffweb.controller import Controller, validate_isinstance
from rdiffweb.controller.dispatch import poppath

_logger = logging.getLogger(__name__)


@poppath('graph')
class GraphsPage(Controller):

    def _data(self, repo_obj, **kwargs):
        attrs = [
            'starttime', 'endtime', 'elapsedtime', 'sourcefiles', 'sourcefilesize',
            'mirrorfiles', 'mirrorfilesize', 'newfiles', 'newfilesize', 'deletedfiles',
            'deletedfilesize', 'changedfiles', 'changedsourcesize', 'changedmirrorsize',
            'incrementfiles', 'incrementfilesize', 'totaldestinationsizechange', 'errors']

        # Return a generator
        def func():
            # Header
            yield 'date'
            for attr in attrs:
                yield ','
                yield attr
            yield '\n'
            # Content
            for d, s in repo_obj.session_statistics.items():
                yield str(d.epoch())
                for attr in attrs:
                    yield ','
                    yield str(getattr(s, attr))
                yield '\n'

        return func()

    def _page(self, repo_obj, graph, **kwargs):
        """
        Generic method to show graphs.
        """
        # Check if any action to process.
        params = {
            'repo': repo_obj,
            'graphs': graph,
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
