# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
Default page handler

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import cherrypy

import rdiffweb.tools.auth  # noqa
import rdiffweb.tools.auth_mfa  # noqa
import rdiffweb.tools.ratelimit  # noqa


def staticdir(path, doc=''):
    """
    Create a page handler to serve static directory.
    """

    @cherrypy.expose
    @cherrypy.tools.auth(on=False)
    @cherrypy.tools.auth_mfa(on=False)
    @cherrypy.tools.ratelimit(on=False)
    @cherrypy.tools.sessions(on=False)
    @cherrypy.tools.secure_headers(on=False)
    @cherrypy.tools.staticdir(section="", dir=str(path))
    def handler(*args, **kwargs):
        raise cherrypy.HTTPError(400)

    if doc:
        handler.__doc__ = doc
    return handler


def staticfile(path, doc=''):
    """
    Create a page handler to serve static file.
    """

    @cherrypy.expose
    @cherrypy.tools.auth(on=False)
    @cherrypy.tools.auth_mfa(on=False)
    @cherrypy.tools.ratelimit(on=False)
    @cherrypy.tools.sessions(on=False)
    @cherrypy.tools.secure_headers(on=False)
    @cherrypy.tools.staticfile(filename=str(path))
    def handler(*args, **kwargs):
        raise cherrypy.HTTPError(400)

    if doc:
        handler.__doc__ = doc
    return handler
