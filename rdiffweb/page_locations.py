#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

from __future__ import unicode_literals

import cherrypy
import logging

import librdiff
import page_main

from rdw_helpers import encode_s
from rdiffweb import rdw_plugin
from i18n import ugettext as _

# Define the logger
logger = logging.getLogger(__name__)


class LocationsPage(page_main.MainPage):
    """
    Shows the repository page. Will show all available destination
    backup directories. This is the root (/) page.
    """

    @cherrypy.expose
    def index(self):
        logger.debug("browsing locations")

        # Get page params
        params = {}
        try:
            params = self._get_parms_for_page()
        except:
            logger.exception("fail to get user's locations")
            params["error"] = _("fail to get user's locations")

        # Render the page.
        return self._compile_template("locations.html", **params)

    def _get_parms_for_page(self):
        """
        Build the params for the locations templates.
        """
        # Get user's locations.
        user_root = self.app.userdb.get_root_dir(self.get_username())
        user_root_b = encode_s(user_root)
        user_repos = self.app.userdb.get_repos(self.get_username())
        repos = []
        for user_repo in user_repos:
            try:
                # Get reference to a repo object
                repo_obj = librdiff.RdiffRepo(user_root_b, encode_s(user_repo))
                path = repo_obj.path
                name = repo_obj.display_name
                in_progress = repo_obj.in_progress
                last_backup_date = repo_obj.last_backup_date
                failed = False
            except librdiff.FileError:
                logging.exception("invalid user path %s" % user_repo)
                path = encode_s(user_repo)
                name = user_repo
                in_progress = False
                last_backup_date = 0
                failed = True
            # Create an entry to represent the repository
            repos.append({
                "path": path,
                "name": name,
                "last_backup_date": last_backup_date,
                'in_progress': in_progress,
                'failed': failed
                })
        params = {"repos": repos}

        # Add plugins params.
        # TODO transform this into lambda function.
        self.app.plugins.run(
            lambda x: x.locations_update_params(params),
            rdw_plugin.ILocationsPagePlugin.CATEGORY)

        # Return the complete list of params.
        return params
