#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffWeb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffWeb contributors
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

import cherrypy
import rdw_config


def handle_setup():
    if not rdw_config.getConfigFile():
        print
        raise cherrypy.HTTPRedirect("/setup/")

cherrypy.tools.setup = cherrypy.Tool('before_handler', handle_setup)
