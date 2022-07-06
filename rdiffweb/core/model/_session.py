# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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

import threading

try:
    import cPickle as pickle
except ImportError:
    import pickle

import logging

import cherrypy
from cherrypy.lib.sessions import Session
from sqlalchemy import Column, DateTime, LargeBinary, String

Base = cherrypy.tools.db.get_base()

logger = logging.getLogger(__name__)

SESSION_KEY = '_cp_username'


class SessionObject(Base):
    __tablename__ = 'sessions'
    __table_args__ = {'sqlite_autoincrement': True}
    id = Column('SessionID', String, unique=True, primary_key=True)
    username = Column('Username', String)
    data = Column('Data', LargeBinary)
    expiration_time = Column('ExpirationTime', DateTime)


class DbSession(Session):
    @classmethod
    def setup(cls, session_key=SESSION_KEY):
        """
        Set up the storage system for SQLAlchemy backend.
        Called once when the built-in tool calls sessions.init.
        """
        cls._session_key = session_key

    def _exists(self):
        return SessionObject.query.filter(SessionObject.id == self.id).first() is not None

    def _load(self):
        session = SessionObject.query.filter(SessionObject.id == self.id).first()
        if not session:
            return None
        try:
            return (pickle.loads(session.data), session.expiration_time)
        except TypeError:
            logger.error('fail to read session data', exc_info=1)
        return None

    def _save(self, expiration_time):
        session = SessionObject.query.filter(SessionObject.id == self.id).first()
        if not session:
            session = SessionObject(id=self.id)
        session.expiration_time = expiration_time
        session.username = self._data.get(self._session_key)
        session.data = pickle.dumps(self._data, pickle.HIGHEST_PROTOCOL)
        session.add()

    def _delete(self):
        SessionObject.query.filter(SessionObject.id == self.id).delete()

    def clean_up(self):
        """Clean up expired sessions."""
        now = self.now()
        with SessionObject.session.begin():
            SessionObject.query.filter(SessionObject.expiration_time < now).delete()

    def __len__(self):
        """Return the number of active sessions."""
        return SessionObject.query.count()

    # http://docs.cherrypy.org/dev/refman/lib/sessions.html?highlight=session#locking-sessions
    # session id locks as done in RamSession

    locks = {}

    def acquire_lock(self):
        """Acquire an exclusive lock on the currently-loaded session data."""
        self.locked = True
        self.locks.setdefault(self.id, threading.RLock()).acquire()

    def release_lock(self):
        """Release the lock on the currently-loaded session data."""
        self.locks[self.id].release()
        self.locked = False
