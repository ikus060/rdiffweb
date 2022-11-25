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

import codecs
import encodings
import logging
import os
import sys

import cherrypy
from sqlalchemy import Column, Integer, SmallInteger, String, and_, case, event, orm
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, validates

import rdiffweb.tools.db  # noqa
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError, RdiffRepo
from rdiffweb.tools.i18n import ugettext as _

Base = cherrypy.tools.db.get_base()

logger = logging.getLogger(__name__)


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


class RepoObject(Base, RdiffRepo):
    DEFAULT_REPO_ENCODING = codecs.lookup((sys.getfilesystemencoding() or 'utf-8').lower()).name

    __tablename__ = 'repos'
    __table_args__ = {'sqlite_autoincrement': True}

    repoid = Column('RepoID', Integer, primary_key=True, autoincrement=True)
    userid = Column('UserID', Integer, nullable=False)
    user = relationship(
        'UserObject',
        foreign_keys=[userid],
        primaryjoin='UserObject.userid == RepoObject.userid',
        uselist=False,
        lazy=True,
    )
    repopath = Column('RepoPath', String, nullable=False, default='')
    maxage = Column('MaxAge', SmallInteger, nullable=False, server_default="0")
    encoding = Column('Encoding', String, default=DEFAULT_REPO_ENCODING)
    _keepdays = Column('keepdays', String, nullable=False, default="-1")

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
        as_user = as_user or cherrypy.tree.apps[''].currentuser
        if not as_user:
            raise AccessDeniedError("as_user or current user must be defined")
        if username != as_user.username and not as_user.is_admin:
            raise AccessDeniedError(name)

        # Search the repo in database
        query = RepoObject.query.join(UserObject, UserObject.userid == RepoObject.userid).filter(
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
            return repo_obj, path[pos + 1 :]
        except ValueError:
            raise DoesNotExistError(path)

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
        return case(
            (cls._keepdays.is_(None), -1),
            (cls._keepdays == '', -1),
            else_=cls._keepdays.cast(Integer),
        )

    @keepdays.setter
    def keepdays(self, value):
        self._keepdays = value

    def delete(self, path=b''):
        """Properly remove the given repository by updating the user's repositories."""
        logger.info("deleting repository %s", self)
        # Remove data from disk
        RdiffRepo.delete(self, path=path)
        # Remove entry from database after deleting files.
        # Otherwise, refresh will add this repo back.
        return super().delete()

    @validates('encoding')
    def validate_encoding(self, key, value):
        codec = encodings.search_function(value.lower())
        if not codec:
            raise ValueError(_('invalid encoding %s') % value)
        return codec.name

    @validates('maxage')
    def validate_maxage(self, key, value):
        int(value)
        return value

    @validates('_keepdays')
    def validate_keepdays(self, key, value):
        int(value)
        return value

    def __str__(self):
        return "RepoObject[%s, %s]" % (self.userid, self.repopath)


@event.listens_for(RepoObject.encoding, "set")
def encoding_set(target, value, oldvalue, initiator):
    codec = encodings.search_function(value)
    if codec:
        target._encoding = codec
