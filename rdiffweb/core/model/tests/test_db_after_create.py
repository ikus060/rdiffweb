# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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
import os
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


@parameterized_class(
    [
        {"version": "1.5.0", "init_sql": SQL_1_5_0},
        {"version": "unknown", "init_sql": SQL_ROLE_WITHOUT_DEFAULT},
    ]
)
@skipIf(os.environ.get('RDIFFWEB_TEST_DATABASE_URI'), 'custom database')
class LoginAbstractTest(rdiffweb.test.WebCase):
    init_sql = ""

    def setUp(self):
        cherrypy.test.helper.CPWebCase.setUp(self)
        cherrypy.tools.db.drop_all()
        # Create custom database ONLY SQLITE here
        dbapi = cherrypy.tools.db.get_session().bind.raw_connection()
        if self.init_sql:
            try:
                dbapi.executescript(self.init_sql)
            finally:
                dbapi.close()
        # Upgrade database
        cherrypy.tools.db.create_all()

    def tearDown(self):
        super().tearDown()

    def test_sanity_check(self):
        # Get index page
        self.getPage('/')
        self.assertStatus(303)
        # Login
        self._login()
        # Get index page
        self.getPage('/')
        self.assertStatus(200)

    def test_get_user(self):
        # Given admin user
        admin = UserObject.get_user('admin')
        # No error when getting is_admin status.
        admin.is_admin
