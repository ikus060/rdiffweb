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

import chartkick  # @UnusedImport
import cherrypy
import pkg_resources
from rdiffweb.controller import Controller, validate_isinstance, validate_int
from rdiffweb.controller.dispatch import poppath, static
from rdiffweb.core.i18n import ugettext as _


_logger = logging.getLogger(__name__)


def bytes_to_mb(v):
    return round(v / 1024 / 1024, 2)

class Data():

    def __init__(self, repo_obj, limit):
        self.repo_obj = repo_obj
        self.limit = limit

    @property
    def activities(self):
        return [
            {'name': _('New files'), 'data': [
                [str(s.date).replace('T', ' '), s.newfiles] for s in self.repo_obj.session_statistics[:-self.limit - 1:-1]]},
            {'name': _('Deleted files'), 'data': [
                [str(s.date).replace('T', ' '), s.deletedfiles] for s in self.repo_obj.session_statistics[:-self.limit - 1:-1]]},
            {'name': _('Changed files'), 'data': [
                [str(s.date).replace('T', ' '), s.changedfiles] for s in self.repo_obj.session_statistics[:-self.limit - 1:-1]]}]

    @property
    def filecount(self):
        return [
            {'name': _('Number of files'), 'data': [
                [s.starttime, s.sourcefiles] for s in self.repo_obj.session_statistics[-self.limit:]]}]

    @property
    def filesize(self):
        return [
            {'name': _('New file size (MiB)'), 'data': [
                [s.starttime, bytes_to_mb(s.newfilesize)] for s in self.repo_obj.session_statistics[-self.limit:]]},
            {'name': _('Deleted file size (MiB)'), 'data': [
                [s.starttime, bytes_to_mb(s.deletedfilesize)] for s in self.repo_obj.session_statistics[-self.limit:]]},
            {'name': _('Changed file size (MiB)'), 'data': [
                [s.starttime, bytes_to_mb(s.changedmirrorsize)] for s in self.repo_obj.session_statistics[-self.limit:]]},
            {'name': _('Increment file size (MiB)'), 'data': [
                [s.starttime, bytes_to_mb(s.incrementfilesize)] for s in self.repo_obj.session_statistics[-self.limit:]]},
            {'name': _('Destination size change (MiB)'), 'data': [
                [s.starttime, bytes_to_mb(s.totaldestinationsizechange)] for s in self.repo_obj.session_statistics[-self.limit:]]}]

    @property
    def sourcefilesize(self):
        return [
            {'name': _('Source file size (MiB)'), 'data': [
                [s.starttime, bytes_to_mb(s.sourcefilesize)] for s in self.repo_obj.session_statistics[-self.limit:]]}]

    @property
    def elapsedtime(self):
        return [
            {'name': _('Elapsed Time (minutes)'), 'data': [
                [s.starttime, round(max(0, s.elapsedtime) / 60, 2)] for s in self.repo_obj.session_statistics[-self.limit:]]}]

    @property
    def errors(self):
        return [
            {'name': _('Error count'), 'data': [
                [s.starttime, s.errors] for s in self.repo_obj.session_statistics[-self.limit:]]}]


@poppath('graph')
class GraphsPage(Controller):

    def __init__(self):
        self.chartkick_js = static(
            pkg_resources.resource_filename('chartkick', 'js/chartkick.js'))  # @UndefinedVariable

    @cherrypy.expose
    def default(self, graph, path, limit='30', **kwargs):
        """
        Called to show every graphs
        """
        validate_isinstance(graph, bytes)
        graph = graph.decode('ascii', 'replace')
        repo_obj = self.app.store.get_repo(path)
        limit = validate_int(limit)
        if graph not in ['activities', 'errors', 'files', 'sizes', 'times']:
            raise cherrypy.NotFound()

        # Check if any action to process.
        params = {
            'repo': repo_obj,
            'graph': graph,
            'limit': limit,
            'data': Data(repo_obj, limit),
        }
        # Generate page.
        return self._compile_template("graphs_%s.html" % graph, **params)
