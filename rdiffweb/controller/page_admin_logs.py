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

import os
import subprocess

import cherrypy
from cherrypy.lib.static import serve_file

from rdiffweb.controller import Controller, validate_int


@cherrypy.tools.is_admin()
class AdminLogsPage(Controller):
    """
    Controller responsible to re-format the logs into usable Json format.
    """

    def _get_log_files(self):
        cfg = cherrypy.tree.apps[''].cfg
        return_value = {}
        if cfg.log_file:
            return_value['log_file'] = os.path.abspath(cfg.log_file)
        if cfg.log_access_file:
            return_value['log_access_file'] = os.path.abspath(cfg.log_access_file)
        return return_value

    def _tail(self, filename, limit, encoding='utf-8'):
        """
        Return a list of log files to be shown in admin area.
        """
        return subprocess.check_output(
            ['tail', '-n', str(limit), filename], stderr=subprocess.STDOUT, encoding=encoding, errors='replace'
        )

    @cherrypy.expose
    def index(self, name=None, limit='2000'):
        """
        Show server logs.
        """
        limit = validate_int(limit, min=1, max=20000)

        # Validate filename
        log_files = self._get_log_files()
        if name is not None and name not in log_files:
            raise cherrypy.NotFound()

        # Read file
        data = None
        if name:
            filename = log_files[name]
            try:
                data = self._tail(filename, limit)
            except subprocess.CalledProcessError:
                data = ''

        return self._compile_template("admin_logs.html", log_files=log_files, name=name, limit=limit, data=data)

    @cherrypy.expose
    @cherrypy.tools.response_headers(headers=[('Content-Type', 'text/plain')])
    def raw(self, name=None):
        """
        Download full server logs.
        """
        # Validate filename
        log_files = self._get_log_files()
        if name not in log_files:
            raise cherrypy.NotFound()
        filename = log_files[name]

        # Release session lock
        cherrypy.session.release_lock()

        # Return log file
        return serve_file(filename, content_type="text/plain", disposition=True)
