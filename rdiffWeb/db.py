#!/usr/bin/python

import rdw_config

class userDB:
   def getUserDBModule(self):
      import db_sqlite
      return db_sqlite.sqliteUserDB(rdw_config.getDatabasePath())

