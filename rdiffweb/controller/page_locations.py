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

import cherrypy

from rdiffweb.controller import Controller

# Define the logger
logger = logging.getLogger(__name__)


class LocationsPage(Controller):
    @cherrypy.expose
    def index(self):
        """
        Shows repositories of current user
        """
        # Get page params
        if self.app.currentuser.refresh_repos():
            self.app.currentuser.commit()
        params = {
            "repos": self.app.currentuser.repo_objs,
            "disk_usage": self.app.currentuser.disk_usage,
            "disk_quota": self.app.currentuser.disk_quota,
        }
        # Render the page.
        return self._compile_template("locations.html", **params)
