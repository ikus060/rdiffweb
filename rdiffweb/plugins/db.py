# udb, A web interface to manage IT network
# Copyright (C) 2025 IKUS Software inc.
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
'''
SQLAlchemy Tool for CherryPy.
'''
import logging

import cherrypy
from cherrypy.process.plugins import SimplePlugin
from sqlalchemy import create_engine, event, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

logger = logging.getLogger(__name__)


@event.listens_for(Engine, 'connect')
def _set_sqlite_journal_mode_wal(connection, connection_record):
    """
    Enable WAL journaling for concurrent read and write operation.
    """
    if 'sqlite3' in str(connection.__class__):
        cursor = connection.cursor()
        cursor.execute('PRAGMA journal_mode=WAL;')
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()


def _get_model_changes(model):
    """
    Return a dictionary containing changes made to the model since it was
    fetched from the database.

    The dictionary is of the form {'property_name': [old_value, new_value]}
    """
    state = inspect(model)
    changes = {}
    for attr in state.attrs:
        hist = attr.history
        if not hist.has_changes():
            continue
        if isinstance(attr.value, (list, tuple)) or len(hist.deleted) > 1 or len(hist.added) > 1:
            # If array, store array
            changes[attr.key] = [hist.deleted, hist.added]
        else:
            # If primitive, store primitive
            changes[attr.key] = [
                hist.deleted[0] if len(hist.deleted) >= 1 else None,
                hist.added[0] if len(hist.added) >= 1 else None,
            ]
    return changes


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

    def add(self):
        """
        Add current object to session.
        """
        self.__class__.session.add(self)
        return self

    def delete(self):
        self.__class__.session.delete(self)
        return self

    def commit(self):
        self.__class__.session.commit()
        return self

    def flush(self):
        self.__class__.session.flush()
        return self

    def expire(self):
        self.__class__.session.expire(self)
        return self

    def rollback(self):
        self.__class__.session.rollback()
        return self


class SQLA(SimplePlugin):
    uri = None
    debug = False

    _base = None
    _session = None
    _engine = None

    def start(self):
        # Adjust debug level.
        if self.debug:
            logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
        # Create connection to database
        self._engine = create_engine(self.uri)
        # Clean-up previous session.
        self.clear_sessions()
        # Associate our session to our engine
        self.get_session().configure(bind=self._engine)
        self.bus.log("Database session plugin started.")

    def stop(self):
        if self._session:
            self.clear_sessions()
        if self._engine:
            self._engine.dispose()
        self.bus.log("Database session plugin stopped.")

    def create_all(self):
        try:
            # Create tables
            base = self.get_base()
            conn = self.get_session().connection()
            base.metadata.create_all(bind=conn)
            self.get_session().commit()
        finally:
            # Release opened sessions.
            self.clear_sessions()

    def drop_all(self):
        try:
            # Drop all
            base = self.get_base()
            base.metadata.drop_all(bind=self._engine)
            self.get_session().commit()
        finally:
            # Release opened sessions.
            self.clear_sessions()

    def get_base(self):
        """
        Return a singleton instance of the Base classe for ORM.
        """
        if self._base is None:
            self._base = declarative_base(cls=Base)
            # Provide a friendly ObjectName.query.
            self._base.session = self.get_session()
            self._base.query = self.get_session().query_property()
        return self._base

    def get_session(self):
        """
        Return a singleton database session.
        """
        if self._session is None:
            self._session_factory = sessionmaker(autoflush=False, autocommit=False)
            self._session = scoped_session(self._session_factory)
        return self._session

    def after_request(self):
        self.clear_sessions()

    def clear_sessions(self):
        """
        Used to clean-up session and raise error if session are not clean.
        """
        if self._session is None:
            return
        try:
            # When terminating, raise an error if objects are not commit.
            if self._session.dirty or self._session.new or self._session.deleted:
                changes = ', '.join([str(_get_model_changes(obj)) for obj in self._session.dirty])
                logger.exception(
                    'session is dirty, some database object(s) are not commited, this indicate a bug in the application '
                    'dirty %s new %s deleted %s' % (changes, self._session.new, self._session.deleted)
                )
                raise SQLAlchemyError('session is dirty')
        finally:
            self._session.rollback()
            self._session.expunge_all()
            self._session.remove()


cherrypy.db = SQLA(cherrypy.engine)
cherrypy.db.subscribe()

cherrypy.config.namespaces['db'] = lambda key, value: setattr(cherrypy.db, key, value)
