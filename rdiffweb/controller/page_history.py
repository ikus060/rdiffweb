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

from rdiffweb.controller import Controller, validate_isinstance, validate_int
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.i18n import ugettext as _


# Define the logger
logger = logging.getLogger(__name__)


@poppath()
class HistoryPage(Controller):

    @cherrypy.expose
    def index(self, path=b"", limit='10', **kwargs):
        validate_isinstance(path, bytes)
        limit = validate_int(limit)

        repo_obj = self.app.currentuser.get_repo(path)

        # Set up warning about in-progress backups, if necessary
        warning = False
        status = repo_obj.status
        if status[0] != 'ok':
            warning = status[1] + ' ' + _("The displayed data may be inconsistent.")

        parms = {
            "limit": limit,
            "repo_name": repo_obj.display_name,
            "repo_path": repo_obj.path,
            "history_entries": repo_obj.get_history_entries(numLatestEntries=limit, reverse=True),
            "warning": warning,
        }

        return self._compile_template("history.html", **parms)
