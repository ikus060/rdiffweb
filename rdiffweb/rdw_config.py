#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffweb contributors
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


class SettingsError:

    def __str__(self):
        return "Invalid configuration file syntax"


class ParameterError:

    def __str__(self):
        return "Invalid parameters"


def getConfigFile():
    settingsFiles = ["rdw.conf", "/etc/rdiffweb/rdw.conf"]
    # TODO: there *has* to be a better way to get the /etc config file
    # path...
    for settingsFile in settingsFiles:
        if os.access(settingsFile, os.F_OK):
            return settingsFile
    # Return default
    return "/etc/rdiffweb/rdw.conf"

import os
import re


def getConfigSetting(settingName, settingsFile=None, default=""):
    if ('=' in settingName):
        raise ParameterError
    if settingsFile is None:
        settingsFile = getConfigFile()
    if (not os.access(settingsFile, os.F_OK)):
        return default
    settingsStrings = open(settingsFile, "r").readlines()
    for setting in settingsStrings:
        setting = re.compile("(.*)#.*").sub(r'\1', setting)
        setting = setting.rstrip()
        setting = setting.lstrip()
        if not setting:
            continue
        if '=' not in setting:
            raise SettingsError

        splitSetting = setting.partition('=')
        if not len(splitSetting) == 3:
            raise SettingsError

        # Lower-case both vars for case-insensitive compare
        if splitSetting[0].lower() == settingName.lower():
            return splitSetting[2]

    return default

# Unit Tests #

import unittest


class configFileTest(unittest.TestCase):

    """Unit tests for the getConfigSetting() function"""
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

    def writeBadFile(self, badSettingNum):
        self.writeGoodFile()
        file = open(self.configFilePath, "w")
        file.write(self.badConfigTexts[badSettingNum])
        file.close()

    def tearDown(self):
        if (os.access(self.configFilePath, os.F_OK)):
            os.remove(self.configFilePath)

    def testBadParms(self):
        value = getConfigSetting("setting", "/tmp/rdw_bogus.conf")
        assert(value == "")
        self.writeGoodFile()
        try:
            getConfigSetting("setting=", "/tmp/rdw_config.conf")
        except ParameterError:
            pass
        else:
            assert(False)

    def testSpacesInValue(self):
        self.writeGoodFile()
        assert(getConfigSetting("SpacesValue", "/tmp/rdw_config.conf")
               == "is a setting with spaces")

    def testSpacesInSetting(self):
        self.writeGoodFile()
        assert(
            getConfigSetting("spaces setting", "/tmp/rdw_config.conf") == "withspaces")

    def testCommentInValue(self):
        self.writeGoodFile()
        assert(
            getConfigSetting("CommentInValue", "/tmp/rdw_config.conf") == "Value")

    def testEmptyValue(self):
        self.writeGoodFile()
        assert(getConfigSetting("NoValue", "/tmp/rdw_config.conf") == "")

    def testCaseInsensitivity(self):
        self.writeGoodFile()
        assert(
            getConfigSetting("commentinvalue", "/tmp/rdw_config.conf") == "Value")

    def testMissingSetting(self):
        self.writeGoodFile()
        assert(
            getConfigSetting("SettingThatDoesntExist", "/tmp/rdw_config.conf") == "")

    def testBadFile(self):
        self.writeBadFile(0)
        try:
            getConfigSetting("SpacesValue", "/tmp/rdw_config.conf")
        except SettingsError:
            pass
        else:
            assert(False)

        self.writeBadFile(1)
        try:
            getConfigSetting("SpacesValue", "/tmp/rdw_config.conf")
        except SettingsError:
            pass
        else:
            assert(False)
