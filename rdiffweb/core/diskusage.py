# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2026 rdiffweb contributors
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

import logging
import os
import shutil
import subprocess
import threading
from datetime import datetime, timedelta, timezone

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from rdiffweb.core.model import DiskUsage, RepoObject

CONTEXT = 'DISKUSAGE'


class DiskUsagePlugin(SimplePlugin):
    """
    Periodically scan backup storage and update disk usage for each repository
    using the `du` command-line tool. The scan is run with `nice` and `ionice`
    when available to reduce its impact on system resources.
    """

    execution_time = '02:00'

    # `nice` CPU priority level (0-19, higher means lower priority)
    nice_level = 19

    # `ionice` class: 1=realtime, 2=best-effort, 3=idle
    ionice_class = 3

    _lock = threading.Lock()

    def start(self):
        self.bus.log('Start DiskUsage plugin')
        self.bus.publish('scheduler:add_job_daily', self.execution_time, self._disk_usage_job)
        # Start the background process if disk usage is empty.
        if DiskUsage.query.first() is None:
            self.bus.publish('scheduler:add_job_now', self._disk_usage_job)

    def stop(self):
        self.bus.log('Stop DiskUsage plugin')
        self.bus.publish('scheduler:remove_job', self._disk_usage_job)

    def graceful(self):
        self.stop()
        self.start()

    def _scan_disk_usage(self, path):
        """
        Use `du` to scan all folder recursively to get the disk usage.
        """
        cmd = []

        ionice = shutil.which(b'ionice')
        if ionice:
            cmd += [ionice, b'-c', str(self.ionice_class).encode()]

        nice = shutil.which(b'nice')
        if nice:
            cmd += [nice, b'-n', str(self.nice_level).encode()]

        cmd += [b'du', b'--block-size=1', path]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
        except OSError as e:
            cherrypy.log(f'failed to start du for path {path!r}: {e}', severity=logging.ERROR, context=CONTEXT)
            return

        for line in process.stdout:
            line = line.rstrip(b'\n')
            parts = line.split(b'\t', 1)
            if len(parts) == 2:
                size_str, subpath = parts
                try:
                    yield int(size_str), subpath
                except ValueError:
                    cherrypy.log(f'unexpected du output line {line!r}', severity=logging.WARNING, context=CONTEXT)
            else:
                cherrypy.log(f'du unexpected output: {line!r}', severity=logging.WARNING, context=CONTEXT)

        process.wait()
        if process.returncode != 0:
            cherrypy.log(
                f'du failed for path {path!r} (exit {process.returncode})', severity=logging.ERROR, context=CONTEXT
            )

    def _update_disk_usage(sefl, repo_obj, logical_path, **kwargs):
        with cherrypy.db.session.begin():
            # Try to update first (most common case)
            rows_updated = DiskUsage.query.filter_by(repoid=repo_obj.id, logical_path=logical_path).update(kwargs)
            # If no row was updated, insert a new one
            if not rows_updated:
                DiskUsage(repoid=repo_obj.id, logical_path=logical_path, **kwargs).add()

    def _delete_disk_usage_older_than(self, repo_obj, cutoff: datetime):
        with cherrypy.db.session.begin():
            DiskUsage.query.filter(
                DiskUsage.repoid == repo_obj.id,
                DiskUsage.last_updated < cutoff,
            ).delete()

    def _disk_usage_job(self):
        # Skip execution if a scan is already running
        if not self._lock.acquire(blocking=False):
            cherrypy.log('disk usage scan already running, skipping', context=CONTEXT)
            return

        try:
            self._run_disk_usage_scan()
        finally:
            self._lock.release()

    def _run_disk_usage_scan(self):
        cherrypy.log('starting disk usage scan', context=CONTEXT)

        with cherrypy.db.session.begin():
            repos = RepoObject.query.all()
            cherrypy.db.session.expunge_all()

        # Loop on each repo
        for repo_obj in repos:
            repo_path = repo_obj.full_path
            increments_prefix = os.path.join(repo_path, b'rdiff-backup-data', b'increments')
            cherrypy.log(f'scanning disk usage for repository {repo_path!r}', context=CONTEXT)
            scan_start = datetime.now(tz=timezone.utc) - timedelta(seconds=1)
            try:
                # Scan files to get disk usage with "du"
                for size, subpath in self._scan_disk_usage(repo_path):
                    try:
                        if subpath.startswith(increments_prefix):
                            logical_path = os.path.relpath(subpath, increments_prefix)
                            self._update_disk_usage(repo_obj, logical_path, increments_size=size)
                        else:
                            logical_path = os.path.relpath(subpath, repo_path)
                            if logical_path.startswith(b'rdiff-backup-data'):
                                continue
                            self._update_disk_usage(repo_obj, logical_path, mirror_size=size)
                    except Exception as e:
                        cherrypy.log(
                            f'failed to update disk usage for folder {subpath!r}: {e}',
                            severity=logging.ERROR,
                            traceback=True,
                            context=CONTEXT,
                        )

                # Delete stale rows not touched during this scan
                self._delete_disk_usage_older_than(repo_obj, scan_start)
                cherrypy.log(f'disk usage updated for repository {repo_path!r}', context=CONTEXT)

            except Exception as e:
                cherrypy.log(
                    f'failed to update disk usage for repository {repo_path!r}: {e}',
                    severity=logging.ERROR,
                    traceback=True,
                    context=CONTEXT,
                )
            finally:
                cherrypy.db.session.rollback()

        cherrypy.log('disk usage scan completed', context=CONTEXT)


cherrypy.disk_usage = DiskUsagePlugin(cherrypy.engine)
cherrypy.disk_usage.subscribe()

cherrypy.config.namespaces['disk_usage'] = lambda key, value: setattr(cherrypy.disk_usage, key, value)
