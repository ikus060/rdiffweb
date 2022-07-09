# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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
from cherrypy.lib.static import serve_fileobj

from rdiffweb.controller import Controller, validate_date, validate_int
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject
from rdiffweb.tools.i18n import ugettext as _

# Define the logger
logger = logging.getLogger(__name__)


@poppath()
class LogsPage(Controller):
    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    def default(self, path, limit='10', date=None, file=None, raw=0):
        """
        Called to show every graphs
        """
        limit = validate_int(limit)
        if date is not None:
            date = validate_date(date)
        raw = validate_int(raw)

        repo_obj = RepoObject.get_repo(path)
        if repo_obj.status[0] == 'failed':
            params = {'repo': repo_obj, 'limit': limit, 'date': date, 'file': file, 'data': '', 'error_logs': []}
            return self._compile_template("logs.html", **params)

        # Read log file data
        if file == 'backup.log':
            entry = repo_obj.backup_log
        elif file == 'restore.log':
            entry = repo_obj.restore_log
        elif date:
            try:
                entry = repo_obj.error_log[date]
            except KeyError:
                raise cherrypy.HTTPError(404, _('Invalid date.'))
        else:
            entry = None

        try:
            data = None
            if raw:
                return serve_fileobj(entry._open(), content_type="text/plain")
            elif entry:
                # Limit to 2000 lines in html page.
                data = entry.tail()
        except FileNotFoundError:
            # If the file doesn't exists, swallow the error.
            pass

        # Get error log list
        if limit < len(repo_obj.error_log):
            error_logs = repo_obj.error_log[: -limit - 1 : -1]
        else:
            error_logs = repo_obj.error_log

        params = {'repo': repo_obj, 'limit': limit, 'date': date, 'file': file, 'data': data, 'error_logs': error_logs}
        return self._compile_template("logs.html", **params)
