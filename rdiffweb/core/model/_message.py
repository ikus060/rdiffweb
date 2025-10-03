# udb, A web interface to manage IT network
# Copyright (C) 2022-2025 IKUS Software inc.
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

import cherrypy
from sqlalchemy import Boolean, Column, String, and_, event, inspect
from sqlalchemy.orm import backref, declared_attr, foreign, relationship, remote
from sqlalchemy.sql.functions import func
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import Integer

from rdiffweb.tools.i18n import gettext as _

from ._timestamp import Timestamp

Base = cherrypy.db.get_base()
Session = cherrypy.db.get_session()


def _get_model_changes(model, ignore=['messages']):
    """
    Return a dictionary containing changes made to the model since it was
    fetched from the database.

    The dictionary is of the form {'property_name': [old_value, new_value]}
    """
    state = inspect(model)
    changes = {}
    for attr in state.attrs:
        # Ignore `messages` field and other private field
        if attr.key == 'messages' or attr.key.startswith('_'):
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
    change_type = 'dirty' if state.has_identity else 'new'
    return change_type, changes


@event.listens_for(Session, "before_flush")
def create_messages(session, flush_context, instances):
    """
    When object get updated, add an audit message.
    """
    # Get current user
    author_id = None
    currentuser = getattr(cherrypy.serving.request, 'currentuser', None)
    if currentuser:
        author_id = currentuser.id
    # Create message if object is created or modified
    # Call "add_change" to let the object decide what should be updated.
    for obj in itertools.chain(session.new, session.dirty):
        if hasattr(obj, 'add_change'):
            # compute the list of changes base on sqlalchemy history
            change_type, changes = _get_model_changes(obj)
            if not changes:
                continue
            # Append the changes to a new message or a message in the current session flush.
            message = Message(author_id=author_id, changes=changes, type=change_type)
            obj.add_change(message)


class Message(Base):
    TYPE_COMMENT = 'comment'
    TYPE_NEW = 'new'
    TYPE_DIRTY = 'dirty'
    TYPE_PARENT = "parent"  # For parent changes

    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    model_name = Column(String, nullable=False)
    model_id = Column(Integer, nullable=False)
    author_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    author = relationship("UserObject", lazy=False)
    type = Column(String, nullable=False, default=TYPE_COMMENT)
    body = Column(String, nullable=False, default='')
    _changes = Column('changes', String, nullable=True)
    date = Column(Timestamp(timezone=True), default=func.now())
    sent = Column(Boolean, default=False)

    @property
    def changes(self):
        """
        Return Json changes stored in message.
        """
        return Message.json_changes(self._changes)

    @changes.setter
    def changes(self, value):
        try:
            self._changes = json.dumps(value, default=str)
        except Exception:
            self._changes = str(value)

    @classmethod
    def _search_string(cls):
        return cls.body + " " + cls._changes

    @property
    def model_object(self):
        """
        Return the model instance related to this message. All object supporting messages create a backref with <tablename>_model.
        """
        if self.model_name is None:
            return None
        return getattr(self, "%s_object" % self.model_name)

    def get_summary(self):
        """
        Provide a summary to be displayed in table.
        """
        model_object = getattr(self, "%s_object" % self.model_name, None)
        if model_object:
            return model_object.summary

    @property
    def author_name(self):
        if self.author is None:
            return _('System')
        return str(self.author)

    @classmethod
    def json_changes(cls, value):
        """
        Safely convert a string to Json data.
        """
        if not value or value[0] != '{':
            return None
        try:
            return json.loads(value)
        except Exception:
            return None


class MessageMixin:
    """
    Mixin to support messages.
    """

    def add_message(self, message):
        message.model_name = self.__tablename__
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
        return relationship(
            Message,
            primaryjoin=lambda: and_(
                cls.__tablename__ == remote(foreign(Message.model_name)), cls.id == remote(foreign(Message.model_id))
            ),
            order_by=Message.date,
            lazy=True,
            cascade="all, delete",
            overlaps="messages",
            backref=backref(
                '%s_object' % cls.__tablename__,
                lazy=True,
                overlaps="messages",
            ),
        )

    @declared_attr
    def comments(cls):
        return relationship(
            Message,
            primaryjoin=lambda: and_(
                cls.__tablename__ == remote(foreign(Message.model_name)),
                cls.id == remote(foreign(Message.model_id)),
                Message.type == Message.TYPE_COMMENT,
            ),
            order_by=Message.date,
            viewonly=True,
            lazy=True,
        )

    @declared_attr
    def changes(cls):
        return relationship(
            Message,
            primaryjoin=lambda: and_(
                cls.__tablename__ == remote(foreign(Message.model_name)),
                cls.id == remote(foreign(Message.model_id)),
                Message.type != Message.TYPE_COMMENT,
            ),
            order_by=Message.date,
            viewonly=True,
            lazy=True,
        )
