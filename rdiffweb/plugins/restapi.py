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

import cherrypy


class Dispatcher(cherrypy.dispatch.Dispatcher):
    """
    Dispatcher using HTTP method to find the proper function to be called.

    e.g.:
    GET /api/users            -> list()
    GET /api/users/3          -> get(3)
    GET /api/users/my/path    -> get('my/path')
    DELETE /api/users/3       -> delete(3)
    DELETE /api/users/my/path -> delete('my/path')

    POST /api/users     -> post(data)
    POST /api/users/3   -> post(3, data)
    PUT /api/users      -> post(data)
    PUT /api/users/3    -> post(3, data)

    """

    supported_method = ['get', 'delete', 'post', 'put']

    def __call__(self, path):
        request = cherrypy.serving.request
        # To simplify implementation reuse default dispatcher function.
        # But strip the last segment
        resource, vpath = self.find_handler(path)

        if not resource:
            request.handler = cherrypy.NotFound()
            return

        # Two scenario possible. Either we have found our GET handler.
        # Or we need to look into the resource for it.
        meth = request.method.lower()
        if meth not in self.supported_method:
            request.handler = cherrypy.HTTPError(405)
        if meth == 'get' and not hasattr(resource, 'list') and not hasattr(resource, 'get'):
            request.handler = cherrypy.dispatch.LateParamPageHandler(resource, *vpath)
            return

        # Call "list()" instead of "get()" when path doesn't have an id or name.
        if meth == 'get' and not vpath and hasattr(resource, 'list'):
            meth = 'list'
        # Find the subhandler
        func = getattr(resource, meth, None)
        if func:
            # Grab any _cp_config on the subhandler.
            if hasattr(func, '_cp_config'):
                request.config.update(func._cp_config)

            # Decode any leftover %2F in the virtual_path atoms.
            if vpath:
                vpath = ['/'.join([x.replace('%2F', '/') for x in vpath])]
            request.handler = cherrypy.dispatch.LateParamPageHandler(func, *vpath)
        else:
            request.handler = cherrypy.HTTPError(405)
