# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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
import datetime

import cherrypy


def enrich_session():
    """
    Store ephemeral information into user's session. e.g.: last IP address, user-agent
    """
    # When session is not enable, simply validate credentials
    sessions_on = cherrypy.request.config.get('tools.sessions.on', False)
    if not sessions_on:
        return
    # Get information related to the current request
    request = cherrypy.serving.request
    ip_address = request.remote.ip
    cherrypy.session['ip_address'] = ip_address
    cherrypy.session['user_agent'] = request.headers.get('User-Agent', None)
    cherrypy.session['access_time'] = datetime.datetime.now()


cherrypy.tools.enrich_session = cherrypy.Tool('before_handler', enrich_session, priority=60)
