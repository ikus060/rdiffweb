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
"""
SQLite UserDB backend used to store users data and credentials
into a SQLite database.
"""

from __future__ import unicode_literals

from builtins import str
import logging
from threading import RLock

from rdiffweb.core import InvalidUserError, RdiffError
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_plugin import IPasswordStore, IDatabase
from rdiffweb.user import UserObject


try:
    # Python 2.5+
    from hashlib import sha1 as sha
except ImportError:
    from sha import new as sha

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
        super(IPasswordStore, self).activate()

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
        assert isinstance(username, str)

        results = self._execute_query(
            "SELECT Username FROM users WHERE Username = ?", (username,))
        return len(results) == 1

    def are_valid_credentials(self, username, password):
        """
        Check if the given `username` and `password` are valid.
        """
        assert isinstance(username, str)
        assert isinstance(password, str)
        logger.info("validating user [%s] credentials", username)
        results = self._execute_query(
            "SELECT Password, Username FROM users WHERE Username = ?",
            (username,))
        if not len(results):
            return None
        if results[0][0] == self._hash_password(password):
            return results[0][1]
        return False

    def get_repos(self, username):
        """
        Get list of repos for the given `username`.
        """
        assert isinstance(username, str)
        if not self.exists(username):
            raise InvalidUserError(username)
        query = ("SELECT RepoPath FROM repos WHERE UserID = %d" %
                 self._get_user_id(username))
        return [row[0] for row in self._execute_query(query)]

    def get_repo_attr(self, username, repo_path, key, default=None):
        """
        Get repository attribute.
        """
        assert isinstance(username, str)
        assert isinstance(repo_path, str)
        query = "SELECT %s FROM repos WHERE RepoPath=? AND UserID = ?" % (key,)
        try:
            results = self._execute_query(query, (repo_path, self._get_user_id(username)))
            if len(results) == 0 or not results[0][0]:
                return default
            return results[0][0]
        except:
            return default

    def get_repo_maxage(self, username, repoPath):
        assert isinstance(username, str)
        query = "SELECT MaxAge FROM repos WHERE RepoPath=? AND UserID = ?"
        results = self._execute_query(query, (repoPath, self._get_user_id(username)))
        assert len(results) == 1
        return int(results[0][0])

    def get_email(self, username):
        assert isinstance(username, str)
        return self._get_user_field(username, "UserEmail")

    def get_user_root(self, username):
        """Get user root directory."""
        assert isinstance(username, str)

        if username not in self._user_root_cache:
            self._user_root_cache[username] = self._get_user_field(username, "UserRoot")

        return self._user_root_cache[username]

    def has_password(self, username):
        """Check if the given user has a password in database."""
        try:
            return bool(self._get_user_field(username, "Password"))
        except InvalidUserError:
            return False

    def is_admin(self, username):
        assert isinstance(username, str)
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
        assert isinstance(username, str)
        logger.info("adding new user [%s]", username)
        query = "INSERT INTO users (Username) values (?)"
        self._execute_query(query, (username,))

    def delete_user(self, username):
        """
        Delete the given `username`.
        """
        assert isinstance(username, str)
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
        assert isinstance(username, str)
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
        assert isinstance(username, str)
        assert isinstance(email, str)
        self._set_user_field(username, 'UserEmail', email)

    def set_repos(self, username, repoPaths):
        assert isinstance(username, str)
        if not self.exists(username):
            raise InvalidUserError(username)
        user_id = self._get_user_id(username)

        # We don't want to just delete and recreate the repos, since that
        # would lose notification information.
        existingRepos = self.get_repos(username)
        reposToDelete = [x for x in existingRepos if x not in repoPaths]
        reposToAdd = [x for x in repoPaths if x not in existingRepos]

        # delete any obsolete repos
        for repo in reposToDelete:
            query = "DELETE FROM repos WHERE UserID=? AND RepoPath=?"
            self._execute_query(query, (user_id, repo))

        # add in new repos
        query = "INSERT INTO repos (UserID, RepoPath) values (?, ?)"
        repoPaths = [[user_id, repo] for repo in reposToAdd]
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, repoPaths)
        finally:
            conn.close()

    def set_password(self, username, password, old_password=None):
        assert isinstance(username, str)
        assert old_password is None or isinstance(old_password, str)
        assert isinstance(password, str)
        if not password:
            raise RdiffError(_("Password can't be empty."))

        # Check old password value.
        if old_password and not self.are_valid_credentials(username, old_password):
            raise RdiffError(_("Wrong password."))

        # Update password.
        self._set_user_field(username, 'Password', self._hash_password(password))

    def set_repo_attr(self, username, repo_path, key, value):
        assert repo_path
        assert isinstance(key, str) and key.isalpha() and key.islower()

        # Add column if required.
        self._create_column('repos', key)

        # Update field.
        query = "UPDATE repos SET %s=? WHERE RepoPath=? AND UserID = ?" % (key,)
        self._execute_query(query, (value, repo_path, self._get_user_id(username)))

    def set_repo_maxage(self, username, repoPath, maxAge):
        assert isinstance(username, str)
        assert repoPath in self.get_repos(username)
        query = "UPDATE repos SET MaxAge=? WHERE RepoPath=? AND UserID = ?"
        self._execute_query(query, (maxAge, repoPath, self._get_user_id(username)))

    def set_user_root(self, username, user_root):
        assert isinstance(username, str)
        assert isinstance(user_root, str)
        if not self.exists(username):
            raise InvalidUserError(username)
        # Remove the user from the cache before
        # updating the database.
        self._user_root_cache.pop(username, None)
        self._execute_query(
            "UPDATE users SET UserRoot=? WHERE Username = ?",
            (user_root, username))

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
        assert isinstance(username, str)
        assert isinstance(fieldName, str)
        assert isinstance(value, str) or isinstance(value, bool) or isinstance(value, int)

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
        password_b = password.encode('utf8')
        hasher = sha()
        hasher.update(password_b)
        value = hasher.hexdigest()
        if isinstance(value, bytes):
            value = value.decode(encoding='latin1')
        return value

    def _execute_query(self, query, args=()):
        assert isinstance(query, str)
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
            self.add_user('admin')
            self.set_password('admin', 'admin123', old_password=None)
            self.set_user_root('admin', '/backups/')
            self.set_is_admin('admin', True)

    def _create_column(self, table, column):
        """
        Add a column to the tables.
        """
        # Check if column exists.
        if column in self._get_columns(table):
            return
        # Add column.
        self._execute_query('ALTER TABLE %s ADD COLUMN %s varchar(255) NOT NULL DEFAULT ""' % (table, column,))

    def _get_columns(self, table):
        """
        List columns for the given table.
        """
        assert table
        return [row[1] for row in self._execute_query("pragma table_info('%s')" % (table,))]

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
