#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffweb contributors
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
import os
import librdiff
import page_main
import rdw_helpers
from rdw_helpers import encode_s, decode_s

class rdiffLocationsPage(page_main.rdiffPage):

    ''' Shows the locations page. Will show all available destination
    backup directories. This is the root (/) page '''
    @cherrypy.expose
    def index(self):
        return self._writePage("locations.html", **self.get_parms_for_page())

    def get_parms_for_page(self):
        user_root_b = encode_s(self.getUserDB().getUserRoot(self.getUsername()))
        user_repos = self.getUserDB().getUserRepoPaths(self.getUsername())
        repoList = []
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
                logging.exception(
                    "Can't get reference on the last backup history for %s" % name)
                path = encode_s(user_repo)
                name = user_repo
                in_progress = False
                last_backup_date = 0
                failed = True
            repoList.append({"path": path,
                             "name": name,
                             "last_backup_date": last_backup_date,
                             'in_progress': in_progress,
                             'failed': failed})

        return {"title": "Locations", "repos": repoList}
