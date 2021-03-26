'''
Created on Mar. 23, 2021

@author: Patrik Dufresne <patrik@ikus-soft.com>
'''
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from cherrypy.process.plugins import SimplePlugin
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime

_logger = logging.getLogger(__name__)


class Scheduler(SimplePlugin):
    """
    Extends Cherrypy Monitor plugin to run jobs in background.
    """

    def __init__(self, bus, app):
        assert app
        self.app = app
        self._scheduler = BackgroundScheduler(
            jobstores={
                'default': MemoryJobStore(),
                'scheduled': MemoryJobStore(),
            },
            executors={
                'default': ThreadPoolExecutor(max_workers=10),
                'scheduled': ThreadPoolExecutor(max_workers=1),
            })
        super().__init__(bus)

    def start(self):
        """
        Start our own scheduler using AP scheduler.
        """
        # Start background thread
        self._scheduler.start()

    def stop(self):
        """
        Stop the scheduler.
        """
        self._scheduler.shutdown()

    def add_job(self, job):
        """
        Add the given scheduled job to the scheduler.
        
        The job must define a property `job_execution_time` defining when the
        job must run and a function `job_run` to be called.
        """
        assert job
        assert hasattr(job, 'job_execution_time')
        assert hasattr(job, 'job_run')
        hour, minute = job.job_execution_time.split(':', 2)
        self._scheduler.add_job(func=job.job_run, trigger='cron', hour=hour, minute=minute, jobstore='scheduled', executor='scheduled')

    def add_task(self, task):
        """
        Add the given task to be execute immediately in background.
        """
        assert hasattr(task, 'job_run') or hasattr(task, '__call__')
        func = getattr(task, 'job_run', task.__call__)
        self._scheduler.add_job(func=func, next_run_time=datetime.now())
