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

import datetime
import os
import subprocess
from collections import namedtuple

import cherrypy

from rdiffweb.controller import Controller, validate_int
from rdiffweb.core.config import Option


def _parse_access_log_date(value):
    """
    Return epoch from date formated as `[03/Feb/2023:10:07:22]`
    """
    try:
        date = datetime.datetime.strptime(value, "[%d/%b/%Y:%H:%M:%S]")
        return int(date.strftime('%s'))
    except ValueError:
        return value


def _parse_server_log_date(value):
    """
    Return epoch from date formated as `2023-02-07 15:06:59,943`
    """
    try:
        date = datetime.datetime.strptime(value, "%Y-%m-%d %H:%M:%S,%f")
        return float(date.strftime('%s.%f'))
    except ValueError:
        return value


LogRow = namedtuple('LogRow', ['filename', 'date', 'ip', 'username', 'description', 'tag'])


@cherrypy.tools.is_admin()
class AdminLogsPage(Controller):
    """
    Controller responsible to re-format the logs into usable Json format.
    """

    logfile = Option('log_file')
    logaccessfile = Option('log_access_file')

    def _get_log_files(self):
        """
        Return a list of log files to be shown in admin area.
        """
        return [fn for fn in [self.logfile, self.logaccessfile] if fn]

    def _tail(self, filename, limit):
        """
        Return a list of log files to be shown in admin area.
        """
        return subprocess.Popen(
            ['tail', '-n', str(limit), filename], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, encoding='utf-8'
        )

    def _parser_access_log(self, filename, limit):
        basename = os.path.basename(filename)
        with self._tail(filename, limit) as proc:
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                # Ignore line with wrong number of parts
                parts = line.split(' ', 4)
                if len(parts) != 5:
                    continue
                yield LogRow(
                    filename=basename,
                    date=_parse_access_log_date(parts[3]),
                    ip=parts[0].strip(),
                    username=parts[2] if parts[2] != '-' else 'anonymous',
                    description=parts[4].strip(),
                    tag=None,
                )

    def _parse_server_log(self, filename, limit):
        basename = os.path.basename(filename)
        with self._tail(filename, limit) as proc:
            entry = None
            while True:
                line = proc.stdout.readline()
                if not line:
                    break
                # Support multiline logs.
                if not line.startswith('[') and entry:
                    entry = entry._replace(description=entry.description + '\n' + line.rstrip('\n'))
                    continue
                if line.startswith('[') and entry:
                    yield entry
                parts = [p.lstrip('[') for p in line.split(']', 6)]
                # Ignore line with wrong number of parts
                if len(parts) != 7:
                    entry = None
                    continue
                # Tag entry using logger name
                tag = None
                if parts[5] in ['activity', 'auth', 'threat']:
                    tag = parts[5]
                elif parts[6].startswith(' TOOLS.RATELIMIT ratelimit access to'):
                    tag = 'threat'
                entry = LogRow(
                    filename=basename,
                    date=_parse_server_log_date(parts[0]),
                    ip=parts[2],
                    username=parts[3],
                    description=(parts[1].strip() + ' ' + parts[6].strip()),
                    tag=tag,
                )
            if entry:
                yield entry

    @cherrypy.expose
    def index(self):
        return self._compile_template("admin_logs.html")

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def data_json(self, limit='2000', **kwargs):
        """
        Return log file as json. To reduce the payload size we use one letter for the key.
        """
        # Release session lock
        cherrypy.session.release_lock()

        limit = validate_int(limit, min=1, max=5000)
        # List all log file.
        log_entries = []
        for filename in self._get_log_files():
            # Read the file line by line
            func = self._parser_access_log if filename == self.logaccessfile else self._parse_server_log
            for entry in func(filename, limit):
                log_entries.append(entry)
        return {'data': log_entries}
