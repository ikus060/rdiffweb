#!/usr/bin/python

import rdw_config
import db_sql

"""We do no length validation for incoming parameters, since truncated values will
at worst lead to slightly confusing results, but no security risks"""
class sqliteUserDB:
   def __init__(self, databaseFilePath, autoConvertDatabase=True):
      self._databaseFilePath = databaseFilePath
      self._autoConvertDatabase = autoConvertDatabase
      self.userRootCache = {}
      self._connect()
      self._migrateExistingData()

   def modificationsSupported(self):
      return True

   def userExists(self, username):
      results = self._executeQuery("SELECT Username FROM users WHERE Username = ?", (username,))
      return len(results) == 1

   def areUserCredentialsValid(self, username, password):
      results = self._executeQuery("SELECT Username FROM users WHERE Username = ? AND Password = ?", (username, self._hashPassword(password)))
      return len(results) == 1

   def getUserRoot(self, username):
      if not username in self.userRootCache:
         self.userRootCache[username] = self._encodePath(self._getUserField(username, "UserRoot"))
      return self.userRootCache[username]

   def getUserRepoPaths(self, username):
      if not self.userExists(username): return None
      query = "SELECT RepoPath FROM repos WHERE UserID = %d" % self._getUserID(username)
      repos = [ self._encodePath(row[0]) for row in self._executeQuery(query)]
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
      query = "INSERT INTO users (Username) values (?)"
      self._executeQuery(query, (username,))

   def deleteUser(self, username):
      if not self.userExists(username): raise ValueError
      self._deleteUserRepos(username)
      query = "DELETE FROM users WHERE Username = ?"
      self._executeQuery(query, (username,))

   def setUserInfo(self, username, userRoot, isAdmin):
      if not self.userExists(username): raise ValueError
      if isAdmin:
         adminInt = 1
      else:
         adminInt = 0
      query = "UPDATE users SET UserRoot=?, IsAdmin="+str(adminInt)+" WHERE Username = ?"
      self._executeQuery(query, (userRoot, username))
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
         query = "DELETE FROM repos WHERE UserID=? AND RepoPath=?"
         self._executeQuery(query, (str(userID), repo))
      
      # add in new repos
      query = "INSERT INTO repos (UserID, RepoPath) values (?, ?)"
      repoPaths = [ [str(userID), repo] for repo in reposToAdd ]
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
      query = "UPDATE repos SET MaxAge=? WHERE RepoPath=? AND UserID = " + str(self._getUserID(username))
      self._executeQuery(query, (maxAge, repoPath))
      
   def getRepoMaxAge(self, username, repoPath):
      query = "SELECT MaxAge FROM repos WHERE RepoPath=? AND UserID = " + str(self._getUserID(username))
      results = self._executeQuery(query, (repoPath,))
      assert len(results) == 1
      return int(results[0][0])
      
   def userIsAdmin(self, username):
      return bool(self._getUserField(username, "IsAdmin"))

   ########## Helper functions ###########   
   def _encodePath(self, path):
      if isinstance(path, unicode):
         return path.encode('utf-8')
      return path
   def _deleteUserRepos(self, username):
      if not self.userExists(username): raise ValueError
      self._executeQuery("DELETE FROM repos WHERE UserID=%d" % self._getUserID(username))

   def _getUserID(self, username):
      assert self.userExists(username)
      return self._getUserField(username, 'UserID')

   def _getUserField(self, username, fieldName):
      if not self.userExists(username): return None
      query = "SELECT "+fieldName+" FROM users WHERE Username = ?"
      results = self._executeQuery(query, (username,))
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
      query = 'UPDATE users SET '+fieldName+'=? WHERE Username=?'
      self._executeQuery(query, (valueStr, username))

   def _hashPassword(self, password):
      import sha
      hasher = sha.new()
      hasher.update(password)
      return hasher.hexdigest()
   
   def _executeQuery(self, query, args=()):
      cursor = self.sqlConnection.cursor()
      cursor.execute(query, args)
      results = cursor.fetchall()
      return results

   def _connect(self):
      try:
         import sqlite3
      except ImportError:
         from pysqlite2 import dbapi2 as sqlite3
         
      connectPath = self._databaseFilePath
      if not connectPath:
         connectPath = ":memory:"
      self.sqlConnection = sqlite3.connect(connectPath)
      self.sqlConnection.isolation_level = None
      
   def _getTables(self):
      return [column[0] for column in self._executeQuery('select name from sqlite_master where type="table"')]

   def _getCreateStatements(self):
      return [
"""create table users (
UserID integer primary key autoincrement,
Username varchar (50) unique NOT NULL,
Password varchar (40) NOT NULL DEFAULT "",
UserRoot varchar (255) NOT NULL DEFAULT "",
IsAdmin tinyint NOT NULL DEFAULT FALSE,
UserEmail varchar (255) NOT NULL DEFAULT "",
RestoreFormat tinyint NOT NULL DEFAULT TRUE)""",
"""create table repos (
RepoID integer primary key autoincrement,
UserID int(11) NOT NULL, 
RepoPath varchar (255) NOT NULL,
MaxAge tinyint NOT NULL DEFAULT 0)"""
 ]

   def _migrateExistingData(self):
      """ If we don't have any data, we may be using a sqlite interface for the first time.
      See if they have another database backend specified, and if they do, try to migrate the data."""
      
      if self._getTables(): return
      
      cursor = self.sqlConnection.cursor()
      cursor.execute("BEGIN TRANSACTION")
      for statement in self._getCreateStatements():
         cursor.execute(statement)

      if self._autoConvertDatabase:
         prevDBType = rdw_config.getConfigSetting("UserDB")
         if prevDBType.lower() == "mysql":
            print 'Converting database from mysql...'
            import db_mysql
            prevDB = db_mysql.mysqlUserDB()
            users = prevDB._executeQuery("SELECT UserID, Username, Password, UserRoot, IsAdmin, UserEmail, RestoreFormat FROM users")
            cursor.executemany("INSERT INTO users (UserID, Username, Password, UserRoot, IsAdmin, UserEmail, RestoreFormat) values (?, ?, ?, ?, ?, ?, ?)", users)
            
            repos = prevDB._executeQuery("SELECT UserID, RepoPath, MaxAge FROM repos")
            cursor.executemany("INSERT INTO repos (UserID, RepoPath, MaxAge) values (?, ?, ?)", repos)
         elif prevDBType.lower() == "file":
            print 'Converting database from file...'
            import db_file
            prevDB = db_file.fileUserDB()
            username = rdw_config.getConfigSetting("username")
            password = rdw_config.getConfigSetting("password")
            self.addUser(username)
            self.setUserPassword(username, password)
            self.setUserInfo(username, prevDB.getUserRoot(username), True)
            self.setUserRepos(username, prevDB.getUserRepoPaths(username))
         
      cursor.execute("COMMIT TRANSACTION")


class sqliteUserDBTest(db_sql.sqlUserDBTest):
   """Unit tests for the sqliteUserDBTeste class"""
   
   def _getUserDBObject(self):
      return sqliteUserDB(":memory:", autoConvertDatabase=False)
   
   def setUp(self):
      super(sqliteUserDBTest, self).setUp()
   
   def tearDown(self):
      pass

   def testUserTruncation(self):
      pass
      
