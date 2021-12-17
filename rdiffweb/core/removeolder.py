'''
Created on Mar. 23, 2021

@author: Patrik Dufresne <patrik@ikus-soft.com>
'''
import logging

from rdiffweb.core import librdiff
from rdiffweb.core.config import Option

_logger = logging.getLogger(__name__)


class RemoveOlderJob():

    def __init__(self, app):
        assert app
        self.app = app

    _remove_older_time = Option('remove_older_time')

    @property
    def job_execution_time(self):
        return self._remove_older_time

    def job_run(self):
        """
        Execute the job.
        """
        # Create a generator to loop on repositories.
        # Loop on each repos.
        for repo in self.app.store.repos():
            try:
                self._remove_older(repo)
            except BaseException:
                _logger.exception("fail to remove older for user [%r] repo [%r]", repo.owner, repo)

    def _remove_older(self, repo):
        """
        Take action to remove older.
        """
        assert repo
        if repo.keepdays <= 0:
            return
        # Check history date.
        if not repo.last_backup_date:
            _logger.info("no backup dates for [%r]", repo.full_path)
            return
        d = librdiff.RdiffTime() - repo.last_backup_date
        d = d.days + repo.keepdays

        repo.remove_older(d)
