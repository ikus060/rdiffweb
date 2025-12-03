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

from datetime import datetime, timezone
from threading import Event

import cherrypy
from cherrypy.test import helper

from .. import scheduler  # noqa

done = Event()


def a_task(*args, **kwargs):
    done.set()


class SchedulerPluginTest(helper.CPWebCase):
    def setUp(self) -> None:
        done.clear()
        cherrypy.scheduler.remove_all_jobs()
        return super().setUp()

    def tearDown(self):
        return super().tearDown()

    @classmethod
    def setup_server(cls):
        pass

    def test_add_job(self):
        # Given a scheduled job
        scheduled = cherrypy.engine.publish(
            'scheduler:add_job',
            a_task,
            name='custom_name',
            args=(1, 2, 3),
            kwargs={'foo': 'bar'},
            next_run_time=datetime.now(timezone.utc),
            misfire_grace_time=None,
        )
        self.assertTrue(scheduled)
        self.assertEqual('custom_name', scheduled[0].name)
        # When waiting for all jobs
        cherrypy.scheduler.wait_for_jobs()
        # Then the job is done
        self.assertTrue(done.is_set())

    def test_add_job_daily(self):
        # Given a scheduler with a specific number of jobs
        count = len(cherrypy.scheduler.get_jobs())
        # When scheduling a daily job.
        scheduled = cherrypy.engine.publish('scheduler:add_job_daily', '23:00', a_task, 1, 2, 3, foo=1, bar=2)
        # Then the job is scheduled
        self.assertTrue(scheduled)
        self.assertEqual('a_task', scheduled[0].name)
        # Then the number of jobs increase.
        self.assertEqual(count + 1, len(cherrypy.scheduler.get_jobs()))

    def test_add_job_now(self):
        # Given a task
        # When scheduling that task
        scheduled = cherrypy.engine.publish('scheduler:add_job_now', a_task, 1, 2, 3, foo=1, bar=2)
        self.assertTrue(scheduled)
        # When waiting for all tasks
        cherrypy.scheduler.wait_for_jobs()
        # Then the task get called
        self.assertTrue(done.is_set())

    def test_remove_job(self):
        # Given a scheduler with a specific number of jobs
        count = len(cherrypy.scheduler.get_jobs())
        # Given a job schedule every seconds
        cherrypy.engine.publish('scheduler:add_job_daily', '23:00', a_task, 1, 2, 3, foo=1, bar=2)
        # Then number of job increase
        self.assertEqual(count + 1, len(cherrypy.scheduler.get_jobs()))
        # When the job is unscheduled.
        cherrypy.engine.publish('scheduler:remove_job', a_task)
        # Then the number of job decrease.
        self.assertEqual(count, len(cherrypy.scheduler.get_jobs()))

    def test_remove_job_with_invalid_job(self):
        # Given an unschedule job
        # When unscheduling an invalid job
        cherrypy.engine.publish('scheduler:remove_job', a_task)
        # Then an error is not raised.

    def test_remove_job_with_job_name(self):
        # Given a scheduled job
        count = len(cherrypy.scheduler.get_jobs())
        cherrypy.engine.publish('scheduler:add_job_daily', '23:00', f'{__name__}:a_task', 1, 2, 3, foo=1, bar=2)
        self.assertEqual(count + 1, len(cherrypy.scheduler.get_jobs()))
        # When unscheduling an invalid job
        cherrypy.engine.publish('scheduler:remove_job', f'{__name__}:a_task')
        # Then an error is not raised.
        self.assertEqual(count, len(cherrypy.scheduler.get_jobs()))
