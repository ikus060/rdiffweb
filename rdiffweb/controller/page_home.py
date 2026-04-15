# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
from collections import Counter
from datetime import timedelta

import cherrypy

from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import UserObject

# Define the logger
logger = logging.getLogger(__name__)


class HomePage:

    @cherrypy.expose
    @cherrypy.tools.jinja2(template="home.html")
    def default(self, username=None):
        """
        Shows repositories of current user
        """
        # Redirect user to it-self if not defined.
        if username is None:
            currentuser = cherrypy.serving.request.currentuser
            raise cherrypy.HTTPRedirect(currentuser.username)

        # Check permissions before returning list of repos.
        currentuser = cherrypy.serving.request.currentuser
        if currentuser.username == username:
            userobj = currentuser
        elif currentuser.is_admin:
            userobj = UserObject.get_user(username)
        else:
            raise cherrypy.HTTPError(403)

        # Refresh user repo
        if userobj.refresh_repos():
            userobj.commit()

        repo_objs = list(userobj.repo_objs)
        status_counts = Counter(r.status[0] for r in repo_objs)

        # Safely get last backup among repos with a valid backup date and ok/in_progress status
        eligible_repos = [r for r in repo_objs if r.last_backup_date and r.status[0] in ['ok', 'in_progress']]
        last_backup = min(eligible_repos, key=lambda r: r.last_backup_date) if eligible_repos else None

        activity_end = RdiffTime()
        activity_start = RdiffTime() - timedelta(days=90)

        return {
            "userobj": userobj,
            "repo_objs": repo_objs,
            "total_repo": len(repo_objs),
            "total_ok": status_counts["ok"],
            "total_failed": status_counts["failed"],
            "total_overdue": status_counts["overdue"],
            "total_interrupted": status_counts["interrupted"],
            "total_in_progress": status_counts["in_progress"],
            # Errors
            "error_count": sum(r.session_statistics[-1].errors for r in repo_objs if r.last_backup_date),
            # last_backup
            "last_backup_date": last_backup.last_backup_date if last_backup else None,
            "last_backup_repo": last_backup.display_name if last_backup else None,
            # Storage
            "disk_usage": userobj.disk_usage,
            "disk_quota": userobj.disk_quota,
            "repos_usage": {
                repo.display_name: repo.session_statistics[-1].sourcefilesize if repo.session_statistics else 0
                for repo in repo_objs
            },
            # Heatmap
            "activity_start": activity_start,
            "activity_end": activity_end,
            "activity_dates": [d for repo in repo_objs for d in repo.session_statistics.keys()],
        }
