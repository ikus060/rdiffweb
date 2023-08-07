# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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


import cherrypy

from rdiffweb.controller import Controller, validate_int
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject
from rdiffweb.tools.i18n import ugettext as _


def bytes_to_mb(v):
    return round(v / 1024 / 1024, 2)


def line_to_state(line):
    """
    For a file statistics entry, determine if the file was changed.
    """
    if line.changed == '0':
        return 'unchanged'
    elif line.source_size == 'NA':
        return 'deleted'
    elif line.mirror_size == 'NA':
        return 'new'
    else:
        return 'changed'


def line_to_size(line):
    """
    Return either the source or mirror file size.
    """
    if line.source_size != 'NA':
        return line.source_size
    elif line.mirror_size != 'NA':
        return line.mirror_size
    return 0


class Data:
    def __init__(self, repo_obj, limit):
        self.repo_obj = repo_obj
        self.limit = limit

    @property
    def activities(self):
        return [
            {
                'name': _('New files'),
                'data': [
                    [str(s.date).replace('T', ' '), s.newfiles]
                    for s in self.repo_obj.session_statistics[: -self.limit - 1 : -1]
                ],
            },
            {
                'name': _('Deleted files'),
                'data': [
                    [str(s.date).replace('T', ' '), s.deletedfiles]
                    for s in self.repo_obj.session_statistics[: -self.limit - 1 : -1]
                ],
            },
            {
                'name': _('Changed files'),
                'data': [
                    [str(s.date).replace('T', ' '), s.changedfiles]
                    for s in self.repo_obj.session_statistics[: -self.limit - 1 : -1]
                ],
            },
        ]

    @property
    def filecount(self):
        return [
            {
                'name': _('Number of files'),
                'data': [[s.starttime, s.sourcefiles] for s in self.repo_obj.session_statistics[-self.limit :]],
            }
        ]

    @property
    def filesize(self):
        return [
            {
                'name': _('New file size (MiB)'),
                'data': [
                    [s.starttime, bytes_to_mb(s.newfilesize)] for s in self.repo_obj.session_statistics[-self.limit :]
                ],
            },
            {
                'name': _('Deleted file size (MiB)'),
                'data': [
                    [s.starttime, bytes_to_mb(s.deletedfilesize)]
                    for s in self.repo_obj.session_statistics[-self.limit :]
                ],
            },
            {
                'name': _('Changed file size (MiB)'),
                'data': [
                    [s.starttime, bytes_to_mb(s.changedmirrorsize)]
                    for s in self.repo_obj.session_statistics[-self.limit :]
                ],
            },
            {
                'name': _('Increment file size (MiB)'),
                'data': [
                    [s.starttime, bytes_to_mb(s.incrementfilesize)]
                    for s in self.repo_obj.session_statistics[-self.limit :]
                ],
            },
            {
                'name': _('Destination size change (MiB)'),
                'data': [
                    [s.starttime, bytes_to_mb(s.totaldestinationsizechange)]
                    for s in self.repo_obj.session_statistics[-self.limit :]
                ],
            },
        ]

    @property
    def sourcefilesize(self):
        return [
            {
                'name': _('Source file size (MiB)'),
                'data': [
                    [s.starttime, bytes_to_mb(s.sourcefilesize)]
                    for s in self.repo_obj.session_statistics[-self.limit :]
                ],
            }
        ]

    @property
    def elapsedtime(self):
        return [
            {
                'name': _('Elapsed Time (minutes)'),
                'data': [
                    [s.starttime, round(max(0, s.elapsedtime) / 60, 2)]
                    for s in self.repo_obj.session_statistics[-self.limit :]
                ],
            }
        ]

    @property
    def errors(self):
        return [
            {
                'name': _('Error count'),
                'data': [[s.starttime, s.errors] for s in self.repo_obj.session_statistics[-self.limit :]],
            }
        ]


@cherrypy.tools.poppath()
class GraphPage(Controller):
    def __init__(self, graph) -> None:
        assert graph
        super().__init__()
        self.graph = graph

    @cherrypy.expose
    def default(self, path, limit='30', **kwargs):
        """
        Called to show every graphs
        """
        repo_obj = RepoObject.get_repo(path)
        limit = validate_int(limit)
        data = Data(repo_obj, limit)

        # Check if any action to process.
        params = {
            'repo': repo_obj,
            'graph': self.graph,
            'limit': limit,
            'data': data,
        }
        # Generate page.
        return self._compile_template("graphs_%s.html" % self.graph, **params)


@cherrypy.tools.errors(
    error_table={
        DoesNotExistError: 404,
        AccessDeniedError: 403,
    }
)
class GraphsPage(Controller):
    activities = GraphPage('activities')
    errors = GraphPage('errors')
    files = GraphPage('files')
    sizes = GraphPage('sizes')
    times = GraphPage('times')
