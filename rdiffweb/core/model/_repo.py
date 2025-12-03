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

import codecs
import encodings
import logging
import os
import sys
from datetime import timedelta

import cherrypy
from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, String
from sqlalchemy import __version__ as sqlalchemy_version
from sqlalchemy import and_, case, event, orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

import rdiffweb.plugins.db  # noqa
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError, RdiffRepo, RdiffTime
from rdiffweb.plugins.scheduler import clear_db_sessions
from rdiffweb.tools.i18n import ugettext as _

from ._callbacks import add_post_commit_tasks
from ._message import AUDIT_IGNORE, MessageMixin
from ._update import column_add, column_exists

Base = cherrypy.db.get_base()
Session = cherrypy.db.get_session()

logger = logging.getLogger(__name__)


def case_wrapper(*whens, else_=None):
    """
    Wrapper to support SQLAlchemy v1.2 to v2.0
    """
    if sqlalchemy_version.startswith('1.'):
        return case(list(whens), else_=else_)
    return case(*whens, else_=else_)


@clear_db_sessions
def delete_repo_path(repoid, path):
    """Job used to delete a repository path."""
    repoobj = RepoObject.query.filter(RepoObject.id == repoid).one()
    # Make sure to log this even when deleting a specific path.
    # Deletion of repository will be log by database.
    cherrypy.engine.publish('delete_path', repoobj, path)
    # Delete data on disk.
    repoobj.delete_path(path)
    repoobj.commit()


@clear_db_sessions
def delete_repo(repoid):
    """Job used to delete a repository."""
    repoobj = RepoObject.query.filter(RepoObject.id == repoid).one()
    # Delete data on disk.
    repoobj.delete_repo()
    repoobj.commit()


def _split_path(path):
    """
    Split the given path into <username as str> / <path as bytes>
    """
    # First part is the username
    assert path
    if isinstance(path, str):
        path = os.fsencode(path)
    path = path.strip(b'/')
    if b'/' in path:
        username, path = path.split(b'/', 1)
        return username.decode('utf-8'), path
    else:
        return path.decode('utf-8'), b''


class RepoObject(MessageMixin, Base, RdiffRepo):
    DEFAULT_REPO_ENCODING = codecs.lookup((sys.getfilesystemencoding() or 'utf-8').lower()).name

    STATUS_DELETING = 'deleting'  # Mark for deletion.

    __tablename__ = 'repos'
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column('RepoID', Integer, primary_key=True, autoincrement=True)
    userid = Column('UserID', Integer, ForeignKey("users.UserID"), nullable=False)
    user = relationship('UserObject', back_populates="repo_objs", lazy="joined")
    repopath = Column('RepoPath', String, nullable=False, default='')
    maxage = Column('MaxAge', SmallInteger, nullable=False, server_default="0")
    _encoding_name = Column('Encoding', String, default='')
    _keepdays = Column('keepdays', String, nullable=False, default="-1", info={'foo': 'bar'})
    _ignore_weekday = Column('IgnoreWeekday', Integer, nullable=False, server_default="0")
    notes = Column('notes', String, nullable=False, default='', server_default='')
    _status = Column('status', String, nullable=False, default='', server_default='', info={AUDIT_IGNORE: True})

    @classmethod
    def get_repo(cls, name, as_user=None, refresh=False):
        """
        Return the repository identified as `name`.
        `name` should be <username>/<repopath>
        """
        from ._user import UserObject

        username, repopath = _split_path(name)
        repopath = os.fsdecode(repopath).strip('/')

        # Check permissions
        as_user = getattr(cherrypy.serving.request, 'currentuser', as_user)
        if not as_user:
            raise AccessDeniedError("as_user or current user must be defined")
        if username != as_user.username and not as_user.is_admin:
            raise AccessDeniedError(name)

        # Search the repo in database
        query = RepoObject.query.join(UserObject, UserObject.id == RepoObject.userid).filter(
            and_(UserObject.username == username, RepoObject.repopath == repopath)
        )
        record = query.first()
        # If the repo is not found but refresh is requested
        if refresh and not record:
            if as_user.refresh_repos():
                as_user.commit()
            record = query.first()
        # If repo is not found, raise an error
        if not record:
            raise DoesNotExistError(username, repopath)
        return record

    @classmethod
    def get_repo_path(cls, path, as_user=None, refresh=False):
        """
        Return a the repository identified by the given `path`.
        `path` should be <username>/<repopath>/<subdir>
        """
        assert isinstance(path, bytes) or isinstance(path, str)
        sep = b'/' if isinstance(path, bytes) else '/'
        path = path.strip(sep) + sep

        # Since we don't know which part of the "path" is the repopath,
        # we need to do multiple search.
        try:
            startpos = 0
            while True:
                pos = path.index(sep, startpos)
                try:
                    # Run refresh only on first run.
                    repo_obj = cls.get_repo(path[:pos], as_user, refresh=refresh and startpos == 0)
                    break
                except DoesNotExistError:
                    # Raised when repo doesn't exists
                    startpos = pos + 1
            return repo_obj, path[pos + 1 : -1]
        except ValueError:
            raise DoesNotExistError(path)

    def __init__(self, *args, **kwargs):
        Base.__init__(self, *args, **kwargs)
        self.__init_on_load__()

    @orm.reconstructor
    def __init_on_load__(self):
        # RdiffRepo required an absolute full path, When the user_root is invalid, let generate an invalid full path.
        if not self.user.user_root:
            full_path = os.path.join('/user_has_an_empty_user_root/', self.repopath.strip('/'))
        elif not os.path.isabs(self.user.user_root):
            full_path = os.path.join('/user_has_a_relative_user_root/', self.repopath.strip('/'))
        else:
            full_path = os.path.join(self.user.user_root, self.repopath.strip('/'))
        RdiffRepo.__init__(self, full_path, encoding=self.encoding or RepoObject.DEFAULT_REPO_ENCODING)

    @property
    def name(self):
        # Repository name is the "repopath"
        return self.repopath

    @property
    def display_name(self):
        # String representation of repopath
        return self.repopath.strip('/')

    @property
    def owner(self):
        return self.user.username

    @hybrid_property
    def keepdays(self):
        try:
            return int(self._keepdays) if self._keepdays else -1
        except ValueError:
            return -1

    @keepdays.expression
    def keepdays(cls):
        return case_wrapper(
            (and_(cls._keepdays != None, cls._keepdays != ''), cls._keepdays.cast(Integer)),  # noqa
            else_=-1,
        )

    @keepdays.setter
    def keepdays(self, value):
        if value is None:
            self._keepdays = None
        else:
            self._keepdays = str(value)

    @hybrid_property
    def encoding(self):
        return (
            self._encoding_name
            if self._encoding_name is not None and self._encoding_name != ''
            else RepoObject.DEFAULT_REPO_ENCODING
        )

    @encoding.expression
    def encoding(cls):
        return case_wrapper(
            (and_(cls._encoding_name != None, cls._encoding_name != ''), cls._encoding_name),  # noqa
            else_=RepoObject.DEFAULT_REPO_ENCODING,
        )

    @encoding.setter
    def encoding(self, value):
        if value is None:
            raise ValueError(_('invalid encoding %s') % value)
        codec = encodings.search_function(value.lower())
        if not codec:
            raise ValueError(_('invalid encoding %s') % value)
        self._encoding_name = codec.name

    def schedule_delete_path(self, path):
        """Schedule deletion of the repository"""
        cherrypy.engine.publish('scheduler:add_job_now', delete_repo_path, self.id, path)

    def schedule_delete_repo(self):
        """
        Mark this repo for deletion.
        """
        self._status = RepoObject.STATUS_DELETING
        add_post_commit_tasks(Session, 'scheduler:add_job_now', delete_repo, self.id)

    def delete_repo(self):
        # Delete repo on disk
        RdiffRepo.delete_repo(self)
        # Delete repo from database
        return super().delete()

    @validates('maxage')
    def validate_maxage(self, key, value):
        int(value)
        return value

    @validates('_keepdays')
    def validate_keepdays(self, key, value):
        int(value)
        return value

    def __str__(self):
        if self.user:
            return f"{self.user.username}/{self.repopath}"
        return f"None/{self.repopath}"

    def __repr__(self):
        return f"RepoObject({self.id}, {self.repopath})"

    def check_activity(self):
        """
        Check if the repository is inactive according to maxage.
        Return None if maxage is undefied.
        Return True if repository is active.
        """
        if self.maxage <= 0:
            return None
        # Loop on session statistics to check backup activity.
        age = 0
        start = RdiffTime()
        ignore_weekday = self.ignore_weekday
        while age < self.maxage:
            end = start
            start = end - timedelta(days=1)
            for stats in self.session_statistics[start:end]:
                if stats.newfiles > 0 or stats.deletedfiles > 0 or stats.changedfiles > 0:
                    # Activity found !
                    return True
            # Only increase age if weekday is not ignored.
            if start.weekday() not in ignore_weekday:
                age += 1
        return False

    @property
    def ignore_weekday(self):
        """
        Return list of days to ignore. Index 0 is monday.
        """
        value = self._ignore_weekday
        return [idx for idx in range(0, 7) if value & (1 << idx)]

    @ignore_weekday.setter
    def ignore_weekday(self, value):
        """
        Set list of days to ignore. Index 0 is monday.
        """
        if not value:
            self._ignore_weekday = 0
        else:
            self._ignore_weekday = sum([1 << idx for idx in range(0, 7) if idx in value])

    @property
    def status(self):
        """
        This implementation merge the database status with the on-disk status.
        """
        try:
            if self._status == RepoObject.STATUS_DELETING:
                return (RepoObject.STATUS_DELETING, _("Deletion in progress..."))
            return RdiffRepo.status.__get__(self, self)
        except Exception:
            pass


@event.listens_for(Base.metadata, 'after_create')
def update_repo_schema(target, conn, **kw):
    # Add repo's Encoding
    if not column_exists(conn, RepoObject._encoding_name):
        column_add(conn, RepoObject._encoding_name)
    if not column_exists(conn, RepoObject._keepdays):
        column_add(conn, RepoObject._keepdays)
    # Add ignore_weekday column to repo table
    if not column_exists(conn, RepoObject._ignore_weekday):
        column_add(conn, RepoObject._ignore_weekday)
    # Add notes column
    if not column_exists(conn, RepoObject.notes):
        column_add(conn, RepoObject.notes)
    # Add status column
    if not column_exists(conn, RepoObject._status):
        column_add(conn, RepoObject._status)
    # Remove preceding and leading slash (/) generated by previous
    # versions. Also rename '.' to ''
    result = RepoObject.query.all()
    for row in result:
        if row.repopath.startswith('/') or row.repopath.endswith('/'):
            row.repopath = row.repopath.strip('/')
            row.add().flush()
        if row.repopath == '.':
            row.repopath = ''
            row.add().flush()

    # Remove duplicates and nested repositories.
    result = RepoObject.query.order_by(RepoObject.userid, RepoObject.repopath).all()
    prev_repo = (None, None)
    for row in result:
        if prev_repo[0] == row.userid and (prev_repo[1] == row.repopath or row.repopath.startswith(prev_repo[1] + '/')):
            row.delete()
        else:
            prev_repo = (row.userid, row.repopath)


@event.listens_for(RepoObject._encoding_name, "set")
def encoding_set(target, value, oldvalue, initiator):
    """When updating encoding, also update the codec in backend."""
    if value is None:
        # Do nothing
        return
    codec = encodings.search_function(value)
    if codec:
        target._encoding = codec


@event.listens_for(Session, 'before_flush')
def user_before_flush(session, flush_context, instances):
    """
    Publish event when repo is added
    """
    from ._user import UserObject

    for repoobj in session.new:
        if isinstance(repoobj, RepoObject):
            userobj = repoobj.user or UserObject.query.filter(UserObject.id == repoobj.userid).first()
            cherrypy.engine.publish('repo_added', userobj, repoobj.repopath)


@event.listens_for(Session, 'after_flush')
def repo_after_flush(session, flush_context):
    """
    Publish event when repo is deleted.
    """
    from ._user import UserObject

    for repoobj in session.deleted:
        if isinstance(repoobj, RepoObject):
            userobj = repoobj.user or UserObject.query.filter(UserObject.id == repoobj.userid).first()
            add_post_commit_tasks(session, 'repo_deleted', userobj, repoobj.repopath)
