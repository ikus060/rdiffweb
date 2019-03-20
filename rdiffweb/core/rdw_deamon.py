from __future__ import unicode_literals

import datetime
import logging
from rdiffweb.core import librdiff
from rdiffweb.core.rdw_spider_repos import find_repos_for_user
import time

from builtins import str
from cherrypy.process.plugins import Monitor

from rdiffweb.core.config import Option

_logger = logging.getLogger(__name__)


class Deamon(Monitor):
    """
    Extends the deamon plugin to run a job once a day at fixed time.

    Sub class should implement `job_execution_time` and `job_run`.
    """

    job_execution_time = '23:00'

    _next_execution_time = None
    
    def __init__(self, bus):
        Monitor.__init__(self, bus, self.deamon_run, frequency=60, name=self.__class__.__name__)

    def deamon_run(self):
        self._wait()
        # Run job.
        try:
            self.job_run()
        finally:
            self._next_execution_time = None

    def job_run(self):
        """
        Sub-class should implement this function.
        """
        raise NotImplementedError("job_run is not implemented")

    def _wait(self):
        """
        Sleep until time to execute the job.
        """
        now = datetime.datetime.now()
        t = self._get_next_execution_time()
        time.sleep((t - now).seconds)

    def _get_next_execution_time(self):
        """
        Return a date time representing the next execution time.
        """
        try:
            time_str = self.job_execution_time
            exec_time = datetime.datetime.strptime(time_str, '%H:%M')
        except:
            _logger.error("invalid execution time [%s], check your config. Using default value.", self.job_execution_time)
            exec_time = datetime.datetime.strptime("23:00", '%H:%M')

        now = datetime.datetime.now()
        exec_time = now.replace(hour=exec_time.hour, minute=exec_time.minute, second=0, microsecond=0)
        if exec_time < now:
            exec_time = exec_time + datetime.timedelta(days=1)
        return exec_time


class RemoveOlder(Deamon):

    _remove_older_time = Option('RemoveOlderTime', '23:00')

    def __init__(self, bus, app):
        self.app = app
        Deamon.__init__(self, bus);
        
    @property
    def job_execution_time(self):
        return self._remove_older_time

    def job_run(self):
        """
        Execute the job in background.
        """
        # Create a generator to loop on repositories.
        gen = (
            (user, repo, int(repo.keepdays))
            for user in self.app.userdb.list()
            for repo in user.repo_list
            if int(repo.keepdays) > 0)

        # Loop on each repos.
        for user, repo, keepdays in gen:
            try:
                self._remove_older(user, repo, keepdays)
            except BaseException:
                _logger.exception("fail to remove older for user [%r] repo [%r]", user, repo)

    def _remove_older(self, user, repo, keepdays):
        """
        Take action to remove older.
        """
        assert isinstance(keepdays, int)
        assert keepdays > 0
        # Get instance of the repo.
        r = librdiff.RdiffRepo(user.user_root, repo.name)
        # Check history date.
        if not r.last_backup_date:
            _logger.info("no backup dates for [%r]", r.full_path)
            return
        d = librdiff.RdiffTime() - r.last_backup_date
        d = d.days + keepdays

        _logger.info("execute rdiff-backup --force --remove-older-than=%sD %r", d, r.full_path)
        r.execute(b'--force',
                  b'--remove-older-than=' + str(d).encode(encoding='latin1') + b'D',
                  r.full_path)
        

class UpdateRepos(Deamon):
    """
    Plugin to refresh user repos.
    """

    def __init__(self, bus, app):
        self.app = app
        Deamon.__init__(self, bus);

    @property
    def deamon_frequency(self):
        """
        Return the frequency to update user repo. Default to 15min.
        """
        value = self.app.cfg.get_config_bool("autoUpdateRepos", "15")
        if value <= 0:
            value = 15
        return value * 60

    def deamon_run(self):
        """
        Refresh the user repository
        """
        try:

            for user in self.app.userdb.list():
                find_repos_for_user(user)

        except:
            _logger.exception("fail to update user repos")
