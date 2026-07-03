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

import logging
from urllib.parse import unquote_to_bytes

import cherrypy
from cherrypy.lib.static import serve_fileobj

from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject

from . import validate_date

# Define the logger
logger = logging.getLogger(__name__)


class LogsPage:

    def _cp_dispatch(self, vpath):
        """
        Return the right handle if raw=1
        """
        func = self._raw if 'raw=1' in cherrypy.request.query_string else self._page
        cherrypy.serving.request.params = {
            'path': b"/".join([unquote_to_bytes(segment.encode('ISO-8859-1')) for segment in vpath])
        }
        vpath.clear()
        return func

    def _get_log_entry(self, repo_obj, date, file):
        if repo_obj.status[0] == 'broken':
            return None

        # Read log file data
        if date:
            try:
                return repo_obj.error_log[date]
            except KeyError:
                raise cherrypy.HTTPError(404, 'invalid date')
        elif file == 'backup.log':
            return repo_obj.backup_log
        elif file == 'restore.log':
            return repo_obj.restore_log
        else:
            raise cherrypy.HTTPError(404, 'invalid file')

    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    @cherrypy.tools.jinja2(template="logs.html")
    def _page(self, path, date=None, file=None, **kwargs):
        """
        Show repository backup and restore logs
        """
        repo_obj = RepoObject.get_repo(path)
        date = validate_date(date, allow_none=True)
        # Default to backup.log
        if file is None and date is None:
            file = 'backup.log'
        entry = self._get_log_entry(repo_obj, date, file)
        data = None
        try:
            if entry:
                data = entry.tail()
        except FileNotFoundError:
            # If the file doesn't exists, swallow the error.
            pass

        return {'repo': repo_obj, 'date': date, 'file': file, 'data': data}

    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    def _raw(self, path, date=None, file=None, **kwargs):
        repo_obj = RepoObject.get_repo(path)
        date = validate_date(date, allow_none=True)
        entry = self._get_log_entry(repo_obj, date, file)
        try:
            return serve_fileobj(entry._open(), content_type="text/plain")
        except FileNotFoundError:
            return cherrypy.HTTPError(404)

    _raw._cp_config = {"response.stream": True}
