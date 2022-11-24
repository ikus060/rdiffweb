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

"""
Created on Oct 17, 2015

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""
import time

import cherrypy
from cherrypy.test import helper

from .. import scheduler  # noqa


class SchedulerPluginTest(helper.CPWebCase):
    def setUp(self) -> None:
        self.called = False
        return super().setUp()

    @classmethod
    def setup_server(cls):
        pass

    def wait_for_tasks(self):
        time.sleep(1)
        while len(cherrypy.scheduler.list_tasks()) or cherrypy.scheduler.is_job_running():
            time.sleep(1)

    def test_schedule_job(self):
        # Given a scheduler with a specific number of jobs
        count = len(cherrypy.scheduler.list_jobs())

        # Given a job schedule every seconds
        def a_job(*args, **kwargs):
            self.called = True

        scheduled = cherrypy.engine.publish('schedule_job', '23:00', a_job, 1, 2, 3, foo=1, bar=2)
        self.assertTrue(scheduled)
        self.assertEqual(count + 1, len(cherrypy.scheduler.list_jobs()))

    def test_scheduler_task(self):
        # Given a task

        def a_task(*args, **kwargs):
            self.called = True

        # When scheduling that task
        scheduled = cherrypy.engine.publish('schedule_task', a_task, 1, 2, 3, foo=1, bar=2)
        self.assertTrue(scheduled)
        self.wait_for_tasks()
        # Then the task get called
        self.assertTrue(self.called)

    def test_unschedule_job(self):
        # Given a scheduler with a specific number of jobs
        count = len(cherrypy.scheduler.list_jobs())

        # Given a job schedule every seconds
        def a_job(*args, **kwargs):
            self.called = True

        cherrypy.engine.publish('schedule_job', '23:00', a_job, 1, 2, 3, foo=1, bar=2)
        self.assertEqual(count + 1, len(cherrypy.scheduler.list_jobs()))
        cherrypy.engine.publish('unschedule_job', a_job)
        self.assertEqual(count, len(cherrypy.scheduler.list_jobs()))

    def test_unschedule_job_with_invalid_job(self):
        # Given an unschedule job
        def a_job(*args, **kwargs):
            self.called = True

        # When unscheduling an invalid job
        cherrypy.engine.publish('unschedule_job', a_job)
        # Then no error are raised
