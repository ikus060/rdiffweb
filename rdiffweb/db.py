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

import rdw_config


class userDB:

    def getUserDBModule(self):
        # Return a different implementation according to UserDB configuration.
        prevDBType = rdw_config.get_config("UserDB")
        if prevDBType.lower().startswith("ldap"):
            import db_ldap
            import db_sqlite
            return db_ldap.ldapUserDB(db_sqlite.sqliteUserDB())
        elif prevDBType.lower() == "mysql":
            import db_mysql
            return db_mysql.mysqlUserDB()
        elif prevDBType.lower() == "file":
            import db_file
            return db_file.fileUserDB()
        elif prevDBType == "" or prevDBType.lower() == "sqlite":
            import db_sqlite
            return db_sqlite.sqliteUserDB()
        else:
            raise ValueError(
                "Invalid user database type. Re-configure rdiffweb.")
