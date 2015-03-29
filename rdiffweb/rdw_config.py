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


# Declare the cache variable used to store the configuration in memory.
_cache = False
# Declare default location
_filename = "/etc/rdiffweb/rdw.conf"
# Declare modification time
_lastmtime = False


def set_config_file(filename):
    """Set the configuration file to be read."""
    # Check filename access
    global _filename
    _filename = filename
    if (not os.access(_filename, os.F_OK)):
        raise SettingsError("Error reading %s, make sure it's readable."
                            % filename)

    # Force reading the configuration file.
    global _lastmtime
    _lastmtime = False


def get_config(key, default=""):
    """Get the configuration value corresponding to key."""
    assert isinstance(key, unicode)
    # Raise error if key contains equals(=)
    if ('=' in key):
        raise ValueError

    # Read the configuration file if required.
    _parse_if_needed()

    # Use the cached value
    cache = _cache.get(key.lower())
    if cache:
        return cache
    else:
        return default


def get_config_boolean(key, default=False):

    """A convenience method which coerces the settingName to a boolean."""

    try:
        value = get_config(key)
        return (value == "1" or value == "yes" or value == "true"
                or value == "on")
    except:
        return default


def get_config_int(key, default=0):

    """A convenience method which coerces the settingName to an integer."""

    try:
        return int(get_config(key))
    except:
        return default


def get_config_str(key, default=""):

    """A convenience method which coerces the settingName to an str."""

    try:
        return rdw_helpers.encode_s(get_config(key, default))
    except:
        return default

def _parse_if_needed(force=False):
    """Read the configuration file and update the internal _cache. Return True
    if the configuration was read. False if the configuration wasn't read. Used
    may called this method with force=True to force the configuration to be
    read."""
    global _filename
    if not _filename:
        raise SettingsError("Error reading configuration. Filename not define.")

    # Check if parsing the config file is required.
    global _cache
    global _lastmtime
    modtime = os.path.getmtime(_filename)
    if _cache and not force and modtime == _lastmtime:
        return False

    # Read configuration file.
    logger.debug("reading configuration file [%s]" % (_filename))
    if not os.access(_filename, os.F_OK):
        raise SettingsError("Error reading %s, make sure it's readable."
                            % (_filename))

    new_cache = dict()

    # Open settings file as utf-8
    lines = codecs.open(_filename, "r",
                        encoding='utf-8',
                        errors='replace').readlines()
    for line in lines:
        line = re.compile("(.*)#.*").sub(r'\1', line)
        line = line.rstrip()
        line = line.lstrip()
        if not line:
            continue
        if '=' not in line:
            raise SettingsError("Error reading configuration line %s" % (line))

        split_line = line.partition('=')
        if not len(split_line) == 3:
            raise SettingsError("Error reading configuration line %s" % (line))

        new_cache[split_line[0].lower()] = split_line[2]

    # Return the configuration data.
    _cache = new_cache
    _lastmtime = modtime
    return True

# Unit Tests #

import unittest


class configFileTest(unittest.TestCase):

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
        set_config_file(self.configFilePath)

    def writeBadFile(self, badSettingNum):
        self.writeGoodFile()
        file = open(self.configFilePath, "w")
        file.write(self.badConfigTexts[badSettingNum])
        file.close()
        set_config_file(self.configFilePath)

    def tearDown(self):
        if (os.access(self.configFilePath, os.F_OK)):
            os.remove(self.configFilePath)

    def testBadParms(self):
        self.writeGoodFile()
        try:
            get_config("setting=")
        except ValueError:
            pass
        else:
            assert(False)

    def testSpacesInValue(self):
        self.writeGoodFile()
        assert(get_config("SpacesValue")
               == "is a setting with spaces")

    def testSpacesInSetting(self):
        self.writeGoodFile()
        assert(
            get_config("spaces setting") == "withspaces")

    def testCommentInValue(self):
        self.writeGoodFile()
        assert(
            get_config("CommentInValue") == "Value")

    def testEmptyValue(self):
        self.writeGoodFile()
        assert(get_config("NoValue") == "")

    def testCaseInsensitivity(self):
        self.writeGoodFile()
        assert(
            get_config("commentinvalue") == "Value")

    def testMissingSetting(self):
        self.writeGoodFile()
        assert(
            get_config("SettingThatDoesntExist") == "")

    def testBadFile(self):
        self.writeBadFile(0)
        try:
            get_config("SpacesValue")
        except SettingsError:
            pass
        else:
            assert(False)

        self.writeBadFile(1)
        value = get_config("This")
        assert(value == "more=than one equals")
