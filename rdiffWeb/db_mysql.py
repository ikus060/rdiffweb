#!/usr/bin/python

import db_sql
import rdw_config
import warnings

"""We do no length validation for incoming parameters, since truncated values will
at worst lead to slightly confusing results, but no security risks"""
class mysqlUserDB:
   def __init__(self, configFilePath=None):
      import MySQLdb
      self.configFilePath = configFilePath
      MySQLdb.paramstyle = "pyformat"
      self.userRootCache = {}
      self._connect()
      self._updateToLatestFormat()

   def modificationsSupported(self):
      return True

   def userExists(self, username):
      results = self._executeQuery("SELECT Username FROM users WHERE Username = %(user)s", user=username)
      return len(results) == 1

   def areUserCredentialsValid(self, username, password):
      results = self._executeQuery("SELECT Username FROM users WHERE Username = %(user)s AND Password = %(password)s", user=username, password=self._hashPassword(password))
      return len(results) == 1

   def getUserRoot(self, username):
      if not username in self.userRootCache:
         self.userRootCache[username] = self._getUserField(username, "UserRoot")
      return self.userRootCache[username]

   def getUserRepoPaths(self, username):
      if not self.userExists(username): return None
      query = "SELECT RepoPath FROM repos WHERE UserID = %d" % self._getUserID(username)
      repos = [ row[0] for row in self._executeQuery(query)]
      repos.sort(lambda x, y: cmp(x.upper(), y.upper()))
      return repos
      
   def getUserEmail(self, username):
      if not self.userExists(username): return None
      return self._getUserField(username, "userEmail")
   
   def useZipFormat(self, username):
      if not self.userExists(username): return False
      return bool(self._getUserField(username, "restoreFormat"))

   def getUserList(self):
      query = "SELECT UserName FROM users"
      users = [x[0] for x in self._executeQuery(query)]
      return users

   def addUser(self, username):
      if self.userExists(username): raise ValueError
      query = "INSERT INTO users (Username) values (%(user)s)"
      self._executeQuery(query, user=username)

   def deleteUser(self, username):
      if not self.userExists(username): raise ValueError
      self._deleteUserRepos(username)
      query = "DELETE FROM users WHERE Username = %(user)s"
      self._executeQuery(query, user=username)

   def setUserInfo(self, username, userRoot, isAdmin):
      if not self.userExists(username): raise ValueError
      if isAdmin:
         adminInt = 1
      else:
         adminInt = 0
      query = "UPDATE users SET UserRoot=%(userRoot)s, IsAdmin="+str(adminInt)+" WHERE Username = %(user)s"
      self._executeQuery(query, userRoot=userRoot, user=username)
      self.userRootCache[username] = userRoot # update cache

   def setUserEmail(self, username, userEmail):
      if not self.userExists(username): raise ValueError
      self._setUserField(username, 'UserEmail', userEmail)
      
   def setUserRepos(self, username, repoPaths):
      if not self.userExists(username): raise ValueError
      userID = self._getUserID(username)
      
      # We don't want to just delete and recreate the repos, since that
      # would lose notification information.      
      existingRepos = self.getUserRepoPaths(username)      
      reposToDelete = filter(lambda x: not x in repoPaths, existingRepos)
      reposToAdd = filter(lambda x: not x in existingRepos, repoPaths)
      
      # delete any obsolete repos
      for repo in reposToDelete:
         query = "DELETE FROM repos WHERE UserID=%(userID)s AND RepoPath= BINARY %(repo)s"
         self._executeQuery(query, repo=repo, userID=str(userID))
      
      # add in new repos
      query = "INSERT INTO repos (UserID, RepoPath) values (%s, %s)"
      repoPaths = [ (str(userID), repo) for repo in reposToAdd ]
      cursor = self.sqlConnection.cursor()
      cursor.executemany(query, repoPaths)

   def setUserPassword(self, username, password):
      if not self.userExists(username): raise ValueError
      self._setUserField(username, 'Password', self._hashPassword(password))
   
   def setUseZipFormat(self, username, useZip):
      if not self.userExists(username): raise ValueError
      self._setUserField(username, 'RestoreFormat', bool(useZip))
      
   def setRepoMaxAge(self, username, repoPath, maxAge):
      if not repoPath in self.getUserRepoPaths(username): raise ValueError
      query = "UPDATE repos SET MaxAge=%(maxAge)s WHERE RepoPath = BINARY %(repoPath)s AND UserID = " + str(self._getUserID(username))
      self._executeQuery(query, maxAge=maxAge, repoPath=repoPath)
      
   def getRepoMaxAge(self, username, repoPath):
      query = "SELECT MaxAge FROM repos WHERE RepoPath = BINARY %(repoPath)s AND UserID = " + str(self._getUserID(username))
      results = self._executeQuery(query, repoPath=repoPath)
      assert len(results) == 1
      return int(results[0][0])
      
   def userIsAdmin(self, username):
      return bool(self._getUserField(username, "IsAdmin"))

   ########## Helper functions ###########   
   def _deleteUserRepos(self, username):
      if not self.userExists(username): raise ValueError
      self._executeQuery("DELETE FROM repos WHERE UserID=%d" % self._getUserID(username))

   def _getUserID(self, username):
      assert self.userExists(username)
      return self._getUserField(username, 'UserID')

   def _getUserField(self, username, fieldName):
      if not self.userExists(username): return None
      query = "SELECT "+fieldName+" FROM users WHERE Username = %(user)s"
      results = self._executeQuery(query, user=username)
      assert len(results) == 1
      return results[0][0]
      
   def _setUserField(self, username, fieldName, value):
      if not self.userExists(username): raise ValueError
      if isinstance(value, bool):
         if value:
            valueStr = '1'
         else:
            valueStr = '0'
      else:
         valueStr = str(value)
      query = 'UPDATE users SET '+fieldName+'=%(value)s WHERE Username=%(user)s'
      self._executeQuery(query, value=valueStr, user=username)

   def _internalExecuteQuery(self, query, **kwargs):
      cursor = self.sqlConnection.cursor()
      cursor.execute(query, kwargs)
      return cursor.fetchall()

   def _executeQuery(self, query, **kwargs):
      # The mysql server connection times out after a while.  Catch this, and try again
      import MySQLdb
      try:
         return self._internalExecuteQuery(query, **kwargs)
      except MySQLdb.OperationalError:
         self._connect()
         return self._internalExecuteQuery(query, **kwargs)

   def _connect(self):
      import MySQLdb
      sqlHost = rdw_config.getConfigSetting("sqlHost", self.configFilePath)
      sqlUsername = rdw_config.getConfigSetting("sqlUsername", self.configFilePath)
      sqlPassword = rdw_config.getConfigSetting("sqlPassword", self.configFilePath)
      sqlDatabaseName = rdw_config.getConfigSetting("sqlDatabase", self.configFilePath)
      self.sqlConnection = MySQLdb.connect(host=sqlHost, user=sqlUsername, passwd=sqlPassword,db=sqlDatabaseName)

   def _hashPassword(self, password):
      import sha
      hasher = sha.new()
      hasher.update(password)
      return hasher.hexdigest()

   def _getCreateStatements(self):
      return [
"""create table users (
UserID int(11) NOT NULL auto_increment,
Username varchar (50) binary unique NOT NULL,
Password varchar (40) NOT NULL DEFAULT "",
UserRoot varchar (255) NOT NULL DEFAULT "",
IsAdmin tinyint NOT NULL DEFAULT FALSE,
UserEmail varchar (255) NOT NULL DEFAULT "",
RestoreFormat tinyint NOT NULL DEFAULT TRUE,
primary key (UserID) )""",
"""create table repos (
RepoID int(11) NOT NULL auto_increment,
UserID int(11) NOT NULL, 
RepoPath varchar (255) NOT NULL,
MaxAge tinyint NOT NULL DEFAULT 0,
primary key (RepoID))"""
 ]
               
   def _updateToLatestFormat(self):
      # Make sure that we have tables. If we don't, just quit.
      tableNames = [table[0].lower() for table in self._executeQuery("show tables")]
      if not tableNames: return
      
      # Make sure that the users table has a "email" column
      columnNames = [column[0].lower() for column in self._executeQuery("describe users")]
      if not "useremail" in columnNames:
         self._executeQuery('alter table users add column UserEmail varchar (255) NOT NULL DEFAULT ""')
         
      # Make sure that the repos table has a "MaxAge" column
      columnNames = [column[0].lower() for column in self._executeQuery("describe repos")]
      if not "maxage" in columnNames:
         self._executeQuery('alter table repos add column MaxAge tinyint NOT NULL DEFAULT 0')
      
      # Make sure that the users table has a "restoreFormat" column
      columnNames = [column[0].lower() for column in self._executeQuery("describe users")]
      if not "restoreformat" in columnNames:
         self._executeQuery('alter table users add column RestoreFormat tinyint NOT NULL DEFAULT TRUE')
         
   def _getTables(self):
      return [table[0].lower() for table in self._executeQuery("show tables")]


##################### Unit Tests #########################

import unittest, os
class mysqlUserDBTest(db_sql.sqlUserDBTest):
   """Unit tests for the mysqlUserDBTest class"""
   configFileData = """sqlHost=localhost
                       sqlUsername=
                       sqlPassword=
                       sqlDatabase=test"""
   configFilePath = "/tmp/rdw_config.conf"
   
   def _getUserDBObject(self):
      return mysqlUserDB(self.configFilePath)

   def setUp(self):
      file = open(self.configFilePath, "w")
      file.write(self.configFileData)
      file.close()
      self.tearDown()
      file = open(self.configFilePath, "w")
      file.write(self.configFileData)
      file.close()

   def tearDown(self):
      userData = mysqlUserDB(self.configFilePath)
      tableNames = [table[0].lower() for table in userData._executeQuery("show tables")]
      if 'users' in tableNames:
         userData._executeQuery("DROP TABLE IF EXISTS users;")
      if 'repos' in tableNames:
         userData._executeQuery("DROP TABLE IF EXISTS repos;")
      if (os.access(self.configFilePath, os.F_OK)):
         os.remove(self.configFilePath)

   def testUserTruncation(self):
      warnings.filterwarnings('ignore', message='Data truncated')
      import MySQLdb
      authModule = self._getUserDB()
      authModule.addUser("bill" * 1000)
      try:
         authModule.addUser("bill" * 1000 + "test")
      except MySQLdb.IntegrityError:
         pass
      else:
         assert(false)
      warnings.resetwarnings()
      
