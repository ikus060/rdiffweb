#!/usr/bin/python
# rdiffWeb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffWeb contributors
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

        userData.addUser("test")
        userData.setUserInfo("test", "/data", False)
        userData.setUserPassword("test", "user")
        userData.setUserRepos("test", ["/data/bill", "/data/frank"])
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
        assert(authModule.userExists("test"))
        assert(authModule.areUserCredentialsValid("test", "user"))

    def testUserTruncation(self):
        raise NotImplementedError

    def testUserList(self):
        authModule = self._getUserDB()
        assert(authModule.getUserList() == ["test"])

    def testDeleteUser(self):
        authModule = self._getUserDB()
        assert(authModule.getUserList() == ["test"])
        authModule.deleteUser("test")
        assert(authModule.getUserList() == [])

    def testUserInfo(self):
        authModule = self._getUserDB()
        assert(authModule.getUserRoot("test") == "/data")
        assert(not authModule.userIsAdmin("test"))

    def testBadPassword(self):
        authModule = self._getUserDB()
        # Basic test
        assert(not authModule.areUserCredentialsValid("test", "user2"))
        # password is case sensitive
        assert(not authModule.areUserCredentialsValid("test", "User"))
        # Match entire password
        assert(not authModule.areUserCredentialsValid("test", "use"))
        # Match entire password
        assert(not authModule.areUserCredentialsValid("test", ""))

    def testBadUser(self):
        authModule = self._getUserDB()
        assert(not authModule.userExists("Test"))  # username is case sensitive
        assert(not authModule.userExists("tes"))  # Match entire username

    def testGoodUserDir(self):
        userDataModule = self._getUserDB()
        assert(userDataModule.getUserRepoPaths("test")
               == ["/data/bill", "/data/frank"])
        assert(userDataModule.getUserRoot("test") == "/data")

    def testBadUserReturn(self):
        userDataModule = self._getUserDB()
        # should return None if user doesn't exist
        assert(not userDataModule.getUserRepoPaths("test2"))
        # should return None if user doesn't exist
        assert(not userDataModule.getUserRoot(""))

    def testUserRepos(self):
        userDataModule = self._getUserDB()
        userDataModule.setUserRepos("test", [])
        userDataModule.setUserRepos("test", ["a", "b", "c"])
        self.assertEquals(
            userDataModule.getUserRepoPaths("test"), ["a", "b", "c"])
        # Make sure that repo max ages are initialized to 0
        maxAges = [userDataModule.getRepoMaxAge("test", x)
                   for x in userDataModule.getUserRepoPaths("test")]
        self.assertEquals(maxAges, [0, 0, 0])
        userDataModule.setRepoMaxAge("test", "b", 1)
        self.assertEquals(userDataModule.getRepoMaxAge("test", "b"), 1)
        userDataModule.setUserRepos("test", ["b", "c", "d"])
        self.assertEquals(userDataModule.getRepoMaxAge("test", "b"), 1)
        self.assertEquals(
            userDataModule.getUserRepoPaths("test"), ["b", "c", "d"])

    def testRestoreFormat(self):
        userDataModule = self._getUserDB()
        # Should default to using zip format
        assert(userDataModule.useZipFormat('test'))
        userDataModule.setUseZipFormat('test', False)
        assert(not userDataModule.useZipFormat('test'))
