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
"""
Created on Nov 16, 2017

@author: Patrik Dufresne
"""

from __future__ import unicode_literals

import logging
from rdiffweb.controller import Controller

import cherrypy

# Define the logger
logger = logging.getLogger(__name__)


class ApiCurrentuser(Controller):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def repos(self):
        """
        Return the list of repositories.
        """
        return self.app.currentuser.repos

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        u = self.app.currentuser
        return {
            "is_admin": u.is_admin,
            "email": u.email,
            "user_root": u.user_root,
            "repos": u.repos,
            "username": u.username,
        }


@cherrypy.config(**{'tools.authform.on': False, 'tools.i18n.on': False, 'tools.authbasic.on': True, 'tools.sessions.on': True, 'error_page.default': False})
class ApiPage(Controller):
    """
    This class provide a restful API to access some of the rdiffweb resources.
    """
    
    currentuser = ApiCurrentuser()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def index(self):
        return "ok"

