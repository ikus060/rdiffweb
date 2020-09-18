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
'''
Created on Mar. 3, 2019

@author: Patrik Dufresne <patrik@ikus-soft.com>
'''

from rdiffweb.core.config import read_config
from rdiffweb.rdw_app import RdiffwebApp

import cherrypy
import os

if __name__.startswith("uwsgi"):
    # Read config file
    configfile = os.environ.get('RDIFFWEB_CONFIG', '/etc/rdiffweb/rdw.conf')
    cfg = read_config(configfile)

    # Create application
    cherrypy.config.update({'engine.autoreload.on': False})
    cherrypy.server.unsubscribe()
    cherrypy.engine.start()

    wsgiapp = cherrypy.tree.mount(RdiffwebApp(cfg))
