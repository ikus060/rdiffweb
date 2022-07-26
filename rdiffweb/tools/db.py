# -*- coding: utf-8 -*-
# udb, A web interface to manage IT network
# Copyright (C) 2022 IKUS Software inc.
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
'''
SQLAlchemy Tool for CherryPy.
'''
import logging

import cherrypy
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

logger = logging.getLogger(__name__)


@event.listens_for(Engine, 'connect')
def _set_sqlite_journal_mode_wal(connection, connection_record):
    """
    Enable WAL journaling for concurrent read and write operation.
    """
    if 'sqlite3' in str(connection.__class__):
        cursor = connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        cursor.close()


class Base:
    '''
    Extends declarative base to provide convenience methods to models similar to
    functionality found in Elixir. Works in python3.

    For example, given the model User:
    # no need to write init methods for models, simply pass keyword arguments or
    # override if needed.
    User(name="daniel", email="daniel@dasa.cc").add()
    User.query # returns session.query(User)
    User.query.all() # instead of session.query(User).all()
    changed = User.from_dict({}) # update record based on dict argument passed in and returns any keys changed
    '''

    def add(self, commit=True):
        """
        Add current object to session.
        """
        self.__class__.session.add(self)
        if commit:
            self.__class__.session.commit()
        return self

    def delete(self, commit=True):
        """
        Delete current object to session.
        """
        self.__class__.session.delete(self)
        if commit:
            self.__class__.session.commit()
        return self

    def merge(self, commit=True):
        """
        Merge current object to session.
        """
        self.__class__.session.merge(self)
        if commit:
            self.__class__.session.commit()
        return self

    def expire(self):
        self.__class__.session.expire(self)


class BaseExtensions(DeclarativeMeta):
    @property
    def query(self):
        return self.session.query(self)

    @property
    def session(self):
        return cherrypy.tools.db.get_session()


class SQLA(cherrypy.Tool):
    _name = 'sqla'
    _base = None
    _session = None

    def __init__(self, **kw):
        cherrypy.Tool.__init__(self, None, None, priority=20)

    def _setup(self):
        cherrypy.request.hooks.attach('on_end_resource', self.on_end_resource)

    def create_all(self):
        # Release opened sessions.
        self.on_end_resource()
        # Create new metadata binding
        base = self.get_base()
        if base.metadata.bind is None:
            dburi = cherrypy.config.get('tools.db.uri')
            debug = cherrypy.config.get('tools.db.debug')
            base.metadata.bind = create_engine(dburi)
            if debug:
                logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
        base.metadata.create_all()

    def drop_all(self):
        # Release opened sessions.
        self.on_end_resource()
        # Drop all
        base = self.get_base()
        base.metadata.drop_all()

    def get_base(self):
        if self._base is None:
            self._base = declarative_base(metaclass=BaseExtensions, cls=Base)
        return self._base

    def get_session(self):
        if self._session is None:
            self._session = scoped_session(sessionmaker(autoflush=False, autocommit=False))
            self._session.bind = self.get_base().metadata.bind
        return self._session

    def on_end_resource(self):
        if self._session is None:
            return
        try:
            self._session.flush()
            self._session.commit()
        except Exception:
            logger.exception('error trying to flush and commit session')
            self._session.rollback()
            self._session.expunge_all()
        finally:
            self._session.remove()


cherrypy.tools.db = SQLA()
