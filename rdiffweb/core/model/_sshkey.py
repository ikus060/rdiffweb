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
import sys

import cherrypy
from sqlalchemy import Column, Index, Integer, PrimaryKeyConstraint, Text, event, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship

from rdiffweb.tools.i18n import gettext_lazy as _

from ._message import Message
from ._update import index_exists

Base = cherrypy.db.get_base()

logger = logging.getLogger(__name__)


class SshKey(Base):
    __tablename__ = 'sshkeys'
    __table_args__ = (
        PrimaryKeyConstraint(
            'Key',
            name='sshkeys_pkey',
            info={'error_message': _("Duplicate key. This key already exists or is associated to another user.")},
        ),
        {'sqlite_autoincrement': True},
    )
    fingerprint = Column('Fingerprint', Text)
    key = Column('Key', Text, unique=True, primary_key=True)
    userid = Column('UserID', Integer, nullable=False)
    user = relationship(
        'UserObject',
        foreign_keys=[userid],
        primaryjoin='UserObject.id == SshKey.userid',
        uselist=False,
        lazy=True,
    )

    def add_change(self, new_message):
        """
        Specific implementation to propagate changes to parent user.
        """
        # Update message to be added to the parent user.
        if new_message.type == Message.TYPE_NEW and self.user:
            new_message.type = Message.TYPE_DIRTY
            new_message.changes = {'authorizedkeys': [[], [[self.fingerprint]]]}
            self.user.add_change(new_message)
        elif new_message.type == Message.TYPE_DELETE and self.user:
            new_message.type = Message.TYPE_DIRTY
            new_message.changes = {'authorizedkeys': [[[self.fingerprint]], []]}
            self.user.add_change(new_message)


# Make finger print unique
sshkey_fingerprint_index = Index(
    'sshkey_fingerprint_index',
    SshKey.fingerprint,
    unique=True,
    info={'error_message': _("Duplicate key. This key already exists or is associated to another user.")},
)


@event.listens_for(Base.metadata, 'after_create')
def update_sshkeys_schema(target, conn, **kw):

    # Fix SSH Key uniqueness - since 2.5.4
    if not index_exists(conn, 'sshkey_fingerprint_index'):
        duplicate_sshkeys = (
            SshKey.query.with_entities(SshKey.fingerprint)
            .group_by(SshKey.fingerprint)
            .having(func.count(SshKey.fingerprint) > 1)
        ).all()
        try:
            sshkey_fingerprint_index.create(bind=conn)
        except IntegrityError:
            msg = (
                'Failure to upgrade your database to make SSH Keys unique. '
                'You must downgrade and deleted duplicate SSH Keys. '
                '%s' % '\n'.join([str(k) for k in duplicate_sshkeys]),
            )
            logger.error(msg)
            print(msg, file=sys.stderr)
            raise SystemExit(12)
