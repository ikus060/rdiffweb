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

# Unit Tests #

import unittest


class sqlUserDBTest(unittest.TestCase):

    """Generic unit tests for sql backends"""

    def _getUserDB(self):
        userData = self._getUserDBObject()
        if not userData._getTables():
            for statement in userData._getCreateStatements():
                userData._executeQuery(statement)

        userData.add_user("test")
        userData.set_info("test", "/data", False)
        userData.set_password("test", None, "user")
        userData.set_repos("test", ["/data/bill", "/data/frank"])
        return userData

    def tearDown(self):
        userData = self._getUserDB()
        tableNames = userData._getTables()
        print tableNames
        if 'users' in tableNames:
            userData._executeQuery("DROP TABLE users")
        if 'repos' in tableNames:
            userData._executeQuery("DROP TABLE repos")

    def testValidUser(self):
        authModule = self._getUserDB()
        assert(authModule.exists("test"))
        assert(authModule.are_valid_credentials("test", "user"))

    def testUserTruncation(self):
        raise NotImplementedError

    def testUserList(self):
        authModule = self._getUserDB()
        assert(authModule.list() == ["test"])

    def testdelete_user(self):
        authModule = self._getUserDB()
        assert(authModule.list() == ["test"])
        authModule.delete_user("test")
        assert(authModule.list() == [])

    def testUserInfo(self):
        authModule = self._getUserDB()
        assert(authModule.get_root_dir("test") == "/data")
        assert(not authModule.is_admin("test"))

    def testBadPassword(self):
        authModule = self._getUserDB()
        # Basic test
        assert(not authModule.are_valid_credentials("test", "user2"))
        # password is case sensitive
        assert(not authModule.are_valid_credentials("test", "User"))
        # Match entire password
        assert(not authModule.are_valid_credentials("test", "use"))
        # Match entire password
        assert(not authModule.are_valid_credentials("test", ""))

    def testBadUser(self):
        authModule = self._getUserDB()
        assert(not authModule.exists("Test"))  # username is case sensitive
        assert(not authModule.exists("tes"))  # Match entire username

    def testGoodUserDir(self):
        userDataModule = self._getUserDB()
        assert(userDataModule.get_repos("test")
               == ["/data/bill", "/data/frank"])
        assert(userDataModule.get_root_dir("test") == "/data")

    def testBadUserReturn(self):
        userDataModule = self._getUserDB()
        # should return None if user doesn't exist
        assert(not userDataModule.get_repos("test2"))
        # should return None if user doesn't exist
        assert(not userDataModule.get_root_dir(""))

    def testUserRepos(self):
        userDataModule = self._getUserDB()
        userDataModule.set_repos("test", [])
        userDataModule.set_repos("test", ["a", "b", "c"])
        self.assertEquals(
            userDataModule.get_repos("test"), ["a", "b", "c"])
        # Make sure that repo max ages are initialized to 0
        maxAges = [userDataModule.get_repo_maxage("test", x)
                   for x in userDataModule.get_repos("test")]
        self.assertEquals(maxAges, [0, 0, 0])
        userDataModule.set_repo_maxage("test", "b", 1)
        self.assertEquals(userDataModule.get_repo_maxage("test", "b"), 1)
        userDataModule.set_repos("test", ["b", "c", "d"])
        self.assertEquals(userDataModule.get_repo_maxage("test", "b"), 1)
        self.assertEquals(
            userDataModule.get_repos("test"), ["b", "c", "d"])
