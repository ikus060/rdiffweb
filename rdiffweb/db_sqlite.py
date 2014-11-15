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

from __future__ import unicode_literals

import rdw_config
import db_sql
from rdw_helpers import encode_s, decode_s

"""We do no length validation for incoming parameters, since truncated values
will at worst lead to slightly confusing results, but no security risks"""


class sqliteUserDB:

    def __init__(self, configFilePath=None, autoConvertDatabase=True):
        self.configFilePath = configFilePath
        # Get database location.
        self._databaseFilePath = rdw_config.get_config(
            "SqliteDBFile", self.configFilePath)
        # If the database path is not define default to /etc/rdiffweb/rdw.db
        if self._databaseFilePath == "":
            self._databaseFilePath = "/etc/rdiffweb/rdw.db"

        self._autoConvertDatabase = autoConvertDatabase
        self.userRootCache = {}
        self._connect()
        self._migrateExistingData()

    def is_modifiable(self):
        return True

    def exists(self, username):
        assert isinstance(username, unicode)

        results = self._executeQuery(
            "SELECT Username FROM users WHERE Username = ?", (username,))
        return len(results) == 1

    def are_valid_credentials(self, username, password):
        assert isinstance(username, unicode)
        assert isinstance(password, unicode)

        results = self._executeQuery(
            "SELECT Username FROM users WHERE Username = ? AND Password = ?",
            (username, self._hashPassword(password)))
        return len(results) == 1

    def get_root_dir(self, username):
        assert isinstance(username, unicode)

        if username not in self.userRootCache:
            self.userRootCache[username] = self._encodePath(
                self._getUserField(username, "UserRoot"))
        return self.userRootCache[username]

    def get_repos(self, username):
        assert isinstance(username, unicode)

        if not self.exists(username):
            return None
        query = ("SELECT RepoPath FROM repos WHERE UserID = %d" %
                 self._getUserID(username))
        repos = [self._encodePath(row[0]) for row in self._executeQuery(query)]
        repos.sort(lambda x, y: cmp(x.upper(), y.upper()))
        return repos

    def get_email(self, username):
        assert isinstance(username, unicode)

        if not self.exists(username):
            return None
        return self._getUserField(username, "userEmail")

    def list(self):
        query = "SELECT UserName FROM users"
        users = [x[0] for x in self._executeQuery(query)]
        return users

    def add_user(self, username):
        assert isinstance(username, unicode)

        if self.exists(username):
            raise ValueError("user '%s' already exists" % username)
        query = "INSERT INTO users (Username) values (?)"
        self._executeQuery(query, (username,))

    def delete_user(self, username):
        assert isinstance(username, unicode)

        if not self.exists(username):
            raise ValueError
        self._delete_userRepos(username)
        query = "DELETE FROM users WHERE Username = ?"
        self._executeQuery(query, (username,))

    def set_info(self, username, userRoot, isAdmin):
        assert isinstance(username, unicode)

        if not self.exists(username):
            raise ValueError
        if isAdmin:
            adminInt = 1
        else:
            adminInt = 0
        query = "UPDATE users SET UserRoot=?, IsAdmin=" + \
            str(adminInt) + " WHERE Username = ?"
        self._executeQuery(query, (userRoot, username))
        # update cache
        self.userRootCache.pop(username, None)

    def set_email(self, username, email):
        assert isinstance(username, unicode)
        assert isinstance(email, unicode)

        if not self.exists(username):
            raise ValueError
        self._setUserField(username, 'UserEmail', email)

    def set_repos(self, username, repoPaths):
        assert isinstance(username, unicode)

        if not self.exists(username):
            raise ValueError
        userID = self._getUserID(username)

        # We don't want to just delete and recreate the repos, since that
        # would lose notification information.
        existingRepos = self.get_repos(username)
        reposToDelete = filter(lambda x: x not in repoPaths, existingRepos)
        reposToAdd = filter(lambda x: x not in existingRepos, repoPaths)

        # delete any obsolete repos
        for repo in reposToDelete:
            query = "DELETE FROM repos WHERE UserID=? AND RepoPath=?"
            self._executeQuery(query, (str(userID), repo))

        # add in new repos
        query = "INSERT INTO repos (UserID, RepoPath) values (?, ?)"
        repoPaths = [[str(userID), repo] for repo in reposToAdd]
        cursor = self.sqlConnection.cursor()
        cursor.executemany(query, repoPaths)

    def set_password(self, username, old_password, password):
        assert isinstance(username, unicode)
        assert old_password is None or isinstance(old_password, unicode)
        assert isinstance(password, unicode)

        if not self.exists(username):
            raise ValueError("invalid username")
        if not password:
            raise ValueError("password can't be empty")
        if old_password and not self.are_valid_credentials(username, old_password):
            raise ValueError("wrong password")
        self._setUserField(username, 'Password', self._hashPassword(password))

    def set_repo_maxage(self, username, repoPath, maxAge):
        assert isinstance(username, unicode)

        if repoPath not in self.get_repos(username):
            raise ValueError
        query = "UPDATE repos SET MaxAge=? WHERE RepoPath=? AND UserID = " + \
            str(self._getUserID(username))
        self._executeQuery(query, (maxAge, repoPath))

    def get_repo_maxage(self, username, repoPath):
        assert isinstance(username, unicode)

        query = "SELECT MaxAge FROM repos WHERE RepoPath=? AND UserID = " + \
            str(self._getUserID(username))
        results = self._executeQuery(query, (repoPath,))
        assert len(results) == 1
        return int(results[0][0])

    def is_admin(self, username):
        assert isinstance(username, unicode)

        return bool(self._getUserField(username, "IsAdmin"))

    def is_ldap(self):
        return False

    # Helper functions #
    def _encodePath(self, path):
        if not isinstance(path, unicode):
            return path.decode('utf-8')
        return path

    def _delete_userRepos(self, username):
        if not self.exists(username):
            raise ValueError
        self._executeQuery("DELETE FROM repos WHERE UserID=%d" %
                           self._getUserID(username))

    def _getUserID(self, username):
        assert self.exists(username)
        return self._getUserField(username, 'UserID')

    def _getUserField(self, username, fieldName):
        if not self.exists(username):
            return None
        query = "SELECT " + fieldName + " FROM users WHERE Username = ?"
        results = self._executeQuery(query, (username,))
        assert len(results) == 1
        return results[0][0]

    def _setUserField(self, username, fieldName, value):
        assert isinstance(username, unicode)
        assert isinstance(fieldName, unicode)
        assert not isinstance(value, str)

        if not self.exists(username):
            raise ValueError
        if isinstance(value, bool):
            if value:
                value = '1'
            else:
                value = '0'
        query = 'UPDATE users SET ' + fieldName + '=? WHERE Username=?'
        self._executeQuery(query, (value, username))

    def _hashPassword(self, password):
        # At this point the password should be unicode. We converted it into
        # system encoding.
        password_b = encode_s(password)
        import sha
        hasher = sha.new()
        hasher.update(password_b)
        return decode_s(hasher.hexdigest())

    def _executeQuery(self, query, args=()):
        assert isinstance(query, unicode)
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
        return [column[0] for column in
                self._executeQuery('select name from sqlite_master where type="table"')]

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
        """ If we don't have any data, we may be using a sqlite interface for
        the first time. See if they have another database backend specified,
        and if they do, try to migrate the data."""

        if self._getTables():
            return

        cursor = self.sqlConnection.cursor()
        cursor.execute("BEGIN TRANSACTION")
        for statement in self._getCreateStatements():
            cursor.execute(statement)

        if self._autoConvertDatabase:
            prevDBType = rdw_config.get_config(
                "UserDB", self.configFilePath)
            if prevDBType.lower() == "mysql":
                print 'Converting database from mysql...'
                import db_mysql
                prevDB = db_mysql.mysqlUserDB(self.configFilePath)
                users = prevDB._executeQuery(
                    "SELECT UserID, Username, Password, UserRoot, IsAdmin, UserEmail, RestoreFormat FROM users")
                cursor.executemany(
                    "INSERT INTO users (UserID, Username, Password, UserRoot, IsAdmin, UserEmail, RestoreFormat) values (?, ?, ?, ?, ?, ?, ?)", users)

                repos = prevDB._executeQuery(
                    "SELECT UserID, RepoPath, MaxAge FROM repos")
                cursor.executemany(
                    "INSERT INTO repos (UserID, RepoPath, MaxAge) values (?, ?, ?)", repos)
            elif prevDBType.lower() == "file":
                print 'Converting database from file...'
                import db_file
                prevDB = db_file.fileUserDB(self.configFilePath)
                username = rdw_config.get_config(
                    "username", self.configFilePath)
                password = rdw_config.get_config(
                    "password", self.configFilePath)
                self.add_user(username)
                self.set_password(username, None, password)
                self.set_info(username, prevDB.get_root_dir(username), True)
                self.set_repos(username, prevDB.get_repos(username))

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
