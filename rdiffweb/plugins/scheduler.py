# -*- coding: utf-8 -*-
# Scheduler plugins for Cherrypy
# Copyright (C) 2022 IKUS Software
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

'''
Created on Mar. 23, 2021

@author: Patrik Dufresne <patrik@ikus-soft.com>
'''
import logging
from datetime import datetime

import cherrypy
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED, EVENT_JOB_SUBMITTED
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from cherrypy.process.plugins import SimplePlugin

logger = logging.getLogger(__name__)


def catch_exception(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        finally:
            cherrypy.tools.db.on_end_resource()

    wrapper._func = func
    return wrapper


class Scheduler(SimplePlugin):
    """
    Plugins to run Job at fixed time (cronjob) and to schedule task to be run on by one.
    """

    def __init__(self, bus):
        super().__init__(bus)
        self._scheduler = self._create_scheduler()
        self._scheduler.start(paused=True)
        self._scheduler.add_listener(self._job_submitted, EVENT_JOB_SUBMITTED)
        self._scheduler.add_listener(self._job_finish, (EVENT_JOB_EXECUTED | EVENT_JOB_ERROR))
        self._running = []

    def _job_submitted(self, event):
        self._running.append(event.job_id)

    def _job_finish(self, event):
        if event.job_id in self._running:
            self._running.remove(event.job_id)

    def _create_scheduler(self):
        return BackgroundScheduler(
            jobstores={
                'default': MemoryJobStore(),
                'scheduled': MemoryJobStore(),
            },
            executors={
                'default': ThreadPoolExecutor(max_workers=10),
                'scheduled': ThreadPoolExecutor(max_workers=1),
            },
        )

    def start(self):
        self.bus.log('Start Scheduler plugins')
        self._scheduler.resume()
        self.bus.subscribe('schedule_job', self.schedule_job)
        self.bus.subscribe('schedule_task', self.schedule_task)
        self.bus.subscribe('unschedule_job', self.unschedule_job)

    def stop(self):
        self.bus.log('Stop Scheduler plugins')
        self._scheduler.pause()
        self.bus.unsubscribe('schedule_job', self.schedule_job)
        self.bus.unsubscribe('unschedule_job', self.unschedule_job)
        self.bus.unsubscribe('schedule_task', self.schedule_task)

    def exit(self):
        # Shutdown scheduler and create a new one in case the engine get started again.
        self._scheduler.shutdown(wait=True)
        self._scheduler = self._create_scheduler()
        self._scheduler.start(paused=True)

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

    def is_job_running(self):
        return self._running

    def schedule_job(self, execution_time, job, *args, **kwargs):
        """
        Add the given scheduled job to the scheduler.
        """
        assert hasattr(job, '__call__'), 'job must be callable'
        hour, minute = execution_time.split(':', 2)
        self._scheduler.add_job(
            func=catch_exception(job),
            name=job.__name__,
            args=args,
            kwargs=kwargs,
            trigger='cron',
            hour=hour,
            minute=minute,
            jobstore='scheduled',
            executor='scheduled',
        )

    def schedule_task(self, task, *args, **kwargs):
        """
        Add the given task to be execute immediately in background.
        """
        assert hasattr(task, '__call__'), 'task must be callable'
        self._scheduler.add_job(
            func=catch_exception(task),
            name=task.__name__,
            args=args,
            kwargs=kwargs,
            next_run_time=datetime.now(),
        )

    def unschedule_job(self, job):
        """
        Remove the given job from scheduler.
        """
        # Search for a matching job
        job_id = next((j.id for j in self._scheduler.get_jobs(jobstore='scheduled') if j.func._func == job), None)
        if job_id:
            self._scheduler.remove_job(job_id=job_id, jobstore='scheduled')


# Register Scheduler plugin
cherrypy.scheduler = Scheduler(cherrypy.engine)
cherrypy.scheduler.subscribe()

cherrypy.config.namespaces['scheduler'] = lambda key, value: setattr(cherrypy.scheduler, key, value)
