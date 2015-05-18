#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

from rdiffweb.rdw_plugin import IUserDBPlugin
from rdiffweb.rdw_helpers import encode_s, decode_s

"""We do no length validation for incoming parameters, since truncated values
will at worst lead to slightly confusing results, but no security risks"""


class SQLiteUserDB(IUserDBPlugin):

    def activate(self):
        """
        Called by the plugin manager to setup the plugin.
        """
        IUserDBPlugin.activate(self)

        # Get database location.
        self._db_file = self.app.config.get_config("SQLiteDBFile",
                                                   "/etc/rdiffweb/rdw.db")
        self._user_root_cache = {}
        self._create_or_update()

    def is_modifiable(self):
        """
        Return true if the UserDB is modifiable.
        """
        return True

    def exists(self, username):
        """
        Check if `username` exists.
        """
        assert isinstance(username, unicode)

        results = self._execute_query(
            "SELECT Username FROM users WHERE Username = ?", (username,))
        return len(results) == 1

    def are_valid_credentials(self, username, password):
        """
        Check if the given `username` and `password` are valid.
        """
        assert isinstance(username, unicode)
        assert isinstance(password, unicode)

        results = self._execute_query(
            "SELECT Username FROM users WHERE Username = ? AND Password = ?",
            (username, self._hash_password(password)))
        return len(results) == 1

    def get_root_dir(self, username):
        """
        Get user root directory.
        """
        assert isinstance(username, unicode)

        if username not in self._user_root_cache:
            self._user_root_cache[username] = self._encode_path(
                self._get_user_field(username, "UserRoot"))
        return self._user_root_cache[username]

    def get_repos(self, username):
        """
        Get list of repos for the given `username`.
        """
        assert isinstance(username, unicode)

        if not self.exists(username):
            return None
        query = ("SELECT RepoPath FROM repos WHERE UserID = %d" %
                 self._get_user_id(username))
        repos = [
            self._encode_path(row[0]) for row in self._execute_query(query)
            ]
        repos.sort(lambda x, y: cmp(x.upper(), y.upper()))
        return repos

    def get_email(self, username):
        assert isinstance(username, unicode)

        if not self.exists(username):
            return None
        return self._get_user_field(username, "userEmail")

    def list(self):
        """
        Return a list of username.
        """
        query = "SELECT UserName FROM users"
        users = [x[0] for x in self._execute_query(query)]
        return users

    def add_user(self, username):
        """
        Add a new username to this userdb.
        """
        assert isinstance(username, unicode)

        if self.exists(username):
            raise ValueError(_("user '%s' already exists") % username)
        query = "INSERT INTO users (Username) values (?)"
        self._execute_query(query, (username,))

    def delete_user(self, username):
        """
        Delete the given `username`.
        """
        assert isinstance(username, unicode)

        if not self.exists(username):
            raise ValueError
        self._delete_user_repos(username)
        query = "DELETE FROM users WHERE Username = ?"
        self._execute_query(query, (username,))

    def set_info(self, username, user_root, is_admin):
        assert isinstance(username, unicode)

        if not self.exists(username):
            raise ValueError
        # Remove the user from the cache before
        # updating the database.
        self._user_root_cache.pop(username, None)
        if is_admin:
            admin_int = 1
        else:
            admin_int = 0
        query = "UPDATE users SET UserRoot=?, IsAdmin=" + \
            str(admin_int) + " WHERE Username = ?"
        self._execute_query(query, (user_root, username))

    def set_email(self, username, email):
        assert isinstance(username, unicode)
        assert isinstance(email, unicode)

        if not self.exists(username):
            raise ValueError
        self._set_user_field(username, 'UserEmail', email)

    def set_repos(self, username, repoPaths):
        assert isinstance(username, unicode)

        if not self.exists(username):
            raise ValueError
        userID = self._get_user_id(username)

        # We don't want to just delete and recreate the repos, since that
        # would lose notification information.
        existingRepos = self.get_repos(username)
        reposToDelete = filter(lambda x: x not in repoPaths, existingRepos)
        reposToAdd = filter(lambda x: x not in existingRepos, repoPaths)

        # delete any obsolete repos
        for repo in reposToDelete:
            query = "DELETE FROM repos WHERE UserID=? AND RepoPath=?"
            self._execute_query(query, (str(userID), repo))

        # add in new repos
        query = "INSERT INTO repos (UserID, RepoPath) values (?, ?)"
        repoPaths = [[str(userID), repo] for repo in reposToAdd]
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, repoPaths)
        finally:
            conn.close()

    def set_password(self, username, old_password, password):
        assert isinstance(username, unicode)
        assert old_password is None or isinstance(old_password, unicode)
        assert isinstance(password, unicode)

        if not self.exists(username):
            raise ValueError(_("invalid username"))
        if not password:
            raise ValueError(_("password can't be empty"))
        if old_password and not self.are_valid_credentials(username, old_password):
            raise ValueError(_("wrong password"))
        self._set_user_field(username, 'Password', self._hash_password(password))

    def set_repo_maxage(self, username, repoPath, maxAge):
        assert isinstance(username, unicode)

        if repoPath not in self.get_repos(username):
            raise ValueError
        query = "UPDATE repos SET MaxAge=? WHERE RepoPath=? AND UserID = " + \
            str(self._get_user_id(username))
        self._execute_query(query, (maxAge, repoPath))

    def get_repo_maxage(self, username, repoPath):
        assert isinstance(username, unicode)

        query = "SELECT MaxAge FROM repos WHERE RepoPath=? AND UserID = " + \
            str(self._get_user_id(username))
        results = self._execute_query(query, (repoPath,))
        assert len(results) == 1
        return int(results[0][0])

    def is_admin(self, username):
        assert isinstance(username, unicode)

        return bool(self._get_user_field(username, "IsAdmin"))

    def is_ldap(self):
        return False

    # Helper functions #
    def _encode_path(self, path):
        if isinstance(path, str):
            # convert to unicode...
            return path.decode('utf-8')
        return path

    def _delete_user_repos(self, username):
        if not self.exists(username):
            raise ValueError
        self._execute_query("DELETE FROM repos WHERE UserID=%d" %
                            self._get_user_id(username))

    def _get_user_id(self, username):
        assert self.exists(username)
        return self._get_user_field(username, 'UserID')

    def _get_user_field(self, username, fieldName):
        if not self.exists(username):
            return None
        query = "SELECT " + fieldName + " FROM users WHERE Username = ?"
        results = self._execute_query(query, (username,))
        assert len(results) == 1
        return results[0][0]

    def _set_user_field(self, username, fieldName, value):
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
        self._execute_query(query, (value, username))

    def _hash_password(self, password):
        # At this point the password should be unicode. We converted it into
        # system encoding.
        password_b = encode_s(password)
        import sha
        hasher = sha.new()
        hasher.update(password_b)
        return decode_s(hasher.hexdigest())

    def _execute_query(self, query, args=()):
        assert isinstance(query, unicode)
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query, args)
            results = cursor.fetchall()
        finally:
            conn.close()
        return results

    def _connect(self):
        """
        Called to create a new connection to database.
        """
        try:
            import sqlite3
        except ImportError:
            from pysqlite2 import dbapi2 as sqlite3

        connect_path = self._db_file
        if not connect_path:
            connect_path = ":memory:"
        conn = sqlite3.connect(connect_path)
        conn.isolation_level = None
        return conn

    def _create_or_update(self):
        """
        Used to create or update the database.
        """

        # Check if tables exists, if not created them.
        if self._get_tables():
            return

        # Create the tables.
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute("BEGIN TRANSACTION")
            for statement in self._get_create_statements():
                cursor.execute(statement)
            cursor.execute("COMMIT TRANSACTION")
        finally:
            conn.close()

    def _get_tables(self):
        return [
            column[0] for column in
            self._execute_query('select name from sqlite_master where type="table"')]

    def _get_create_statements(self):
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


import unittest


class SQLiteUserDBTest(unittest.TestCase):

    """Unit tests for the sqliteUserDBTeste class"""

    def _getUserDBObject(self):
        return SQLiteUserDB(":memory:", autoConvertDatabase=False)

    def setUp(self):
        super(SQLiteUserDBTest, self).setUp()

    def _getUserDB(self):
        userData = self._getUserDBObject()
        if not userData._get_tables():
            for statement in userData._get_create_statements():
                userData._execute_query(statement)

        userData.add_user("test")
        userData.set_info("test", "/data", False)
        userData.set_password("test", None, "user")
        userData.set_repos("test", ["/data/bill", "/data/frank"])
        return userData

    def tearDown(self):
        userData = self._getUserDB()
        tableNames = userData._get_tables()
        print tableNames
        if 'users' in tableNames:
            userData._execute_query("DROP TABLE users")
        if 'repos' in tableNames:
            userData._execute_query("DROP TABLE repos")

    def testValidUser(self):
        authModule = self._getUserDB()
        assert(authModule.exists("test"))
        assert(authModule.are_valid_credentials("test", "user"))

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
