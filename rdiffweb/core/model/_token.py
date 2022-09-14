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
import datetime

import cherrypy
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = cherrypy.tools.db.get_base()


class Token(Base):
    __tablename__ = 'tokens'
    name = Column('Name', String, nullable=False, default="", primary_key=True)
    userid = Column('UserID', Integer, nullable=False, primary_key=True)
    user = relationship(
        'UserObject',
        foreign_keys=[userid],
        primaryjoin='UserObject.userid == Token.userid',
        uselist=False,
        lazy=True,
    )
    hash_token = Column('Token', String, nullable=False, default="")
    access_time = Column('AccessTime', DateTime, nullable=True)
    creation_time = Column('CreationTime', DateTime, nullable=False, server_default=func.now())
    expiration_time = Column('ExpirationTime', DateTime, nullable=True)

    @property
    def is_expired(self):
        return self.expiration_time is not None and self.expiration_time <= datetime.datetime.now()
