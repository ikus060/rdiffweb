#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

import codecs
import logging
import rdw_helpers

# Define the logger
logger = logging.getLogger(__name__)


class SettingsError:

    def __init__(self, error=None):
        if not error:
            raise ValueError
        assert isinstance(error, unicode)
        self.error = error

    def __unicode__(self):
        return self.error

    def __str__(self):
        return rdw_helpers.encode_s(unicode(self))


import os
import re


class Configuration(object):

    def __init__(self, filename="/etc/rdiffweb/rdw.conf"):
        # Declare the cache variable used to store the configuration in memory.
        self._cache = False
        # Declare default location
        self._filename = filename
        # Declare modification time
        self._lastmtime = False

    def get_config_file(self):
        """Return the configuration file location."""
        return self._filename

    def set_config_file(self, filename):
        """Set the configuration file to be read."""
        # Check filename access
        self._filename = filename
        if (not os.access(self._filename, os.F_OK)):
            raise SettingsError("Error reading %s, make sure it's readable."
                                % filename)

        # Force reading the configuration file.
        self._lastmtime = False

    def get_config(self, key, default=""):
        """Get the configuration value corresponding to key."""
        assert isinstance(key, unicode)
        # Raise error if key contains equals(=)
        if ('=' in key):
            raise ValueError

        # Read the configuration file if required.
        self._parse_if_needed()

        # Use the cached value
        cache = self._cache.get(key.lower())
        if cache:
            return cache
        else:
            return default

    def get_config_bool(self, key, default="False"):
        """
        A convenience method which coerces the key to a boolean.
        """
        value = self.get_config(key, default)
        return (value == "1" or value == "yes" or value == "true"
                or value == "on")

    def get_config_int(self, key, default=''):
        """
        A convenience method which coerces the key to an integer.
        """
        return int(self.get_config(key, default))

    def get_config_list(self, key, default='', sep=',', keep_empty=False):
        """A convenience method which coerces the key to a list of string.
    
        A different separator can be specified using the `sep` parameter. The
        `sep` parameter can specify multiple values using a list or a tuple.
        If the `keep_empty` parameter is set to `True`, empty elements are
        included in the list.
    
        Valid default input is a string or a list. Returns a string.
        """
        value = self.get_config(key, default)
        if not value:
            return []
        if isinstance(value, basestring):
            if isinstance(sep, (list, tuple)):
                splitted = re.split('|'.join(map(re.escape, sep)), value)
            else:
                splitted = value.split(sep)
            items = [item.strip() for item in splitted]
        else:
            items = list(value)
        if not keep_empty:
            items = [item for item in items if item not in (None, '')]
        return items

    def get_config_str(self, key, default=""):

        """A convenience method which coerces the key to an str."""

        try:
            return rdw_helpers.encode_s(self.get_config(key, default))
        except:
            return default

    def _parse_if_needed(self, force=False):
        """Read the configuration file and update the internal _cache. Return True
        if the configuration was read. False if the configuration wasn't read. Used
        may called this method with force=True to force the configuration to be
        read."""
        if not self._filename:
            raise SettingsError("Error reading configuration. Filename not define.")

        # Check if parsing the config file is required.
        modtime = os.path.getmtime(self._filename)
        if self._cache and not force and modtime == self._lastmtime:
            return False

        # Read configuration file.
        logger.debug("reading configuration file [%s]" % (self._filename))
        if not os.access(self._filename, os.F_OK):
            raise SettingsError("Error reading %s, make sure it's readable."
                                % (self._filename))

        new_cache = dict()

        # Open settings file as utf-8
        lines = codecs.open(self._filename, "r",
                            encoding='utf-8',
                            errors='replace').readlines()
        for line in lines:
            line = re.compile("(.*)#.*").sub(r'\1', line).strip()
            if not line:
                continue
            if '=' not in line:
                raise SettingsError(
                    "Error reading configuration line %s" % (line))
            split_line = line.partition('=')
            if not len(split_line) == 3:
                raise SettingsError(
                    "Error reading configuration line %s" % (line))
            new_cache[split_line[0].lower().strip()] = split_line[2].strip()

        # Return the configuration data.
        self._cache = new_cache
        self._lastmtime = modtime
        return True

# Unit Tests #

import unittest


class ConfigurationTest(unittest.TestCase):

    """Unit tests for the get_config() function"""
    goodConfigText = """ #This=is a comment
    SpacesValue=is a setting with spaces
    spaces setting=withspaces
    CommentInValue=Value#this is a comment
    NoValue=#This is a setting with no value
    """
    badConfigTexts = [
        'This#doesnt have an equals', 'This=more=than one equals']
    configFilePath = "/tmp/rdw_config.conf"

    def writeGoodFile(self):
        file = open(self.configFilePath, "w")
        file.write(self.goodConfigText)
        file.close()
        self.config = Configuration(self.configFilePath)

    def writeBadFile(self, badSettingNum):
        self.writeGoodFile()
        file = open(self.configFilePath, "w")
        file.write(self.badConfigTexts[badSettingNum])
        file.close()
        self.config = Configuration(self.configFilePath)

    def tearDown(self):
        if (os.access(self.configFilePath, os.F_OK)):
            os.remove(self.configFilePath)

    def testBadParms(self):
        self.writeGoodFile()
        try:
            self.config.get_config("setting=")
        except ValueError:
            pass
        else:
            assert(False)

    def testSpacesInValue(self):
        self.writeGoodFile()
        assert(self.config.get_config("SpacesValue")
               == "is a setting with spaces")

    def testSpacesInSetting(self):
        self.writeGoodFile()
        assert(
            self.config.get_config("spaces setting") == "withspaces")

    def testCommentInValue(self):
        self.writeGoodFile()
        assert(
            self.config.get_config("CommentInValue") == "Value")

    def testEmptyValue(self):
        self.writeGoodFile()
        assert(self.config.get_config("NoValue") == "")

    def testCaseInsensitivity(self):
        self.writeGoodFile()
        assert(
            self.config.get_config("commentinvalue") == "Value")

    def testMissingSetting(self):
        self.writeGoodFile()
        assert(
            self.config.get_config("SettingThatDoesntExist") == "")

    def testBadFile(self):
        self.writeBadFile(0)
        try:
            self.config.get_config("SpacesValue")
        except SettingsError:
            pass
        else:
            assert(False)

        self.writeBadFile(1)
        value = self.config.get_config("This")
        assert(value == "more=than one equals")
