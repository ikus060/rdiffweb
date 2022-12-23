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

import cherrypy
from sqlalchemy import Column, Index, Integer, Text

Base = cherrypy.tools.db.get_base()


class SshKey(Base):
    __tablename__ = 'sshkeys'
    __table_args__ = {'sqlite_autoincrement': True}
    fingerprint = Column('Fingerprint', Text)
    key = Column('Key', Text, unique=True, primary_key=True)
    userid = Column('UserID', Integer, nullable=False)


# Make finger print unique
sshkey_fingerprint_index = Index('sshkey_fingerprint_index', SshKey.fingerprint, unique=True)
