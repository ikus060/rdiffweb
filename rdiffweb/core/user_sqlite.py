#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

from rdiffweb.core import RdiffError
from rdiffweb.core.config import Option
from rdiffweb.core.i18n import ugettext as _

try:
    import sqlite3
except ImportError:
    from pysqlite2 import dbapi2 as sqlite3

try:
    # Python 2.5+
    from hashlib import sha1 as sha
except ImportError:
    from sha import new as sha

"""We do no length validation for incoming parameters, since truncated values
will at worst lead to slightly confusing results, but no security risks"""

# Define the logger
logger = logging.getLogger(__name__)


class SQLiteUserDB():

    _db_file = Option("SQLiteDBFile", "/etc/rdiffweb/rdw.db")

    def _bool(self, val):
        return str(val).lower() in ['true', '1']

    def __init__(self, app):
        """
        Called by the plugin manager to setup the plugin.
        """
        self.app = app

        # Declare a lock.
        self.create_tables_lock = RLock()
        self._create_or_update()

    def add_authorizedkey(self, username, fingerprint, key):
        assert isinstance(username, str)
        assert fingerprint
        assert key
        
        # Query user
        user_id = self._get_user_id(username)
        assert user_id, "user [%s] doesn't exists" % username
        try:
            self._execute_query(
                "INSERT INTO sshkeys (UserID, Fingerprint, Key) values (?, ?, ?)", (user_id, fingerprint, key))
        except sqlite3.IntegrityError:  # @UndefinedVariable
            raise ValueError(_("Duplicate key. This key already exists or is associated to another user."))

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
            return False
        if results[0][0] == self._hash_password(password):
            return results[0][1]
        return False

    def get_repos(self, username):
        """
        Get list of repos for the given `username`.
        """
        assert isinstance(username, str)
        assert self.exists(username), "user [%s] doesn't exists" % username
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

    def get_email(self, username):
        assert isinstance(username, str)
        return self._get_user_field(username, "UserEmail")

    def get_user_root(self, username):
        """Get user root directory."""
        assert isinstance(username, str)
        return self._get_user_field(username, "UserRoot")

    def get_authorizedkeys(self, username):
        assert isinstance(username, str)
        user_id = self._get_user_id(username)
        assert user_id, "user [%s] doesn't exists" % username
        query = ("SELECT Key FROM sshkeys WHERE UserID = %d" % user_id)
        return [row[0] for row in self._execute_query(query)]

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

    def add_user(self, username, password=None):
        """
        Add a new username to this userdb.
        """
        assert isinstance(username, str)
        logger.info("adding new user [%s]", username)
        if password:
            query = "INSERT INTO users (Username, Password) values (?, ?)"
            self._execute_query(query, (username, self._hash_password(password)))
        else:
            query = "INSERT INTO users (Username) values (?)"
            self._execute_query(query, (username,))

    def delete_user(self, username):
        """
        Delete the given `username`.
        """
        assert isinstance(username, str)
        
        # Check if user exists
        user_id = self._get_user_id(username)
        assert user_id, "user [%s] doesn't exists" % username
        
        # Delete user
        logger.info("deleting user [%s]", username)
        self._execute_query("DELETE FROM repos WHERE UserID=?", (user_id,))
        self._execute_query("DELETE FROM sshkeys WHERE UserID=?", (user_id,))
        self._execute_query("DELETE FROM users WHERE UserID = ?", (user_id,))

    def remove_authorizedkey(self, username, fingerprint):
        assert isinstance(username, str)
        assert fingerprint

        # Query user
        user_id = self._get_user_id(username)
        assert user_id, "user [%s] doesn't exists" % username
        self._execute_query(
            "DELETE FROM sshkeys WHERE UserID= ? AND Fingerprint = ?", (user_id, fingerprint))

    def set_is_admin(self, username, is_admin):
        assert isinstance(username, str)
        assert self.exists(username), "user [%s] doesn't exists" % username
        self._execute_query(
            "UPDATE users SET IsAdmin = ? WHERE Username = ?",
            (bool(is_admin), username))

    def set_email(self, username, email):
        assert isinstance(username, str)
        assert isinstance(email, str)
        self._set_user_field(username, 'UserEmail', email)

    def set_repos(self, username, repo_paths):
        assert isinstance(username, str)
        user_id = self._get_user_id(username)
        assert user_id, "user [%s] doesn't exists" % username

        # We don't want to just delete and recreate the repos, since that
        # would lose notification information.
        existing_repos = self.get_repos(username)
        repos_to_delete = [x for x in existing_repos if x not in repo_paths]
        repos_to_add = [x for x in repo_paths if x not in existing_repos]

        # delete any obsolete repos
        for repo in repos_to_delete:
            query = "DELETE FROM repos WHERE UserID=? AND RepoPath=?"
            self._execute_query(query, (user_id, repo))

        # add in new repos
        query = "INSERT INTO repos (UserID, RepoPath) values (?, ?)"
        repo_paths = [[user_id, repo] for repo in repos_to_add]
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.executemany(query, repo_paths)
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

        # Update field.
        query = "UPDATE repos SET %s=? WHERE RepoPath=? AND UserID = ?" % (key,)
        self._execute_query(query, (value, repo_path, self._get_user_id(username)))

    def set_user_root(self, username, user_root):
        assert isinstance(username, str)
        assert isinstance(user_root, str)
        self._set_user_field(username, 'UserRoot', user_root)

    def _get_user_id(self, username):
        return self._get_user_field(username, 'UserID')

    def _get_user_field(self, username, fieldname):
        query = "SELECT " + fieldname + " FROM users WHERE Username = ?"
        results = self._execute_query(query, (username,))
        assert len(results) == 1, "user [%s] doesn't exists" % username
        return results[0][0]

    def _set_user_field(self, username, fieldname, value):
        assert isinstance(username, str)
        assert isinstance(fieldname, str)
        assert isinstance(value, str) or isinstance(value, bool) or isinstance(value, int)
        assert self.exists(username), "user [%s] doesn't exists" % username
        if isinstance(value, bool):
            if value:
                value = '1'
            else:
                value = '0'
        query = 'UPDATE users SET ' + fieldname + '=? WHERE Username=?'
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
        conn = sqlite3.connect(self._db_file)
        conn.isolation_level = None
        return conn

    def _create_or_update(self):
        """
        Used to create or update the database.
        """

        # To avoid re-creating the table twice.
        with self.create_tables_lock:
            # Check if tables exists, if not created them.
            tables = self._get_tables()
            
            # Create the tables.
            conn = self._connect()
            cursor = conn.cursor()
            try:
                if not tables:
                    cursor.execute("BEGIN TRANSACTION")
                    cursor.execute("""create table users (
UserID integer primary key autoincrement,
Username varchar (50) unique NOT NULL,
Password varchar (40) NOT NULL DEFAULT "",
UserRoot varchar (255) NOT NULL DEFAULT "",
IsAdmin tinyint NOT NULL DEFAULT FALSE,
UserEmail varchar (255) NOT NULL DEFAULT "",
RestoreFormat tinyint NOT NULL DEFAULT TRUE)""")
                    cursor.execute("""create table repos (
RepoID integer primary key autoincrement,
UserID int(11) NOT NULL,
RepoPath varchar (255) NOT NULL,
MaxAge tinyint NOT NULL DEFAULT 0,
Encoding varchar (50))""")
                    cursor.execute("COMMIT TRANSACTION")

                # Create `keepdays` columns in repos
                self._create_column('repos', 'keepdays')
                
                # Create table for ssh Keys
                if 'sshkeys' not in tables:
                    cursor.execute("""create table sshkeys (
Fingerprint primary key,
Key clob UNIQUE,
UserID int(11) NOT NULL)""")

                # Create admin user                
                if not tables:
                    self.add_user('admin', 'admin123')
                    self.set_is_admin('admin', True)
                
            finally:
                conn.close()

    def _create_column(self, table, column, datatype='varchar(255)'):
        """
        Add a column to the tables.
        """
        # Check if column exists.
        if column.lower() in self._get_columns(table):
            return
        # Add column.
        self._execute_query('ALTER TABLE %s ADD COLUMN %s %s NOT NULL DEFAULT ""' % (table, column, datatype,))

    def _get_columns(self, table):
        """
        List columns for the given table.
        """
        assert table
        return [row[1].lower() for row in self._execute_query("pragma table_info('%s')" % (table,))]

    def _get_tables(self):
        return [
            column[0] for column in
            self._execute_query('select name from sqlite_master where type="table"')]
