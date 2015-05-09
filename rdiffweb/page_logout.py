#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 rdiffweb contributors
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
import page_main

# Define the logger
logger = logging.getLogger(__name__)


class rdiffLogoutPage(page_main.rdiffPage):

    @cherrypy.expose
    def index(self):

        # Empty the session info
        self.setUsername(None)
        cherrypy.request.user = None

        # Redirect user to /login
        raise cherrypy.HTTPRedirect("/login/")
