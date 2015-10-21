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

from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_plugin import IPasswordStore, IDatabase
from rdiffweb.rdw_helpers import encode_s, decode_s
from threading import RLock
from rdiffweb.core import InvalidUserError
import logging

"""We do no length validation for incoming parameters, since truncated values
will at worst lead to slightly confusing results, but no security risks"""

# Define the logger
logger = logging.getLogger(__name__)


class SQLiteUserDB(IPasswordStore, IDatabase):

    def _bool(self, val):
        return str(val).lower() in ['true', '1']

    def activate(self):
        """
        Called by the plugin manager to setup the plugin.
        """
        super(SQLiteUserDB, self).activate()

        # Declare a lock.
        self.create_tables_lock = RLock()

        # Get database location.
        self._db_file = self.app.cfg.get_config("SQLiteDBFile",
                                                "/etc/rdiffweb/rdw.db")
        self._user_root_cache = {}
        self._create_or_update()

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
        logger.info("validating user [%s] credentials", username)
        results = self._execute_query(
            "SELECT Password, Username FROM users WHERE Username = ?",
            (username,))
        if not len(results):
            return None
        if results[0][0] == self._hash_password(password):
            return results[0][1]
        return False

    def get_user_root(self, username):
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
            raise InvalidUserError(username)
        query = ("SELECT RepoPath FROM repos WHERE UserID = %d" %
                 self._get_user_id(username))
        repos = [
            self._encode_path(row[0]) for row in self._execute_query(query)
        ]
        repos.sort(lambda x, y: cmp(x.upper(), y.upper()))
        return repos

    def get_repo_maxage(self, username, repoPath):
        assert isinstance(username, unicode)

        query = "SELECT MaxAge FROM repos WHERE RepoPath=? AND UserID = " + \
            str(self._get_user_id(username))
        results = self._execute_query(query, (repoPath,))
        assert len(results) == 1
        return int(results[0][0])

    def get_email(self, username):
        assert isinstance(username, unicode)
        return self._get_user_field(username, "UserEmail")

    def get_user_root(self, username):
        assert isinstance(username, unicode)
        return self._get_user_field(username, "UserRoot")

    def is_admin(self, username):
        assert isinstance(username, unicode)
        value = self._get_user_field(username, "IsAdmin")
        return self._bool(value)

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
        logger.info("adding new user [%s]", username)
        query = "INSERT INTO users (Username) values (?)"
        self._execute_query(query, (username,))

    def delete_user(self, username):
        """
        Delete the given `username`.
        """
        assert isinstance(username, unicode)
        # Check if user exists
        if not self.exists(username):
            return False
        # Delete user
        logger.info("deleting user [%s]", username)
        self._execute_query("DELETE FROM repos WHERE UserID=%d" %
                            self._get_user_id(username))
        self._execute_query("DELETE FROM users WHERE Username = ?",
                            (username,))
        return True

    def set_is_admin(self, username, is_admin):
        assert isinstance(username, unicode)
        if not self.exists(username):
            raise InvalidUserError(username)
        if is_admin:
            admin_int = 1
        else:
            admin_int = 0
        self._execute_query(
            "UPDATE users SET IsAdmin = ? WHERE Username = ?",
            (admin_int, username))

    def set_email(self, username, email):
        assert isinstance(username, unicode)
        assert isinstance(email, unicode)
        self._set_user_field(username, 'UserEmail', email)

    def set_repos(self, username, repoPaths):
        assert isinstance(username, unicode)
        if not self.exists(username):
            raise InvalidUserError(username)
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

    def set_password(self, username, password, old_password=None):
        assert isinstance(username, unicode)
        assert old_password is None or isinstance(old_password, unicode)
        assert isinstance(password, unicode)
        if not password:
            raise ValueError(_("password can't be empty"))

        # Check old password value.
        if old_password and not self.are_valid_credentials(username, old_password):
            raise ValueError(_("wrong password"))

        # Update password.
        self._set_user_field(username, 'Password', self._hash_password(password))

    def set_repo_maxage(self, username, repoPath, maxAge):
        assert isinstance(username, unicode)
        if repoPath not in self.get_repos(username):
            raise ValueError
        query = "UPDATE repos SET MaxAge=? WHERE RepoPath=? AND UserID = " + \
            str(self._get_user_id(username))
        self._execute_query(query, (maxAge, repoPath))

    def set_user_root(self, username, user_root):
        assert isinstance(username, unicode)
        assert isinstance(user_root, unicode)
        if not self.exists(username):
            raise InvalidUserError(username)
        # Remove the user from the cache before
        # updating the database.
        self._user_root_cache.pop(username, None)
        self._execute_query(
            "UPDATE users SET UserRoot=? WHERE Username = ?",
            (user_root, username))

    # Helper functions #
    def _encode_path(self, path):
        if isinstance(path, str):
            # convert to unicode...
            return path.decode('utf-8')
        return path

    def _get_user_id(self, username):
        assert self.exists(username)
        return self._get_user_field(username, 'UserID')

    def _get_user_field(self, username, fieldName):
        if not self.exists(username):
            raise InvalidUserError(username)
        query = "SELECT " + fieldName + " FROM users WHERE Username = ?"
        results = self._execute_query(query, (username,))
        assert len(results) == 1
        return results[0][0]

    def _set_user_field(self, username, fieldName, value):
        assert isinstance(username, unicode)
        assert isinstance(fieldName, unicode)
        assert not isinstance(value, str)

        if not self.exists(username):
            raise InvalidUserError(username)
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

        # To avoid re-creating the table twice.
        with self.create_tables_lock:

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

            # Create admin user
            self.set_password('admin', 'admin123', old_password=None)
            self.set_user_root('admin', '/backups/')
            self.set_is_admin('admin', True)

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

    def supports(self, operation):
        return hasattr(self, operation)
