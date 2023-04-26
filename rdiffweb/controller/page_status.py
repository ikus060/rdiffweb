# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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

import datetime
import logging
import time

import cherrypy

from rdiffweb.controller import Controller, validate_int
from rdiffweb.controller.filter_authorization import is_admin
from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import UserObject
from rdiffweb.tools.i18n import ugettext as _

# Define the logger
logger = logging.getLogger(__name__)

DAYS_DEFAULT = 7
DAYS_MIN = 1
DAYS_MAX = 60

COUNT_DEFAULT = 10
COUNT_MIN = 1
COUNT_MAX = 20


class StatusPage(Controller):
    def _list_repo(self, username):
        # Check permissions before get list of repos.
        currentuser = cherrypy.serving.request.currentuser
        if currentuser.username == username:
            return currentuser.repo_objs
        # Make sure current user is admin before return list of repo.
        is_admin()
        userobj = UserObject.get_user(username)
        if not userobj:
            raise cherrypy.HTTPError(404)
        return userobj.repo_objs

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def per_days_json(self, path, days=DAYS_DEFAULT, **kwargs):
        """
        Count number of backup per days.
        """
        days = validate_int(days, min=DAYS_MIN, max=DAYS_MAX)

        # Release session lock
        cherrypy.session.release_lock()

        def _key(d):
            return time.strftime(str(d).split('T')[0])

        base = RdiffTime().replace(hour=0, minute=0, second=0) - datetime.timedelta(days=days)
        success = {_key(base + datetime.timedelta(days=i)): 0 for i in range(0, days + 1)}
        warning = success.copy()
        failed = success.copy()

        # Sum number of backup per days.
        for repo in self._list_repo(path):
            try:
                if len(repo.session_statistics):
                    for stat in repo.session_statistics[base:]:
                        key = _key(stat.date)
                        if key not in success:
                            continue
                        if stat.date == repo.last_backup_date and repo.status[0] != 'ok':
                            failed[key] = failed.get(key, 0) + 1
                        elif stat.errors:
                            warning[key] = warning.get(key, 0) + 1
                        else:
                            success[key] = success.get(key, 0) + 1
            except Exception:
                pass
        return [
            {'name': _('Success'), 'data': success},
            {'name': _('Warning'), 'data': warning},
            {'name': _('Failed'), 'data': failed},
        ]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def age_json(self, path, count=COUNT_DEFAULT, **kwargs):
        """
        Return the oldest backup.
        """

        # Release session lock
        cherrypy.session.release_lock()

        # Get data
        count = validate_int(count, min=COUNT_MIN, max=COUNT_MAX)
        now = RdiffTime()
        repos = sorted(self._list_repo(path), key=lambda r: (r.last_backup_date is None, r.last_backup_date))
        data = {}
        for repo in repos:
            try:
                if repo.last_backup_date:
                    delta = now.epoch - repo.last_backup_date.epoch
                    data[repo.display_name] = float('%.2g' % (delta / 60 / 60))
            except Exception:
                pass
            if len(data) >= count:
                break
        return [
            {'name': _('Hours since last backup'), 'data': data},
        ]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def disk_usage_json(self, path, **kwargs):
        """
        Return disk usage.
        """
        # Release session lock
        cherrypy.session.release_lock()

        data = {}
        for repo in self._list_repo(path):
            try:
                data[repo.display_name] = 0
                if len(repo.session_statistics):
                    size = repo.session_statistics[-1].sourcefilesize / 1024 / 1024
                    data[repo.display_name] = float('%.2g' % size)
            except Exception:
                pass
        # Sort from small to large
        return sorted(data.items(), key=lambda i: i[1], reverse=True)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def activities_json(self, path, days=DAYS_DEFAULT, count=COUNT_DEFAULT, sort=1, **kwargs):
        """
        Return list of repositories with less activities (new ,modified, deleted files).
        """
        days = validate_int(days, min=DAYS_MIN, max=DAYS_MAX)
        count = validate_int(count, min=COUNT_MIN, max=COUNT_MAX)
        sort = validate_int(sort)

        # Release session lock
        cherrypy.session.release_lock()

        from_date = RdiffTime() - datetime.timedelta(days=7)
        # Count activities per repository for the last X days
        new = {}
        modified = {}
        deleted = {}
        for repo in self._list_repo(path):
            try:
                new[repo.display_name] = 0
                modified[repo.display_name] = 0
                deleted[repo.display_name] = 0
                if len(repo.session_statistics):
                    for stats in repo.session_statistics[from_date:]:
                        new[repo.display_name] = stats.newfiles + new.get(repo.display_name, 0)
                        modified[repo.display_name] = stats.changedfiles + modified.get(repo.display_name, 0)
                        deleted[repo.display_name] = stats.deletedfiles + deleted.get(repo.display_name, 0)
            except Exception:
                pass

        # Sort by activities ascending (1) or descending (-1)
        def tot(x):
            return new[x[0]] + modified[x[0]] + deleted[x[0]]

        new = dict(sorted(list(new.items()), key=tot, reverse=sort < 0))
        modified = dict(sorted(list(modified.items()), key=tot, reverse=sort < 0))
        deleted = dict(sorted(list(deleted.items()), key=tot, reverse=sort < 0))
        # Limit
        new = dict(list(new.items())[0:count])
        modified = dict(list(modified.items())[0:count])
        deleted = dict(list(deleted.items())[0:count])
        return [
            {'name': _('New'), 'data': new},
            {'name': _('Deleted'), 'data': deleted},
            {'name': _('Modified'), 'data': modified},
        ]

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def elapsetime_json(self, path, days=DAYS_DEFAULT, count=COUNT_DEFAULT, **kwargs):
        """
        Return list of repositories with average elapse time (in minute).
        """
        days = validate_int(days, min=DAYS_MIN, max=DAYS_MAX)
        count = validate_int(count, min=COUNT_MIN, max=COUNT_MAX)
        from_date = RdiffTime() - datetime.timedelta(days=7)

        # Release session lock
        cherrypy.session.release_lock()

        data = {}
        for repo in self._list_repo(path):
            try:
                data[repo.display_name] = 0
                if len(repo.session_statistics):
                    data_points = []
                    for stats in repo.session_statistics[from_date:]:
                        data_points.append(stats.elapsedtime)
                    average = sum(data_points) / len(data_points) / 60
                    data[repo.display_name] = float('%.2g' % average)
            except Exception:
                pass
        # Sort
        data = dict(sorted(data.items(), key=lambda d: d[1], reverse=True))
        # Limit
        data = dict(list(data.items())[0:count])
        return [
            {'name': _('Average duration (min)'), 'data': data},
        ]

    @cherrypy.expose
    def index(self, path, days=DAYS_DEFAULT, count=COUNT_DEFAULT, **kwargs):
        days = validate_int(days, min=DAYS_MIN, max=DAYS_MAX)
        count = validate_int(count, min=COUNT_MIN, max=COUNT_MAX)
        repos = self._list_repo(path)
        params = {'days': days, 'count': count, 'path': path, 'repos': repos}
        return self._compile_template("status.html", **params)


StatusPage._cp_dispatch = cherrypy.popargs('path', handler=StatusPage())
