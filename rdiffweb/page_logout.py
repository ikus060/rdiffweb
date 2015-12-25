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
from __future__ import absolute_import

import cherrypy
import logging
from rdiffweb import page_main

# Define the logger
logger = logging.getLogger(__name__)


class LogoutPage(page_main.MainPage):

    @cherrypy.expose
    def index(self):

        # Empty the session info
        cherrypy.session['username'] = None  # @UndefinedVariable
        cherrypy.request.user = None

        # Redirect user to /login
        raise cherrypy.HTTPRedirect("/login/")
