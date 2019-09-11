#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 rdiffweb contributors
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

from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from io import open
import logging
import re

from builtins import object
from cherrypy import Application
import cherrypy

# Define the logger
logger = logging.getLogger(__name__)


def read_config(filename):
    """
    Used to read the rdiffweb config file as dict.
    
    Read the configuration file and update the internal _cache. Return True
    if the configuration was read. False if the configuration wasn't read. Used
    may called this method with force=True to force the configuration to be
    read.
    """
    
    if not filename:
        return {}

    # Read configuration file.
    logger.debug("reading configuration file [%s]", filename)

    new_cache = dict()

    # Open settings file as utf-8
    with open(filename, encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        line = re.compile("(.*)#.*").sub(r'\1', line).strip()
        if not line:
            continue
        if '=' not in line:
            raise Exception(
                "error reading configuration line %s" % (line))
        split_line = line.partition('=')
        if not len(split_line) == 3:
            raise Exception(
                "error reading configuration line %s" % (line))
        new_cache[split_line[0].lower().strip()] = split_line[2].strip()

    # This dictionary is read by cherrypy. So create appropriate structure.
    return new_cache


def write_config(config, filename):
    # Start writing the file.
    with open(filename, "w", encoding='utf-8') as f:
        for key, value in list(config.items()):
            f.write('%s=%s' % (key, value))
            f.write('\n')


class Option(object):

    def __init__(self, key, default="", doc=None, _get_func=None, _set_func=None):
        self.key = key.lower()
        self.default = default
        self.doc = doc
        self._get_func = _get_func or (lambda x: x)
        self._set_func = _set_func or (lambda x: x)

    def __get__(self, instance, owner):
        """
        Return a property to wrap the given option.
        """
        return self.get(instance)
    
    def __set__(self, instance, value):
        """
        Update the config with the new value.
        """
        self.set(value, instance)
    
    def get(self, instance=None):
        """
        Return the value of this options.
        """
        if isinstance(instance, Application):
            app = instance
        else:
            app = cherrypy.request.app or getattr(instance, 'app', None)
        assert app, "Option() can't find reference to app"
        config = app.cfg
        value = config.get(self.key)  # @UndefinedVariable
        if value is None:
            return self.default
        return self._get_func(value)
    
    def set(self, value, instance=None):
        """
        Update the config with the new value.
        """
        if isinstance(instance, Application):
            app = instance
        else:
            app = cherrypy.request.app or getattr(instance, 'app', None)
        assert app, "Option() can't find reference to app"
        config = app.cfg
        if value is None:
            config.set(self.key, None)
        else:
            config[self.key] = self._set_func(value)


class IntOption(Option):

    def __init__(self, key, default="", doc=None):
        Option.__init__(self, key, default, doc, _get_func=int, _set_func=str)


class BoolOption(Option):

    def __init__(self, key, default="", doc=None):
        Option.__init__(self, key, default, doc,
            _get_func=lambda x: x.lower() in ("1", "yes", "true", "on"),
            _set_func=str)
