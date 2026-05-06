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

import itertools
import json
import logging

import cherrypy
import cherrypy_foundation.plugins.db  # noqa
from sqlalchemy import Column, String, Text, and_, event, inspect, text
from sqlalchemy.orm import Session, backref, declared_attr, foreign, relationship, remote
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer
from sqlalchemy.types import TypeDecorator

from ._timestamp import Timestamp
from ._update import column_add, column_exists, constraint_add, constraint_exists, is_sqlite

Base = cherrypy.db.base


AUDIT_IGNORE = 'audit_ignore'

logger = logging.getLogger(__name__)


class JSONString(TypeDecorator):
    """Stores JSON data as a string in the database."""

    impl = Text  # Use TEXT column type (or String if you prefer)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        """Convert Python object -> JSON string (when saving to DB)."""
        if value is None:
            return None
        # If already a string, keep-it as-is it's probably a LIKe pattern.
        if isinstance(value, str):
            return value
        return json.dumps(value, default=str)

    def process_result_value(self, value, dialect):
        """Convert JSON string -> Python object (when loading from DB)."""
        if value is None:
            return None
        try:
            return json.loads(value)
        except (TypeError, json.JSONDecodeError) as e:
            logger.warning("Failed to deserialize JSON string: %s. Error: %s", value, e)
            return None


def get_model_changes(model):
    """
    Return a dictionary containing changes made to the model since it was
    fetched from the database.

    The dictionary is of the form {'property_name': [old_value, new_value]}
    """
    state = inspect(model)
    changes = {}
    for attr in state.attrs:
        # Ignore `messages` field and other private field
        mapper = state.mapper
        if mapper.has_property(attr.key) and mapper.get_property(attr.key).info.get('audit_ignore', False):
            continue
        # Ignore attribute without history changes.
        hist = attr.load_history()
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
    if model in state.session.deleted:
        change_type = 'deleted'
    elif state.has_identity:
        change_type = 'dirty'
    else:
        change_type = 'new'
    return change_type, changes


@event.listens_for(Session, "before_flush")
def create_messages(session, flush_context, instances):
    """
    When object get updated, add an audit message.
    """
    # Get current user
    author_id = None
    # Create message if object is created or modified
    # Call "add_change" to let the object decide what should be updated.
    for obj in itertools.chain(session.new, session.dirty, session.deleted):
        if hasattr(obj, 'add_change'):
            # compute the list of changes base on sqlalchemy history
            change_type, changes = get_model_changes(obj)
            if change_type == 'dirty' and not changes:
                continue

            # Enrich event using current user, IP address and User-Agent
            request = cherrypy.serving.request
            currentuser = getattr(cherrypy.serving.request, 'currentuser', None)
            if currentuser:
                author_id = currentuser.id
            ip_address = request.remote.ip
            user_agent = request.headers.get('User-Agent', '')
            # Append the changes to a new message or a message in the current session flush.
            message = Message(
                author_id=author_id, changes=changes, type=change_type, ip_address=ip_address, user_agent=user_agent
            )
            obj.add_change(message)


class Message(Base):
    TYPE_COMMENT = 'comment'
    TYPE_EVENT = 'event'
    TYPE_NEW = 'new'
    TYPE_DIRTY = 'dirty'
    TYPE_DELETE = 'deleted'

    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    model_id = Column(Integer, nullable=False)
    model_summary = Column(String, nullable=False, default='', server_default='')
    author_id = Column(
        Integer, ForeignKey('users.UserID', name='fk_messages_author_id', ondelete="SET NULL"), nullable=True
    )
    author = relationship("UserObject", lazy=False)
    ip_address = Column(String, nullable=False, default='', server_default='')
    user_agent = Column(String, nullable=False, default='', server_default='')
    type = Column(String, nullable=False, default=TYPE_COMMENT, server_default=TYPE_COMMENT)
    body = Column(String, nullable=False, default='', server_default='')
    changes = Column('changes', JSONString, nullable=True)
    date = Column(Timestamp(timezone=True), default=func.now())

    @property
    def model_object(self):
        """
        Return the model instance related to this message. All object supporting messages create a backref with <tablename>_model.
        """
        if self.model_name is None:
            return None
        return getattr(self, "%s_object" % self.model_name)


class MessageMixin:
    """
    Mixin to support messages.
    """

    @classmethod
    def _get_message_model_name(cls):
        # Strip ending 's' from table name
        return cls.__tablename__[0:-1] if cls.__tablename__[-1] == 's' else cls.__tablename__

    def add_message(self, message):
        message.model_name = self._get_message_model_name()
        message.model_summary = str(self)
        self.messages.append(message)

    def add_change(self, new_message):
        """
        Append change to an existing message to be flushed or to a new message.
        """
        # Check if the last message is uncommit.
        if not (self.messages and self.messages[-1].id is None):
            self.add_message(new_message)
            return

        # Merge both messages
        message = self.messages[-1]
        message.type = new_message.type
        changes = message.changes
        if changes:
            for key, values in new_message.changes.items():
                if key not in changes:
                    changes[key] = values
                elif isinstance(changes[key][0], list) and isinstance(values[0], list):
                    # Combine both list
                    changes[key][0].extend(values[0])
                    changes[key][1].extend(values[1])
                    # And sort them to make it predictable.
                    changes[key][0].sort()
                    changes[key][1].sort()
                else:
                    # Replace the new value
                    changes[key][1] = values[0]
            message.changes = changes
        else:
            message.changes = new_message.changes
        message.add()

    @declared_attr
    def messages(cls):
        model_name = cls._get_message_model_name()
        return relationship(
            Message,
            primaryjoin=lambda: and_(
                model_name == remote(foreign(Message.model_name)), cls.id == remote(foreign(Message.model_id))
            ),
            order_by=Message.date,
            lazy=True,
            cascade="save-update",
            overlaps="messages,user_object,repo_object",
            backref=backref(
                '%s_object' % model_name,
                lazy=True,
                overlaps="messages,user_object,repo_object",
            ),
            info={AUDIT_IGNORE: True},
            passive_deletes="all",
        )

    @declared_attr
    def comments(cls):
        model_name = cls._get_message_model_name()
        return relationship(
            Message,
            primaryjoin=lambda: and_(
                model_name == remote(foreign(Message.model_name)),
                cls.id == remote(foreign(Message.model_id)),
                Message.type == Message.TYPE_COMMENT,
            ),
            order_by=Message.date,
            viewonly=True,
            lazy=True,
            info={AUDIT_IGNORE: True},
        )

    @declared_attr
    def changes(cls):
        model_name = cls._get_message_model_name()
        return relationship(
            Message,
            primaryjoin=lambda: and_(
                model_name == remote(foreign(Message.model_name)),
                cls.id == remote(foreign(Message.model_id)),
                Message.type.in_([Message.TYPE_NEW, Message.TYPE_DIRTY, Message.TYPE_DELETE]),
            ),
            order_by=Message.date,
            viewonly=True,
            lazy=True,
            info={AUDIT_IGNORE: True},
        )


@event.listens_for(Base.metadata, 'after_create', insert=True)
def update_message_schema(target, conn, **kw):
    if not column_exists(conn, Message.ip_address):
        column_add(conn, Message.ip_address)
    if not column_exists(conn, Message.user_agent):
        column_add(conn, Message.user_agent)

    # Since 2.11.4 - author_id  ondelete="SET NULL"
    fk_constraint = next(c for c in Message.__table__.foreign_key_constraints if c.name == 'fk_messages_author_id')
    if not constraint_exists(conn, fk_constraint):
        if not is_sqlite(conn):
            # With postgresql drop previous constraint.
            conn.execute(
                text("ALTER TABLE %s DROP CONSTRAINT IF EXISTS %s" % (Message.__tablename__, fk_constraint.name))
            )
        # Then add the constraint.
        constraint_add(conn, fk_constraint)
