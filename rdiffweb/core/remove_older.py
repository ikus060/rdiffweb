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

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from rdiffweb.core import librdiff
from rdiffweb.core.model import RepoObject

_logger = logging.getLogger(__name__)


class RemoveOlder(SimplePlugin):
    execution_time = '23:00'

    def start(self):
        self.bus.log('Start RemoveOlder plugin')
        self.bus.publish('schedule_job', self.execution_time, self.remove_older_job)

    start.priority = 55

    def stop(self):
        self.bus.log('Stop RemoveOlder plugin')
        self.bus.publish('unschedule_job', self.remove_older_job)

    stop.priority = 45

    def remove_older_job(self):
        # Create a generator to loop on repositories.
        # Loop on each repos.
        for repo in RepoObject.query.filter(RepoObject.keepdays > 0).all():
            try:
                # Check history date.
                if not repo.last_backup_date:
                    _logger.info("no backup dates for [%r]", repo.full_path)
                    continue
                d = librdiff.RdiffTime() - repo.last_backup_date
                d = d.days + repo.keepdays
                repo.remove_older(d)
            except Exception:
                _logger.exception("fail to remove older for user [%r] repo [%r]", repo.owner, repo)


cherrypy.remove_older = RemoveOlder(cherrypy.engine)
cherrypy.remove_older.subscribe()

cherrypy.config.namespaces['remove_older'] = lambda key, value: setattr(cherrypy.remove_older, key, value)
