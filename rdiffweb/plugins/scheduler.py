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
        self.bus.subscribe('schedule_job', self.schedule_job)
        self.bus.subscribe('schedule_task', self.schedule_task)

    def stop(self):
        self.bus.log('Stop Scheduler')
        self._scheduler.pause()
        self.bus.unsubscribe('schedule_job', self.schedule_job)
        self.bus.unsubscribe('schedule_task', self.schedule_task)

    def exit(self):
        # Shutdown scheduler and create a new one in case the engine get started again.
        self._scheduler.shutdown(wait=True)
        self._scheduler = self._create_scheduler()
        self._scheduler.start(paused=True)

    def schedule_job(self, execution_time, job, *args, **kwargs):
        """
        Add the given scheduled job to the scheduler.
        """
        assert hasattr(job, '__call__'), 'job must be callable'
        hour, minute = execution_time.split(':', 2)
        self._scheduler.add_job(func=job, args=args, kwargs=kwargs, trigger='cron', hour=hour, minute=minute, jobstore='scheduled', executor='scheduled')

    def schedule_task(self, task, *args, **kwargs):
        """
        Add the given task to be execute immediately in background.
        """
        assert hasattr(task, '__call__'), 'task must be callable'
        self._scheduler.add_job(func=task, args=args, kwargs=kwargs, next_run_time=datetime.now())

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
