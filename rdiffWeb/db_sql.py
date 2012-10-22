#!/usr/bin/python

##################### Unit Tests #########################

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
      assert(authModule.userIsAdmin("test") == False)

   def testBadPassword(self):
      authModule = self._getUserDB()
      assert(not authModule.areUserCredentialsValid("test", "user2")) # Basic test
      assert(not authModule.areUserCredentialsValid("test", "User")) # password is case sensitive
      assert(not authModule.areUserCredentialsValid("test", "use")) # Match entire password
      assert(not authModule.areUserCredentialsValid("test", "")) # Match entire password

   def testBadUser(self):
      authModule = self._getUserDB()
      assert(not authModule.userExists("Test")) # username is case sensitive
      assert(not authModule.userExists("tes")) # Match entire username

   def testGoodUserDir(self):
      userDataModule = self._getUserDB()
      assert(userDataModule.getUserRepoPaths("test") == ["/data/bill", "/data/frank"])
      assert(userDataModule.getUserRoot("test") == "/data")

   def testBadUserReturn(self):
      userDataModule = self._getUserDB()
      assert(not userDataModule.getUserRepoPaths("test2")) # should return None if user doesn't exist
      assert(not userDataModule.getUserRoot("")) # should return None if user doesn't exist
      
   def testUserRepos(self):
      userDataModule = self._getUserDB()
      userDataModule.setUserRepos("test", [])
      userDataModule.setUserRepos("test", ["a", "b", "c"])
      self.assertEquals(userDataModule.getUserRepoPaths("test"), ["a", "b", "c"])
      # Make sure that repo max ages are initialized to 0
      maxAges = [ userDataModule.getRepoMaxAge("test", x) for x in userDataModule.getUserRepoPaths("test") ]
      self.assertEquals(maxAges, [0, 0, 0])
      userDataModule.setRepoMaxAge("test", "b", 1)
      self.assertEquals(userDataModule.getRepoMaxAge("test", "b"), 1)
      userDataModule.setUserRepos("test", ["b", "c", "d"])
      self.assertEquals(userDataModule.getRepoMaxAge("test", "b"), 1)
      self.assertEquals(userDataModule.getUserRepoPaths("test"), ["b", "c", "d"])
      
   def testRestoreFormat(self):
      userDataModule = self._getUserDB()
      assert(userDataModule.useZipFormat('test')) # Should default to using zip format
      userDataModule.setUseZipFormat('test', False)
      assert(not userDataModule.useZipFormat('test'))
      
