# Scheduler plugins for Cherrypy
# Copyright (C) 2025 IKUS Software
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
import copy
import logging
from datetime import datetime, timezone
from functools import wraps
from threading import Event, RLock

import cherrypy
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_SUBMITTED
from apscheduler.schedulers.background import BackgroundScheduler
from cherrypy.process.plugins import SimplePlugin

logger = logging.getLogger(__name__)


def clear_db_sessions(func):
    """
    A decorator that ensures database connections that have become unusable, or are obsolete, are closed
    before and after the job is executed.
    """

    @wraps(func)
    def func_wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        finally:
            cherrypy.db.clear_sessions()
        return result

    return func_wrapper


class Scheduler(SimplePlugin):
    """
    Plugins to run Job at fixed time (cronjob) and to schedule task to be run on by one.

    Configuration:
    - jobstore. Take value 'memory' (default), 'db' to use SQLalchemy database in combination with cherrypy.db. Or any callable function to create an instance of BaseJobStore
    """

    jobstores = {"default": {"type": "memory"}}
    executors = {"default": {"type": "threadpool", "max_workers": 10}}
    job_defaults = {"coalesce": False, "max_instances": 1}
    timezone = None

    def __init__(self, bus):
        super().__init__(bus)
        self._scheduler = None
        # Let keep track of running jobs manually.
        # This is required for unit testing to wait for all running task.
        self._lock = RLock()
        self._event = Event()
        self._submitted_jobs = set()
        self._completed_jobs = set()

    @property
    def _running_jobs(self):
        with self._lock:
            return self._submitted_jobs

    def _track_running_jobs(self, event):
        """
        This listener keep track of running jobs.
        This is required to implement wait for tasks mostly used during unit testing.
        """
        with self._lock:
            # Special care must be taken to handle race condition
            # the EVENT_JOB_EXECUTED may get called before EVENT_JOB_SUBMITTED
            if event.code == EVENT_JOB_SUBMITTED:
                if event.job_id in self._completed_jobs:
                    self._completed_jobs.remove(event.job_id)
                else:
                    self._submitted_jobs.add(event.job_id)
            elif event.code in (EVENT_JOB_EXECUTED, EVENT_JOB_ERROR):
                if event.job_id in self._submitted_jobs:
                    self._submitted_jobs.remove(event.job_id)
                else:
                    self._completed_jobs.add(event.job_id)
            # Wakeup wait_for_tasks.
            self._event.set()

    def _drop_table(self, target, conn, **kwargs):
        """
        Callback listener to drop table.
        This is required because SQLAlchemyJobStore creates the table manually.
        """
        from sqlalchemy.sql import ddl

        # Here we need to use private API to loop over all sqlalchemy job store.
        for jobstore in self._scheduler._jobstores.values():
            table = getattr(jobstore, 'jobs_t', None)
            if table is not None:
                conn.execute(ddl.DropTable(table, if_exists=True))

    def _create_table(self, target, conn, **kwargs):
        """
        Callback listener to drop table.
        This is required because SQLAlchemyJobStore creates the table manually.
        """
        from sqlalchemy.sql import ddl

        # Here we need to use private API to loop over all sqlalchemy job store.
        for jobstore in self._scheduler._jobstores.values():
            table = getattr(jobstore, 'jobs_t', None)
            if table is not None:
                conn.execute(ddl.CreateTable(table, if_not_exists=True))

    def _db_events(self, listen_or_remove):
        """
        Listen on database events to create and drop tables as required.
        """
        assert listen_or_remove in ['listen', 'remove']
        try:
            from sqlalchemy import event

            if getattr(cherrypy, 'db', False):
                base = cherrypy.db.get_base()
                func = getattr(event, listen_or_remove)
                func(base.metadata, 'after_drop', self._drop_table)
                func(base.metadata, 'after_create', self._create_table)
        except ImportError:
            # Nothing to do if sqlalchemy is not available
            pass

    def _create_scheduler(self):
        """
        Create a new APScheduler base on plugin configuration.
        """
        # Create the scheduler with deepcopy of configuration.
        scheduler = BackgroundScheduler(
            jobstores=copy.deepcopy(self.jobstores),
            executors=copy.deepcopy(self.executors),
            job_defaults=copy.deepcopy(self.job_defaults),
            timezone=self.timezone,
        )
        # Add listener to keep track of running jobs.
        scheduler.add_listener(self._track_running_jobs, (EVENT_JOB_EXECUTED | EVENT_JOB_ERROR | EVENT_JOB_SUBMITTED))
        # Start the scheduler.
        scheduler.start()
        return scheduler

    def start(self):
        self.bus.log('Start Scheduler plugin')
        # Create apscheduler
        self._scheduler = self._create_scheduler()
        # Register drop_table event (when using database)
        self._db_events('listen')
        # Then register new channels
        self.bus.subscribe('scheduler:add_job', self.add_job)
        self.bus.subscribe('scheduler:add_job_daily', self.add_job_daily)
        self.bus.subscribe('scheduler:add_job_now', self.add_job_now)
        self.bus.subscribe('scheduler:remove_job', self.remove_job)

    # Slightly lower priority to start after database, but before other plugins.
    start.priority = 49

    def stop(self):
        self.bus.log('Stop Scheduler plugin')
        # Unregister drop_table event (when using database)
        self._db_events('remove')
        # Shutdown the scheduler & wait for running task to complete.
        if self._scheduler:
            self._scheduler.shutdown(wait=True)
            self._scheduler = None
        self.bus.unsubscribe('scheduler:add_job', self.add_job)
        self.bus.unsubscribe('scheduler:add_job_daily', self.add_job_daily)
        self.bus.unsubscribe('scheduler:add_job_now', self.add_job_now)
        self.bus.unsubscribe('scheduler:remove_job', self.remove_job)

    stop.priority = 51

    def graceful(self):
        """Reload of subscribers."""
        self.stop()
        self.start()

    def add_job(self, func, *args, **kwargs):
        """
        Called via engine.publish('scheduler:add_job', ...)
        OR directly on the plugin instance.
        """
        if not self._scheduler:
            raise RuntimeError("Scheduler not running; cannot add job.")

        return self._scheduler.add_job(func, *args, **kwargs)

    def add_job_daily(self, execution_time, func, *args, **kwargs):
        """
        A convenience wrapper around add_job() that ensures
        the job runs daily.
        """
        hour, minute = execution_time.split(':', 2)
        return self.add_job(
            id=getattr(func, '__name__', str(func)),
            func=func,
            name=getattr(func, '__name__', str(func)),
            args=args,
            kwargs=kwargs,
            trigger='cron',
            hour=hour,
            minute=minute,
            misfire_grace_time=None,
            coalesce=True,
            replace_existing=True,
        )

    def add_job_now(self, func, *args, **kwargs):
        """
        A convenience wrapper around add_job() that ensures
        the job runs immediately upon being added.
        """
        return self.add_job(
            func=func,
            name=getattr(func, '__name__', str(func)),
            args=args,
            kwargs=kwargs,
            next_run_time=datetime.now(timezone.utc),
            misfire_grace_time=None,
        )

    def get_jobs(self, jobstore=None):
        """
        Return list of scheduled jobs.
        """
        if not self._scheduler:
            raise RuntimeError("Scheduler not running; cannot get jobs.")
        return self._scheduler.get_jobs(jobstore=jobstore)

    def remove_job(self, job, jobstore=None):
        """
        Remove the given job from scheduler.
        """
        # Search for a matching job
        return_value = False
        if self._scheduler is None:
            return return_value
        for j in self._scheduler.get_jobs(jobstore=jobstore):
            if j.func == job or j.name == job:
                self._scheduler.remove_job(job_id=j.id, jobstore=jobstore)
                return_value = True
        return return_value

    def remove_all_jobs(self, jobstore=None):
        """
        Remove all jobs from scheduler.
        """
        if self._scheduler is None:
            return
        self._scheduler.remove_all_jobs(jobstore=jobstore)

    def wait_for_jobs(self, jobstore=None):
        """
        Used to wait for all running jobs to complete.
        """
        if self._scheduler is None:
            return
        # Wait until the queue is empty.
        while any(
            job for job in self._scheduler.get_jobs(jobstore=jobstore) if job.next_run_time < datetime.now(timezone.utc)
        ):
            self._event.wait(timeout=1)
            self._event.clear()
        # Wait until all jobs are completed.
        while self._running_jobs:
            self._event.wait(timeout=1)
            self._event.clear()


# Register Scheduler plugin
cherrypy.scheduler = Scheduler(cherrypy.engine)
cherrypy.scheduler.subscribe()

cherrypy.config.namespaces['scheduler'] = lambda key, value: setattr(cherrypy.scheduler, key, value)
