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

import datetime
import logging
import time

import cherrypy

from rdiffweb.controller import Controller
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.tools.i18n import ugettext as _

# Define the logger
logger = logging.getLogger(__name__)


@poppath()
class StatusPage(Controller):
    def _data(self, days):
        """
        Return number of backups per days including failure.
        """

        def _key(d):
            return time.strftime(str(d).split('T')[0])

        base = RdiffTime().set_time(0, 0, 0) - datetime.timedelta(days=days)
        # Creating empty data
        data = {_key(base + datetime.timedelta(days=i)): [] for i in range(0, days + 1)}
        success = {_key(base + datetime.timedelta(days=i)): 0 for i in range(0, days + 1)}
        failure = success.copy()

        # Sum number of backup per days.
        for repo in self.app.currentuser.repo_objs:
            try:
                if len(repo.session_statistics):
                    for stat in repo.session_statistics[base:]:
                        key = _key(stat.date)
                        if key not in success:
                            continue
                        success[key] = success.get(key, 0) + 1
                        data[key].append(stat)
                        if stat.errors:
                            failure[key] += 1
            except Exception:
                logger.warning('failure to read session statistics from %s', repo, exc_info=1)

        # Return data.
        return {
            'backup_count': [
                {'name': _('Successful Backup'), 'data': success},
                {'name': _('Backup with errors'), 'data': failure},
            ],
            'data': data,
        }

    @cherrypy.expose
    def default(self, limit=14):
        params = self._data(limit)
        return self._compile_template("status.html", **params)
