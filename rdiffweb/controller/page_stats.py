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

from rdiffweb.controller import Controller, validate_date, validate_int
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject
from rdiffweb.tools.i18n import ugettext as _


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


@cherrypy.tools.poppath()
class StatsPage(Controller):
    @cherrypy.expose()
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    def default(self, path, limit='10', date=None):
        """
        Called to show file statistics
        """
        limit = validate_int(limit)
        if date is not None:
            date = validate_date(date)

        # If Repo is broken
        repo_obj = RepoObject.get_repo(path)
        if repo_obj.status[0] == 'failed':
            params = {'repo': repo_obj, 'limit': limit, 'date': date}
            return self._compile_template("stats.html", **params)

        # Check if date exists
        if date:
            try:
                repo_obj.file_statistics[date]
            except KeyError:
                raise cherrypy.HTTPError(404, _('Invalid date.'))

        # Get file_statistics list
        if limit < len(repo_obj.file_statistics):
            file_statistics = repo_obj.file_statistics[: -limit - 1 : -1]
        else:
            file_statistics = repo_obj.file_statistics
        params = {'repo': repo_obj, 'limit': limit, 'date': date, 'file_statistics': file_statistics}
        return self._compile_template("stats.html", **params)

    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    @cherrypy.tools.json_out()
    def data_json(self, path, limit='10', date=None, **kwargs):
        """
        Create a json array with stats
        """
        limit = validate_int(limit)
        date = validate_date(date)

        # If Repo is broken return no data
        repo_obj = RepoObject.get_repo(path)
        if repo_obj.status[0] == 'failed':
            return {}

        # Check if date exists
        try:
            stat = repo_obj.file_statistics[date]
        except KeyError:
            raise cherrypy.HTTPError(404, _('Invalid date.'))

        return {
            'data': [
                [
                    line.path,
                    line_to_state(line),
                    line_to_size(line),
                    line.increment_size,
                ]
                for line in stat.readlines()
            ],
        }
