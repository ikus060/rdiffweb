#!/usr/bin/python
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

from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from builtins import bytes
from builtins import str
import cherrypy
from future.utils import iteritems

from rdiffweb.controller import Controller, validate_isinstance
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core import librdiff


_logger = logging.getLogger(__name__)


@poppath('graph')
class GraphsPage(Controller):

    def _data(self, path, **kwargs):
        assert isinstance(path, bytes)

        _logger.debug("repo stats [%r]", path)

        # Check user permissions
        try:
            repo_obj = self.app.currentuser.get_repo_path(path)[0]
        except librdiff.FileError as e:
            _logger.exception("invalid user path [%r]", path)
            return self._compile_error_template(str(e))

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
            for d, s in iteritems(repo_obj.session_statistics):
                yield str(d.epoch())
                for attr in attrs:
                    yield ','
                    yield str(getattr(s, attr))
                yield '\n'

        return func()

    def _page(self, path, graph, **kwargs):
        """
        Generic method to show graphs.
        """
        _logger.debug("repo graphs [%r][%r]", graph, path)

        # Check user permissions
        try:
            repo_obj = self.app.currentuser.get_repo_path(path)[0]
        except librdiff.FileError as e:
            _logger.exception("invalid user path [%r]", path)
            return self._compile_error_template(str(e))

        # Check if any action to process.
        params = {
            'repo_name': repo_obj.display_name,
            'repo_path': repo_obj.path,
            'graphs': graph,
        }

        # Generate page.
        return self._compile_template("graphs_%s.html" % graph, **params)

    @cherrypy.expose
    def index(self, graph, path, **kwargs):
        """
        Called to show every graphs
        """
        validate_isinstance(path, bytes)
        validate_isinstance(graph, bytes)
        graph = graph.decode('ascii', 'replace')

        # check if data should be shown.
        if graph == 'data':
            return self._data(path, **kwargs)
        elif graph in ['activities', 'errors', 'files', 'sizes', 'times']:
            return self._page(path, graph, **kwargs)
        # Raise error.
        raise cherrypy.NotFound()
