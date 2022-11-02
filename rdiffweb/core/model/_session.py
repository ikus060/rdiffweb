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

import logging
import threading

import cherrypy
from cherrypy.lib.sessions import Session
from sqlalchemy import Column, DateTime, Integer, PickleType, String
from sqlalchemy.orm import validates

SESSION_KEY = '_cp_username'

Base = cherrypy.tools.db.get_base()

logger = logging.getLogger(__name__)


class SessionObject(Base):
    __tablename__ = 'sessions'
    __table_args__ = {'sqlite_autoincrement': True}
    number = Column('Number', Integer, unique=True, primary_key=True)
    id = Column('SessionID', String, unique=True, nullable=False)
    username = Column('Username', String)
    data = Column('Data', PickleType)
    expiration_time = Column('ExpirationTime', DateTime, nullable=False)
    access_time = Column('AccessTime', DateTime)

    @validates('data')
    def validate_data(self, key, value):
        # Extract specific fields from data into column to speed up SQL query.
        if value:
            self.access_time = value.get('access_time')
            self.username = value.get(SESSION_KEY)
        return value


class DbSession(Session):
    def _exists(self):
        return SessionObject.query.filter(SessionObject.id == self.id).first() is not None

    def _load(self):
        session = SessionObject.query.filter(SessionObject.id == self.id).first()
        if not session:
            return None
        try:
            self.timeout = session.data.pop('_timeout', self.timeout)
            return (session.data, session.expiration_time)
        except TypeError:
            logger.error('fail to read session data', exc_info=1)
        return None

    def _save(self, expiration_time):
        session = SessionObject.query.filter(SessionObject.id == self.id).first()
        if not session:
            session = SessionObject(id=self.id)
        session.data = self._data
        session.data['_timeout'] = self.timeout
        session.expiration_time = expiration_time
        session.add().commit()

    def _delete(self):
        SessionObject.query.filter(SessionObject.id == self.id).delete()
        SessionObject.session.commit()

    def clean_up(self):
        """Clean up expired sessions."""
        try:
            now = self.now()
            SessionObject.query.filter(SessionObject.expiration_time < now).delete()
            SessionObject.session.commit()
        except Exception:
            logger.error('fail to clean-up sessions', exc_info=1)
        finally:
            cherrypy.tools.db.on_end_resource()

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
