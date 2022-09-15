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

import cherrypy


def real_ip(remote='X-Real-IP'):
    """
    Update the `remote.ip` from the `X-Real-IP` field.
    """

    request = cherrypy.serving.request

    value = request.headers.get(remote)
    if value:
        request.remote.ip = value


cherrypy.tools.real_ip = cherrypy.Tool('before_request_body', real_ip, priority=31)
