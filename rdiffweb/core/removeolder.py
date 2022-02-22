'''
Created on Mar. 23, 2021

@author: Patrik Dufresne <patrik@ikus-soft.com>
'''
import logging

from rdiffweb.core import librdiff

_logger = logging.getLogger(__name__)


def remove_older_job(app):
    """
    Execute the job.
    """
    # Create a generator to loop on repositories.
    # Loop on each repos.
    for repo in app.store.repos():
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
