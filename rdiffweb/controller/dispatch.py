# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 Patrik Dufresne Service Logiciel
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


import cherrypy
from cherrypy.lib.static import serve_file, mimetypes
import os

from rdiffweb.core.rdw_helpers import unquote_url


def empty():

    @cherrypy.expose
    def handler():
        return None

    return handler


def poppath(*args, **kwargs):
    """
    A decorator for _cp_dispatch
    (cherrypy.dispatch.Dispatcher.dispatch_method_name).

    Used to merge the segment of URI into a single parameter denoting the
    repository path.
    """

    # Since keyword arg comes after *args, we have to process it ourselves
    # for lower versions of python.

    handler = None
    handler_call = False
    for k, v in kwargs.items():
        if k == 'handler':
            handler = v
        else:
            raise TypeError(
                "cherrypy.popargs() got an unexpected keyword argument '{0}'"
                .format(k)
            )

    import inspect

    if handler is not None \
            and (hasattr(handler, '__call__') or inspect.isclass(handler)):
        handler_call = True

    def decorated(cls_or_self=None, vpath=None):
        if inspect.isclass(cls_or_self):
            # cherrypy.poppath is a class decorator
            cls = cls_or_self
            setattr(cls, cherrypy.dispatch.Dispatcher.dispatch_method_name, decorated)
            return cls

        # We're in the actual function
        self = cls_or_self
        parms = {}
        for arg in args:
            if not vpath:
                break
            parms[arg] = unquote_url(vpath.pop(0))

        # Build repo path.
        path = []
        while len(vpath) > 0:
            path.append(unquote_url(vpath.pop(0)))
        parms['path'] = b"/".join(path)

        if handler is not None:
            if handler_call:
                return handler(**parms)
            else:
                cherrypy.request.params.update(parms)  # @UndefinedVariable
                return handler

        cherrypy.request.params.update(parms)  # @UndefinedVariable

        # If we are the ultimate handler, then to prevent our _cp_dispatch
        # from being called again, we will resolve remaining elements through
        # getattr() directly.
        if vpath:
            return getattr(self, vpath.pop(0), None)
        else:
            return self

    return decorated


def static(path):
    """
    Create a page handler to serve static files. Disable authentication.
    """
    assert isinstance(path, str)
    assert os.path.exists(path), "%r doesn't exists" % path
    content_type = None
    if os.path.isfile(path):
        # Set content-type based on filename extension
        ext = ""
        i = path.rfind('.')
        if i != -1:
            ext = path[i:].lower()
        content_type = mimetypes.types_map.get(ext, None)  # @UndefinedVariable

    @cherrypy.expose
    @cherrypy.config(**{'tools.authform.on': False})
    def handler(*args, **kwargs):
        if cherrypy.request.method not in ('GET', 'HEAD'):
            return None
        filename = os.path.join(path, *args)
        assert filename.startswith(path)
        if not os.path.isfile(filename):
            return None
        return serve_file(filename, content_type)

    return handler
