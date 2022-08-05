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
import os
import subprocess
from collections import OrderedDict

import cherrypy

from rdiffweb.controller import Controller
from rdiffweb.core.config import Option


@cherrypy.tools.is_admin()
class AdminLogsPage(Controller):
    logfile = Option('log_file')
    logaccessfile = Option('log_access_file')

    def _get_log_files(self):
        """
        Return a list of log files to be shown in admin area.
        """
        return [fn for fn in [self.logfile, self.logaccessfile] if fn]

    def _get_log_data(self, fn, num=2000):
        """
        Return a list of log files to be shown in admin area.
        """
        try:
            return subprocess.check_output(['tail', '-n', str(num), fn], stderr=subprocess.STDOUT).decode('utf-8')
        except Exception:
            logging.exception('fail to get log file content')
            return "Error getting file content"

    @cherrypy.expose
    def default(self, filename=u""):
        # get list of log file available.
        data = ""
        logfiles = OrderedDict([(os.path.basename(fn), fn) for fn in self._get_log_files()])
        if logfiles:
            filename = filename or list(logfiles.keys())[0]
            if filename not in logfiles:
                raise cherrypy.HTTPError(404, 'invalid log file: ' + filename)
            data = self._get_log_data(logfiles.get(filename))

        params = {
            "filename": filename,
            "logfiles": logfiles.keys(),
            "data": data,
        }
        return self._compile_template("admin_logs.html", **params)
