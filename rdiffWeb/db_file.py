#!/usr/bin/python

import rdw_config
import db

class fileUserDB(db.userDB):
   def __init__(self, configFilePath=None):
      self.configFilePath = configFilePath

   def userExists(self, username):
      valid_username = rdw_config.getConfigSetting("username", self.configFilePath)
      return valid_username == username

   def areUserCredentialsValid(self, username, password):
      """The valid users string in the config file is in the form:
         username=bill
         password=frank """
      valid_username = rdw_config.getConfigSetting("username", self.configFilePath)
      valid_password = rdw_config.getConfigSetting("password", self.configFilePath)
      return valid_username == username and valid_password == password

   def getUserRoot(self, username):
      if not self.userExists(username): return None
      return rdw_config.getConfigSetting("UserRoot", self.configFilePath)

   def getUserRepoPaths(self, username):
      """The user home dirs string in the config file is in the form of username:/data/dir|/data/dir2..."""
      if not self.userExists(username): return None
      return rdw_config.getConfigSetting("UserRepoPaths", self.configFilePath).split("|")

   def userIsAdmin(self, username):
      return False


##################### Unit Tests #########################

import unittest, os
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
      assert(not authModule.areUserCredentialsValid("test", "user2")) # Basic test
      assert(not authModule.areUserCredentialsValid("test", "User")) # password is case sensitive
      assert(not authModule.areUserCredentialsValid("test", "use")) # Match entire password
      assert(not authModule.areUserCredentialsValid("test", "")) # Make sure pipe at end doesn't allow blank username/password

   def testBadUser(self):
      authModule = fileUserDB(self.configFilePath)
      assert(not authModule.userExists("Test")) # username is case sensitive
      assert(not authModule.userExists("tes")) # Match entire username
      assert(not authModule.userExists("")) # Make sure blank username is disallowed

   def testGoodUserDir(self):
      userDataModule = fileUserDB(self.configFilePath)
      assert(userDataModule.getUserRepoPaths("test") == ["/data/bill", "/data/frank"])
      assert(userDataModule.getUserRoot("test") == "/data")

   def testBadUser(self):
      userDataModule = fileUserDB(self.configFilePath)
      assert(not userDataModule.getUserRepoPaths("test2")) # should return None if user doesn't exist
      assert(not userDataModule.getUserRoot("")) # should return None if user doesn't exist

if __name__ == "__main__":
   print "Called as standalone program; running unit tests..."
   fileUserDataTest = unittest.makeSuite(fileUserDataTest, 'test')
   testRunner = unittest.TextTestRunner()
   testRunner.run(fileUserDataTest)
