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
from sqlalchemy import Column, ForeignKey, Index, Integer, PrimaryKeyConstraint, Text, event, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import reconstructor, relationship, validates

from rdiffweb.core.authorizedkeys import AuthorizedKey, check_publickey
from rdiffweb.tools.i18n import gettext_lazy as _

from ._callbacks import add_post_commit_tasks
from ._update import index_exists

Base = cherrypy.db.get_base()
Session = cherrypy.db.get_session()

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
    _key = Column('Key', Text, unique=True, primary_key=True)
    userid = Column('UserID', Integer, ForeignKey("users.UserID"), nullable=False)
    user = relationship('UserObject', back_populates="authorizedkeys", lazy="joined")
    # Transient value.
    _authorizedkey = None

    @classmethod
    def from_authorizedkey(cls, data, comment=None):
        """
        Create a new SshKey from a given public ssh key and comment.
        """
        # Parse/validate the key
        authorizedkey = check_publickey(data)
        # Remove option & Remove comment for SQL storage
        authorizedkey = AuthorizedKey(
            options=None, keytype=authorizedkey.keytype, key=authorizedkey.key, comment=comment or authorizedkey.comment
        )
        return SshKey(_key=authorizedkey.getvalue())

    @reconstructor
    def __init_on_load__(self):
        """
        Called when object get constructed by ORM.

        This implementation initialize the comment field.
        """
        try:
            self._authorizedkey = check_publickey(self._key)
        except ValueError:
            # Ignore error.
            pass

    @validates('_key')
    def validate_key(self, _key, value):
        # Parse ssh key. Will raise error if invalid.
        self._authorizedkey = check_publickey(value)
        # Update fingerprint at the same time.
        self.fingerprint = self._authorizedkey.fingerprint
        return value

    @property
    def key(self):
        return self._authorizedkey.key

    @property
    def comment(self):
        return self._authorizedkey.comment

    @property
    def keytype(self):
        return self._authorizedkey.keytype

    def __str__(self):
        return self.fingerprint


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


@event.listens_for(Session, 'after_flush')
def sshkey_after_flush(session, flush_context):
    for sshkey in session.new:
        if isinstance(sshkey, SshKey):
            add_post_commit_tasks(session, 'authorizedkey_added', sshkey.user, sshkey.fingerprint, sshkey.comment)
