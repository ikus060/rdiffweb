# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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
Default page handler

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""


import inspect

import cherrypy

import rdiffweb.tools.auth_form  # noqa
import rdiffweb.tools.auth_mfa  # noqa
import rdiffweb.tools.ratelimit  # noqa
from rdiffweb.core.rdw_helpers import unquote_url


def restapi():
    """
    A decorator for _cp_dispatch
    (cherrypy.dispatch.Dispatcher.dispatch_method_name).

    Will use the HTTP method to find the proper function to be called.

    e.g.:
    GET /api/users      -> list()
    GET /api/users/3    -> get(3)
    DELETE /api/users/3 -> delete(3)
    POST /api/users     -> post(data)
    POST /api/users/3   -> post(3, data)
    PUT /api/users      -> post(data)
    PUT /api/users/3    -> post(3, data)
    """

    @cherrypy.expose
    def decorated(cls_or_self=None, *args, **kwargs):
        if inspect.isclass(cls_or_self):
            # cherrypy.restapi is a class decorator
            cls = cls_or_self
            setattr(cls, 'default', decorated)
            return cls

        # We're in the actual function
        self = cls_or_self

        # Handle GET without object identifier
        method = cherrypy.request.method
        if method == 'GET' and not args:
            method = 'LIST'

        # Lookup class for a matching node.
        if getattr(self, method.lower(), False):
            # Verify if the node is an exposed function.
            node = getattr(self, method.lower(), False)
            if hasattr(node, '__call__') and getattr(node, 'exposed', False):
                return node(*args, **kwargs)

        # Raise 405 Method not allowed if a function matching the method is not found.
        raise cherrypy.HTTPError(405)

    return decorated


def convert_path():
    """
    A tool to conver vpath to path once the handler was found.

    Used to merge the segment of URI into a single parameter denoting the
    repository path.
    """
    handler = cherrypy.serving.request.handler
    if hasattr(handler, 'kwargs'):
        handler.kwargs = {'path': b"/".join([unquote_url(segment) for segment in handler.args])}
        handler.args = []


cherrypy.tools.poppath = cherrypy.Tool('on_start_resource', convert_path, priority=15)


def staticdir(path):
    """
    Create a page handler to serve static directory.
    """

    @cherrypy.expose
    @cherrypy.tools.auth_form(on=False)
    @cherrypy.tools.auth_mfa(on=False)
    @cherrypy.tools.ratelimit(on=False)
    @cherrypy.tools.sessions(on=False)
    @cherrypy.tools.secure_headers(on=False)
    @cherrypy.tools.staticdir(section="", dir=path)
    def handler(*args, **kwargs):
        raise cherrypy.HTTPError(400)

    return handler


def staticfile(path):
    """
    Create a page handler to serve static file.
    """

    @cherrypy.expose
    @cherrypy.tools.auth_form(on=False)
    @cherrypy.tools.auth_mfa(on=False)
    @cherrypy.tools.ratelimit(on=False)
    @cherrypy.tools.sessions(on=False)
    @cherrypy.tools.secure_headers(on=False)
    @cherrypy.tools.staticfile(filename=path)
    def handler(*args, **kwargs):
        raise cherrypy.HTTPError(400)

    return handler
