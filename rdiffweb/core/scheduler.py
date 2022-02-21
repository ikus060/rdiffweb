'''
Created on Mar. 23, 2021

@author: Patrik Dufresne <patrik@ikus-soft.com>
'''
import cherrypy
from apscheduler.schedulers.background import BackgroundScheduler
from cherrypy.process.plugins import SimplePlugin
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from datetime import datetime


class Scheduler(SimplePlugin):
    """
    Extends Cherrypy Monitor plugin to run jobs in background.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self._scheduler = self._create_scheduler()
        self._scheduler.start(paused=True)

    def _create_scheduler(self):
        return BackgroundScheduler(
            jobstores={
                'default': MemoryJobStore(),
                'scheduled': MemoryJobStore(),
            },
            executors={
                'default': ThreadPoolExecutor(max_workers=10),
                'scheduled': ThreadPoolExecutor(max_workers=1),
            })

    def start(self):
        self.bus.log('Start Scheduler')
        self._scheduler.resume()
        cherrypy.engine.subscribe('schedule_task', self.add_task)
        cherrypy.engine.subscribe('schedule_job', self.add_job)

    def stop(self):
        self.bus.log('Stop Scheduler')
        self._scheduler.pause()
        cherrypy.engine.unsubscribe('schedule_task', self.add_task)
        cherrypy.engine.unsubscribe('schedule_job', self.add_job)

    def exit(self):
        # Shutdown scheduler and create a new one in case the engine get started again.
        self._scheduler.shutdown(wait=True)
        self._scheduler = self._create_scheduler()
        self._scheduler.start(paused=True)

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

    def add_task(self, task, args=(), kwargs={}):
        """
        Add the given task to be execute immediately in background.
        """
        assert hasattr(task, 'job_run') or hasattr(task, '__call__')
        func = getattr(task, 'job_run', task)
        self._scheduler.add_job(func=func, args=args, kwargs=kwargs, next_run_time=datetime.now())

    def list_jobs(self):
        """
        Return list of scheduled jobs.
        """
        return self._scheduler.get_jobs(jobstore='scheduled')

    def list_tasks(self):
        """
        Return list of tasks.
        """
        return self._scheduler.get_jobs(jobstore='default')


# Register Scheduler plugin
cherrypy.scheduler = Scheduler(cherrypy.engine)
cherrypy.scheduler.subscribe()

cherrypy.config.namespaces['scheduler'] = lambda key, value: setattr(cherrypy.scheduler, key, value)
