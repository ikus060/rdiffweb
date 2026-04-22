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

import logging

import cherrypy
from cherrypy_foundation.db_sessions import SessionModel  # noqa
from sqlalchemy import Column, Integer, String, event

from ._timestamp import Timestamp
from ._update import column_exists

Base = cherrypy.db.base

logger = logging.getLogger(__name__)


class SessionObject(SessionModel, Base):
    SESSION_USER_KEY = '_cp_username'
    __tablename__ = 'sessions'
    __table_args__ = {"extend_existing": True, 'sqlite_autoincrement': True}

    # Define number field for display
    number = Column('Number', Integer, unique=True, primary_key=True, autoincrement=True)
    # Red-define the column to remove primary_key
    session_id = Column('SessionID', String(255), unique=True, nullable=False, index=True)
    # Extend session table by definning additional columns
    username = Column('Username', String)
    access_time = Column('AccessTime', Timestamp)

    def __repr__(self):
        return f'SessionObject(number={self.number}, session_id={self.session_id}, username={self.username})'


@event.listens_for(SessionObject.data, 'set')
def validate_data(target, value, oldvalue, initiator):
    # Extract specific fields from data into column to speed up SQL query.
    if value:
        target.access_time = value.get('access_time')
        target.username = value.get(SessionObject.SESSION_USER_KEY)
    return value


@event.listens_for(Base.metadata, 'after_create')
def update_session_schema(target, conn, **kw):
    # Re-create session table if `login` column is missing
    if not column_exists(conn, SessionObject.username):
        SessionObject.__table__.drop(bind=conn)
        SessionObject.__table__.create(bind=conn)
