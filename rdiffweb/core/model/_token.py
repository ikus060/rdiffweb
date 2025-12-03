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
import datetime

import cherrypy
from cherrypy.process.plugins import SimplePlugin
from sqlalchemy import Column, ForeignKey, Integer, String, event
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ._callbacks import add_post_commit_tasks
from ._timestamp import Timestamp
from ._update import column_add, column_exists

Base = cherrypy.db.get_base()
Session = cherrypy.db.get_session()


class Token(Base):
    __tablename__ = 'tokens'
    name = Column('Name', String, nullable=False, default="", primary_key=True)
    userid = Column('UserID', Integer, nullable=False, primary_key=True)
    userid = Column('UserID', Integer, ForeignKey("users.UserID"), nullable=False)
    user = relationship('UserObject', back_populates="tokens", lazy="joined")
    hash_token = Column('Token', String, nullable=False, default="")
    access_time = Column('AccessTime', Timestamp, nullable=True)
    creation_time = Column('CreationTime', Timestamp, nullable=False, server_default=func.now())
    expiration_time = Column('ExpirationTime', Timestamp, nullable=True)
    _scope = Column('Scope', String, nullable=False, server_default="")

    @property
    def is_expired(self):
        return self.expiration_time is not None and self.expiration_time <= datetime.datetime.now(
            tz=datetime.timezone.utc
        )

    def accessed(self):
        self.access_time = datetime.datetime.now(tz=datetime.timezone.utc)

    @property
    def scope(self):
        if self._scope:
            return self._scope.split(',')
        return []

    @scope.setter
    def scope(self, value):
        if isinstance(value, (tuple, list)):
            value = ','.join(value)
        self._scope = value

    def __str__(self):
        return self.name


class TokenCleanup(SimplePlugin):
    execution_time = '23:00'

    def start(self):
        self.bus.log('Start Token Clean Up plugin')
        self.bus.publish(
            'scheduler:add_job_daily', self.execution_time, f'{self.__module__}:cherrypy.token_cleanup.clean_up'
        )

    def stop(self):
        self.bus.log('Stop Token Clean Up plugin')
        self.bus.publish('scheduler:remove_job', f'{self.__module__}:cherrypy.token_cleanup.clean_up')

    def graceful(self):
        """Reload of subscribers."""
        self.stop()
        self.start()

    def clean_up(self):
        Token.query.filter(Token.expiration_time <= datetime.datetime.now(tz=datetime.timezone.utc)).delete()
        Token.session.commit()


cherrypy.token_cleanup = TokenCleanup(cherrypy.engine)
cherrypy.token_cleanup.subscribe()

cherrypy.config.namespaces['token_cleanup'] = lambda key, value: setattr(cherrypy.token_cleanup, key, value)


@event.listens_for(Base.metadata, 'after_create')
def update_token_schema(target, conn, **kw):
    # Add Token.scope column - since v2.9.0 with value of All for backward compatibility
    if not column_exists(conn, Token._scope):
        column_add(conn, Token._scope)
        Token.query.update({Token._scope: 'all'})


@event.listens_for(Session, 'after_flush')
def token_after_flush(session, flush_context):
    for token in session.new:
        if isinstance(token, Token):
            add_post_commit_tasks(session, 'access_token_added', token.user, token.name)
