'''
Created on Mar. 23, 2021

@author: Patrik Dufresne <patrik@ikus-soft.com>
'''
import logging

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from rdiffweb.core import librdiff

_logger = logging.getLogger(__name__)


class RemoveOlder(SimplePlugin):

    execution_time = '23:00'

    def start(self):
        self.bus.log('Start RemoveOlder plugin')
        self.bus.publish('schedule_job', self.execution_time, self.remove_older_job)

    def stop(self):
        self.bus.log('Stop RemoveOlder plugin')
        self.bus.publish('unschedule_job', self.remove_older_job)

    @property
    def app(self):
        return cherrypy.tree.apps['']

    def remove_older_job(self):
        # Create a generator to loop on repositories.
        # Loop on each repos.
        for repo in self.app.store.repos():
            try:
                if repo.keepdays <= 0:
                    return
                # Check history date.
                if not repo.last_backup_date:
                    _logger.info("no backup dates for [%r]", repo.full_path)
                    return
                d = librdiff.RdiffTime() - repo.last_backup_date
                d = d.days + repo.keepdays
                repo.remove_older(d)
            except BaseException:
                _logger.exception("fail to remove older for user [%r] repo [%r]", repo.owner, repo)


cherrypy.remove_older = RemoveOlder(cherrypy.engine)
cherrypy.remove_older.subscribe()

cherrypy.config.namespaces['remove_older'] = lambda key, value: setattr(cherrypy.remove_older, key, value)
