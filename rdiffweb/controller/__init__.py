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

from __future__ import unicode_literals

import cherrypy


def validate(value, message=None):
    """Raise HTTP error if value is not true."""
    if not value:
        raise cherrypy.HTTPError(400, message)

def validate_int(value, message=None):
    """Raise HTTP Error if the value is not an integer"""
    try:
        int(value)
    except:
        raise cherrypy.HTTPError(400, message)

def validate_isinstance(value, cls, message=None):
    """Raise HTTP error if value is not cls."""
    if not isinstance(value, cls):
        raise cherrypy.HTTPError(400, message)


class Controller(object):

    @property
    def app(self):
        return cherrypy.request.app
