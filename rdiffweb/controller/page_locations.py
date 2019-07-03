#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

from __future__ import absolute_import
from __future__ import unicode_literals

import logging

import cherrypy
from rdiffweb.controller import Controller

# Define the logger
logger = logging.getLogger(__name__)


class LocationsPage(Controller):
    """
    Shows the repository page. Will show all available destination
    backup directories. This is the root (/) page.
    """

    @cherrypy.expose
    def index(self):
        # Get page params
        params = {
            "repos": [{
                "path": repo_obj.path,
                "name_split": repo_obj.display_name.strip('/').split('/'),
                "last_backup_date": repo_obj.last_backup_date,
                'status': repo_obj.status,
            } for repo_obj in self.app.currentuser.repo_objs],
            "disk_usage": self.app.currentuser.disk_usage,
        }
        # Render the page.
        return self._compile_template("locations.html", **params)

