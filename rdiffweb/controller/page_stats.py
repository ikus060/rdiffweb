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


import cherrypy
from cherrypy_foundation.tools.i18n import ugettext as _

from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject

from . import validate_date


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
class StatsPage:
    @cherrypy.expose()
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    @cherrypy.tools.jinja2(template="stats.html")
    def default(self, path, date=None, **kwargs):
        """
        Show file statistics
        """
        date = validate_date(date, allow_none=True)
        # If Repo is broken
        repo_obj = RepoObject.get_repo(path)
        if repo_obj.status[0] == 'failed':
            return {'repo': repo_obj, 'date': date}

        # Check if date exists
        if date:
            try:
                repo_obj.file_statistics[date]
            except KeyError:
                raise cherrypy.HTTPError(404, _('Invalid date.'))

        # Provide list of available dates.
        source_dates = [{'value': str(f.date), 'display': str(f.date)} for f in repo_obj.file_statistics]

        return {'repo': repo_obj, 'date': date, 'source_dates': source_dates}

    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    @cherrypy.tools.json_out()
    def data_json(self, path, date=None, **kwargs):
        """
        Return a json array with stats
        """
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
