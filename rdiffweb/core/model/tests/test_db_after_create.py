# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import os
import tempfile
from unittest import skipIf

import cherrypy
from parameterized import parameterized_class

import rdiffweb.test
from rdiffweb.core.model import UserObject

SQL_1_5_0 = """
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
UserID integer primary key autoincrement,
Username varchar (50) unique NOT NULL,
Password varchar (40) NOT NULL DEFAULT "",
UserRoot varchar (255) NOT NULL DEFAULT "",
IsAdmin tinyint NOT NULL DEFAULT FALSE,
UserEmail varchar (255) NOT NULL DEFAULT "",
RestoreFormat tinyint NOT NULL DEFAULT TRUE, role tinyint NOT NULL DEFAULT "10");
INSERT INTO users VALUES(1,'admin','{SSHA}SM8K9ZSzc90hCPwy7pz3phkEE+jUqYO2','',0,'',1,0);
CREATE TABLE repos (
RepoID integer primary key autoincrement,
UserID int(11) NOT NULL,
RepoPath varchar (255) NOT NULL,
MaxAge tinyint NOT NULL DEFAULT 0,
Encoding varchar (50), keepdays varchar(255) NOT NULL DEFAULT "");
CREATE TABLE sshkeys (
Fingerprint primary key,
Key clob UNIQUE,
UserID int(11) NOT NULL);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',1);
COMMIT;
"""

SQL_ROLE_WITHOUT_DEFAULT = """
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
UserID integer primary key autoincrement,
Username varchar (50) unique NOT NULL,
Password varchar (40) NOT NULL DEFAULT "",
UserRoot varchar (255) NOT NULL DEFAULT "",
IsAdmin tinyint NOT NULL DEFAULT FALSE,
UserEmail varchar (255) NOT NULL DEFAULT "",
RestoreFormat tinyint NOT NULL DEFAULT TRUE, fullname VARCHAR, role SMALLINT);
INSERT INTO users VALUES(1,'admin','{SSHA}eFF2vTUKbfA4qGyQlscj3Z8dtdR4Uilt','/home/root-mail',0,'',1,NULL,NULL);
CREATE TABLE repos (
RepoID integer primary key autoincrement,
UserID int(11) NOT NULL,
RepoPath varchar (255) NOT NULL,
MaxAge tinyint NOT NULL DEFAULT 0, Encoding VARCHAR, keepdays VARCHAR);
INSERT INTO repos VALUES(1,1,'test',1,NULL,NULL);
INSERT INTO repos VALUES(2,1,'desktop',0,NULL,NULL);
CREATE TABLE sshkeys (
    "Fingerprint" TEXT,
    "Key" TEXT,
    "UserID" INTEGER NOT NULL,
    UNIQUE ("Key")
);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',2);
INSERT INTO sqlite_sequence VALUES('repos',3);
COMMIT;
"""

SQL_WITH_DUPLICATE_USERS = """
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
UserID integer primary key autoincrement,
Username varchar (50) unique NOT NULL,
Password varchar (40) NOT NULL DEFAULT "",
UserRoot varchar (255) NOT NULL DEFAULT "",
IsAdmin tinyint NOT NULL DEFAULT FALSE,
UserEmail varchar (255) NOT NULL DEFAULT "",
RestoreFormat tinyint NOT NULL DEFAULT TRUE, fullname VARCHAR, role SMALLINT);
INSERT INTO users VALUES(1,'admin','{SSHA}eFF2vTUKbfA4qGyQlscj3Z8dtdR4Uilt','/home/root-mail',0,'',1,NULL,NULL);
INSERT INTO users VALUES(2,'Patrik','{SSHA}eFF2vTUKbfA4qGyQlscj3Z8dtdR4Uilt','/home/Patrik',0,'',1,NULL,NULL);
INSERT INTO users VALUES(3,'patrik','{SSHA}eFF2vTUKbfA4qGyQlscj3Z8dtdR4Uilt','/home/patrik',0,'',1,NULL,NULL);
CREATE TABLE repos (
RepoID integer primary key autoincrement,
UserID int(11) NOT NULL,
RepoPath varchar (255) NOT NULL,
MaxAge tinyint NOT NULL DEFAULT 0, Encoding VARCHAR, keepdays VARCHAR);
INSERT INTO repos VALUES(1,1,'test',1,NULL,NULL);
INSERT INTO repos VALUES(2,1,'desktop',0,NULL,NULL);
CREATE TABLE sshkeys (
    "Fingerprint" TEXT,
    "Key" TEXT,
    "UserID" INTEGER NOT NULL,
    UNIQUE ("Key")
);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',2);
INSERT INTO sqlite_sequence VALUES('repos',3);
COMMIT;
"""

SQL_WITH_INVALID_USERNAMES = """
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
UserID integer primary key autoincrement,
Username varchar (50) unique NOT NULL,
Password varchar (40) NOT NULL DEFAULT "",
UserRoot varchar (255) NOT NULL DEFAULT "",
IsAdmin tinyint NOT NULL DEFAULT FALSE,
UserEmail varchar (255) NOT NULL DEFAULT "",
RestoreFormat tinyint NOT NULL DEFAULT TRUE, fullname VARCHAR, role SMALLINT);
INSERT INTO users VALUES(1,'admin','{SSHA}eFF2vTUKbfA4qGyQlscj3Z8dtdR4Uilt','/home/root-mail',0,'',1,NULL,NULL);
INSERT INTO users VALUES(2,'1user','{SSHA}eFF2vTUKbfA4qGyQlscj3Z8dtdR4Uilt','/home/Patrik',0,'',1,NULL,NULL);
CREATE TABLE repos (
RepoID integer primary key autoincrement,
UserID int(11) NOT NULL,
RepoPath varchar (255) NOT NULL,
MaxAge tinyint NOT NULL DEFAULT 0, Encoding VARCHAR, keepdays VARCHAR);
INSERT INTO repos VALUES(1,1,'test',1,NULL,NULL);
INSERT INTO repos VALUES(2,1,'desktop',0,NULL,NULL);
CREATE TABLE sshkeys (
    "Fingerprint" TEXT,
    "Key" TEXT,
    "UserID" INTEGER NOT NULL,
    UNIQUE ("Key")
);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',3);
INSERT INTO sqlite_sequence VALUES('repos',3);
COMMIT;
"""

# Some database have been created with null values
# Recent database enforce NOT NULL constraints.
SQL_WITH_NULL_FIELDS = """
PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE users (
UserID integer primary key autoincrement,
Username varchar (50) unique NOT NULL,
Password varchar (40) NOT NULL DEFAULT "",
UserRoot varchar (255) NOT NULL DEFAULT "",
IsAdmin tinyint NOT NULL DEFAULT FALSE,
UserEmail varchar (255) NOT NULL DEFAULT "",
RestoreFormat tinyint NOT NULL DEFAULT TRUE, role tinyint NOT NULL DEFAULT "10", fullname VARCHAR, mfa SMALLINT, lang VARCHAR, report_time_range SMALLINT, report_last_sent DATETIME);
INSERT INTO "main"."users" ("UserID", "Username", "Password", "UserRoot", "IsAdmin", "UserEmail", "RestoreFormat", "role", "fullname", "mfa", "lang", "report_time_range", "report_last_sent") VALUES ('1', 'admin', '{SSHA}eFF2vTUKbfA4qGyQlscj3Z8dtdR4Uilt', '/backups/admin', '0', 'info@ikus-soft.com', 'TRUE', '10', NULL, NULL, NULL, NULL, NULL);
CREATE TABLE repos (
RepoID integer primary key autoincrement,
UserID int(11) NOT NULL,
RepoPath varchar (255) NOT NULL,
MaxAge tinyint NOT NULL DEFAULT 0, Encoding VARCHAR, keepdays VARCHAR);
INSERT INTO repos VALUES(1,1,'test',1,NULL,NULL);
INSERT INTO repos VALUES(2,1,'desktop',0,NULL,NULL);
CREATE TABLE sshkeys (
    "Fingerprint" TEXT,
    "Key" TEXT,
    "UserID" INTEGER NOT NULL,
    UNIQUE ("Key")
);
DELETE FROM sqlite_sequence;
INSERT INTO sqlite_sequence VALUES('users',3);
INSERT INTO sqlite_sequence VALUES('repos',3);
COMMIT;
"""


@parameterized_class(
    [
        {"name": "from_1.5.0", "init_sql": SQL_1_5_0, "success": True},
        {"name": "unknown", "init_sql": SQL_ROLE_WITHOUT_DEFAULT, "success": True},
        {"name": "with_duplicate_users", "init_sql": SQL_WITH_DUPLICATE_USERS, "success": False},
        {"name": "with_invalid_usernames", "init_sql": SQL_WITH_INVALID_USERNAMES, "success": False},
        {"name": "with_null_fields", "init_sql": SQL_WITH_NULL_FIELDS, "success": True},
    ]
)
@skipIf(os.environ.get('RDIFFWEB_TEST_DATABASE_URI'), 'custom database')
class DbUpdateSchemaTest(rdiffweb.test.WebCase):
    init_sql = ""
    success = True

    @classmethod
    def setup_class(cls):
        # Delete database file
        db_file = tempfile.gettempdir() + '/test_rdiffweb_data.db'
        if os.path.exists(db_file):
            os.remove(db_file)
        super().setup_class()

    @classmethod
    def teardown_class(cls):
        super().teardown_class()
        # Delete database file
        db_file = tempfile.gettempdir() + '/test_rdiffweb_data.db'
        if os.path.exists(db_file):
            os.remove(db_file)

    def test_update_schema(self):
        assert self.init_sql

        # Given a older database Schema.
        cherrypy.db.drop_all()
        # Make sure the tables are deleted
        dbapi = cherrypy.db.get_session().bind.raw_connection()
        cursor = dbapi.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        self.assertEqual(['sqlite_sequence'], [table[0] for table in tables])
        try:
            dbapi.executescript(self.init_sql)
        finally:
            dbapi.close()

        # When updating existing schema
        if self.success:
            cherrypy.db.create_all()
            # Then index page is working
            self.getPage('/')
            self.assertStatus(303)
            # Then login is working
            self._login()
            # Then location is working
            self.getPage('/')
            self.assertStatus(200)
            # Then admin user is working
            admin = UserObject.get_user('admin')
            # No error when getting is_admin status.
            admin.is_admin
        else:
            # Then an error is raised
            with self.assertRaises(SystemExit):
                cherrypy.db.create_all()
