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

import rdw_config
import db


class fileUserDB(db.userDB):

    def __init__(self, configFilePath=None):
        self.configFilePath = configFilePath

    def userExists(self, username):
        valid_username = rdw_config.get_config(
            "username", self.configFilePath)
        return valid_username == username

    def areUserCredentialsValid(self, username, password):
        """The valid users string in the config file is in the form:
            username=bill
            password=frank """
        valid_username = rdw_config.get_config(
            "username", self.configFilePath)
        valid_password = rdw_config.get_config(
            "password", self.configFilePath)
        return valid_username == username and valid_password == password

    def getUserRoot(self, username):
        if not self.userExists(username):
            return None
        return rdw_config.get_config("UserRoot", self.configFilePath)

    def getUserRepoPaths(self, username):
        """The user home dirs string in the config file is in the form of username:/data/dir|/data/dir2..."""
        if not self.userExists(username):
            return None
        return rdw_config.get_config("UserRepoPaths", self.configFilePath).split("|")

    def userIsAdmin(self, username):
        return False


# Unit Tests

import unittest
import os


class fileUserDataTest(unittest.TestCase):

    """Unit tests for the fileUserData class"""
    validUsersString = """username=test
                                 password=user
                                 UserRoot=/data
                                 UserRepoPaths=/data/bill|/data/frank"""
    configFilePath = "/tmp/rdw_config.conf"

    def setUp(self):
        file = open(self.configFilePath, "w")
        file.write(self.validUsersString)
        file.close()

    def tearDown(self):
        if (os.access(self.configFilePath, os.F_OK)):
            os.remove(self.configFilePath)

    def testValidUser(self):
        authModule = fileUserDB(self.configFilePath)
        assert(authModule.userExists("test"))
        assert(authModule.areUserCredentialsValid("test", "user"))

    def testBadPassword(self):
        authModule = fileUserDB(self.configFilePath)
        # Basic test
        assert(not authModule.areUserCredentialsValid("test", "user2"))
        # password is case sensitive
        assert(not authModule.areUserCredentialsValid("test", "User"))
        # Match entire password
        assert(not authModule.areUserCredentialsValid("test", "use"))
        # Make sure pipe at end doesn't allow blank username/password
        assert(not authModule.areUserCredentialsValid("test", ""))

    def testBadUser(self):
        authModule = fileUserDB(self.configFilePath)
        # username is case sensitive
        assert(not authModule.userExists("Test"))
        # Match entire username
        assert(not authModule.userExists("tes"))
        # Make sure blank username is disallowed
        assert(not authModule.userExists(""))

    def testGoodUserDir(self):
        userDataModule = fileUserDB(self.configFilePath)
        assert(userDataModule.getUserRepoPaths("test")
               == ["/data/bill", "/data/frank"])
        assert(userDataModule.getUserRoot("test") == "/data")

    def testBadUser(self):
        userDataModule = fileUserDB(self.configFilePath)
        # should return None if user doesn't exist
        assert(not userDataModule.getUserRepoPaths("test2"))
        # should return None if user doesn't exist
        assert(not userDataModule.getUserRoot(""))

if __name__ == "__main__":
    print "Called as standalone program; running unit tests..."
    fileUserDataTest = unittest.makeSuite(fileUserDataTest, 'test')
    testRunner = unittest.TextTestRunner()
    testRunner.run(fileUserDataTest)
