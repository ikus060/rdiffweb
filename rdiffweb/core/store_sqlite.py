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


import logging
import sqlite3
import sys
from threading import RLock

from rdiffweb.core.store import ADMIN_ROLE, USER_ROLE


# Define the logger
logger = logging.getLogger(__name__)

# List of tables
_TABLES = ['users', 'repos', 'sshkeys']


def _dict_factory(cursor, row):
    """
    Returning an object that can also access columns by name.
    """
    d = {}
    for idx, col in enumerate(cursor.description):
        col = col[0].lower()
        # For SQLite <= 3.16.2 tinyint default value are return as string.
        if col in ['isadmin', 'restoreformat']:
            d[col] = 1 if row[idx] == 1 or row[idx] == 'TRUE' else 0
        else:
            d[col] = row[idx]
    return d


def _validate_model(model):
    if model not in _TABLES:
        raise ValueError(model + " is not a valid table name")


def _where(fields):
    """
    Create the WHERE clause from the given fields.
    """
    if not fields:
        return ""
    return " WHERE " + ' AND '.join(['%s = ?' % f for f in fields])


class SQLiteBackend():
    """
    SQLite data base backend to do CRUD operation.
    """

    def __init__(self, db_file):
        """
        Called by the plugin manager to setup the plugin.
        """
        self._db_file = db_file
        # Declare a lock.
        self.create_tables_lock = RLock()
        self._create_or_update()

    def _get_id(self, model, **kwargs):
        """
        Return the primary key fields of the given model.
        """
        _validate_model(model)
        if 'users' == model:
            if 'userid' in kwargs:
                return ['userid']
            return ['username']
        elif 'repos' == model:
            if 'repoid' in kwargs:
                return ['repoid']
            return ['userid', 'repopath']
        elif 'sshkeys' == model:
            return ['fingerprint']
        return None

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
                self._create_column('repos', 'encoding', datatype='varchar(30)')

                # Create table for ssh Keys
                if 'sshkeys' not in tables:
                    cursor.execute("""create table sshkeys (
Fingerprint primary key,
Key clob UNIQUE,
UserID int(11) NOT NULL)""")

                # Create column for roles using "isadmin" column. Keep the
                # original column in case we need to revert to previous version. 
                if 'role'.lower() not in self._get_columns('users'):
                    self._rowcount('ALTER TABLE users ADD COLUMN role tinyint NOT NULL DEFAULT "%s"' % (USER_ROLE,))
                    cursor.execute('UPDATE users SET role = %s WHERE isadmin=1' % (ADMIN_ROLE,))

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
        self._rowcount('ALTER TABLE %s ADD COLUMN %s %s NOT NULL DEFAULT ""' % (table, column, datatype,))

    def _fetchall(self, sql, args=[]):
        conn = self._connect()
        conn.row_factory = _dict_factory
        try:
            cursor = conn.cursor()
            cursor.execute(sql, args)
            # We want to return either the rowcount or the list or record.
            return cursor.fetchall()
        finally:
            conn.close()

    def _get_columns(self, table):
        """
        List columns for the given table.
        """
        assert table
        return [record['name'].lower() for record in self._fetchall("pragma table_info('%s')" % (table,))]

    def _get_tables(self):
        return [
            record['name'] for record in
            self._fetchall('SELECT name FROM sqlite_master WHERE type="table"')]

    def _rowcount(self, sql, args=[]):
        conn = self._connect()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, args)
            return cursor.rowcount
        finally:
            conn.close()

    def count(self, model, **kwargs):
        """
        Return the number of record matching the given model and criteria.
        """
        _validate_model(model)
        query = "SELECT COUNT(*) as count FROM " + model + _where(kwargs.keys())
        return self._fetchall(query, list(kwargs.values()))[0]['count']

    def delete(self, model, **kwargs):
        _validate_model(model)
        query = "DELETE FROM " + model + _where(kwargs.keys())
        return self._rowcount(query, list(kwargs.values()))

    def find(self, model, **kwargs):
        _validate_model(model)
        query = "SELECT * FROM " + model + _where(kwargs.keys())
        return self._fetchall(query, list(kwargs.values()))

    def findone(self, model, **kwargs):
        _validate_model(model)
        query = "SELECT * FROM " + model + _where(kwargs.keys()) + " LIMIT 1"
        record = self._fetchall(query, list(kwargs.values()))
        if record:
            return record[0]
        return None

    def insert(self, model, **kwargs):
        _validate_model(model)
        query = "INSERT INTO " + model + " (" + ','.join(kwargs.keys()) + ") values (" + ','.join('?' * len(kwargs)) + ")"
        return self._rowcount(query, args=list(kwargs.values()))

    def search(self, model, value, *in_fields):
        """
        Search the `value` in the `in_fields`.
        """
        _validate_model(model)
        value = '%' + value.replace('%', '').replace('_', '') + '%'
        # Build the query
        query = "SELECT * FROM " + model + " WHERE " + ' OR '.join(['%s LIKE ?' % x for x in in_fields])
        # Make a JOIN for repos model.
        if model == 'repos':
            query = "SELECT * FROM users, repos WHERE repos.UserID = users.UserID AND " + ' OR '.join(['%s LIKE ?' % x for x in in_fields])
        return self._fetchall(query, [value] * len(in_fields))

    def update(self, model, **kwargs):
        """
        Update a single object identified using the modelid.
        """
        _validate_model(model)
        # Get model identity
        keys = self._get_id(model, **kwargs)
        query = "UPDATE " + model + " SET " + ', '.join(['%s=?' % k for k in kwargs.keys() if k not in keys]) + _where(keys)
        return self._rowcount(query, [v for k, v in kwargs.items() if k not in keys] + [kwargs.get(k) for k in keys])
