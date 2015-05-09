#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 rdiffweb contributors
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

    def exists(self, username):
        valid_username = rdw_config.get_config(
            "username", self.configFilePath)
        return valid_username == username

    def are_valid_credentials(self, username, password):
        """The valid users string in the config file is in the form:
            username=bill
            password=frank """
        valid_username = rdw_config.get_config(
            "username", self.configFilePath)
        valid_password = rdw_config.get_config(
            "password", self.configFilePath)
        return valid_username == username and valid_password == password

    def get_root_dir(self, username):
        if not self.exists(username):
            return None
        return rdw_config.get_config("UserRoot", self.configFilePath)

    def get_repos(self, username):
        """The user home dirs string in the config file is in the form of username:/data/dir|/data/dir2..."""
        if not self.exists(username):
            return None
        return rdw_config.get_config("UserRepoPaths", self.configFilePath).split("|")

    def is_admin(self, username):
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
        assert(authModule.exists("test"))
        assert(authModule.are_valid_credentials("test", "user"))

    def testBadPassword(self):
        authModule = fileUserDB(self.configFilePath)
        # Basic test
        assert(not authModule.are_valid_credentials("test", "user2"))
        # password is case sensitive
        assert(not authModule.are_valid_credentials("test", "User"))
        # Match entire password
        assert(not authModule.are_valid_credentials("test", "use"))
        # Make sure pipe at end doesn't allow blank username/password
        assert(not authModule.are_valid_credentials("test", ""))

    def testBadUser(self):
        authModule = fileUserDB(self.configFilePath)
        # username is case sensitive
        assert(not authModule.exists("Test"))
        # Match entire username
        assert(not authModule.exists("tes"))
        # Make sure blank username is disallowed
        assert(not authModule.exists(""))

    def testGoodUserDir(self):
        userDataModule = fileUserDB(self.configFilePath)
        assert(userDataModule.get_repos("test")
               == ["/data/bill", "/data/frank"])
        assert(userDataModule.get_root_dir("test") == "/data")

if __name__ == "__main__":
    print "Called as standalone program; running unit tests..."
    fileUserDataTest = unittest.makeSuite(fileUserDataTest, 'test')
    testRunner = unittest.TextTestRunner()
    testRunner.run(fileUserDataTest)
