# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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
from io import open
import logging
import os
import sys

import pkg_resources
from rdiffweb.core import RdiffError, authorizedkeys
from rdiffweb.core.config import Option
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.ldap_auth import LdapPasswordStore
from rdiffweb.core.librdiff import RdiffRepo, DoesNotExistError, \
    AccessDeniedError
from rdiffweb.core.passwd import check_password, hash_password
from sqlalchemy import Table, Column, Integer, SmallInteger, String, MetaData, Text
from sqlalchemy import create_engine
from sqlalchemy.sql.expression import select, or_, and_
from sqlalchemy.sql.functions import count
from sqlalchemy.exc import IntegrityError

# Define the logger
logger = logging.getLogger(__name__)

SEP = b'/'

DEFAULT_REPO_ENCODING = codecs.lookup(
    (sys.getfilesystemencoding() or 'utf-8').lower()).name

# Define roles
ADMIN_ROLE = 0
MAINTAINER_ROLE = 5
USER_ROLE = 10
ROLES = {
    'admin': ADMIN_ROLE,
    'maintainer': MAINTAINER_ROLE,
    'user': USER_ROLE,
}

# Define SQLAlchemy metadata
_META = MetaData()
_USERS = Table('users', _META,
               Column('UserID', Integer, key='userid', primary_key=True),
               Column('Username', String, key='username',
                      nullable=False, unique=True),
               Column('Password', String, key='password',
                      nullable=False, server_default=""),
               Column('UserRoot', String, key='user_root',
                      nullable=False, server_default=""),
               Column('IsAdmin', SmallInteger, key='is_admin', nullable=False,
                      server_default="0", doc="DEPRECATED This column is replaced by 'role'"),
               Column('UserEmail', String, key='email',
                      nullable=False, server_default=""),
               Column('RestoreFormat', SmallInteger, nullable=False,
                      server_default="1", doc="DEPRECATED This column is not used anymore"),
               Column('role', SmallInteger, nullable=False,
                      server_default=str(USER_ROLE)),
               sqlite_autoincrement=True,
               )

_REPOS = Table('repos', _META,
               Column('RepoID', Integer, key='repoid',
                      primary_key=True, autoincrement=True),
               Column('UserID', Integer, key='userid', nullable=False),
               Column('RepoPath', String, key='repopath', nullable=False),
               Column('MaxAge', SmallInteger, key='maxage',
                      nullable=False, server_default="0"),
               Column('Encoding', String, key='encoding'),
               Column('keepdays', String, nullable=False, server_default=""),
               sqlite_autoincrement=True,
               )

_SSHKEYS = Table('sshkeys', _META,
                 Column('Fingerprint', Text, key='fingerprint'),
                 Column('Key', Text, key='key', unique=True),
                 Column('UserID', Integer, key='userid', nullable=False),
                 )


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


class DuplicateSSHKeyError(Exception):
    """
    Raised by add_authorizedkey when trying to add the same SSH Key twice.
    """
    pass


class IUserChangeListener():
    """
    A listener to receive user changes event.
    """

    def __init__(self, app):
        self.app = app
        self.app.store.add_change_listener(self)

    def user_added(self, userobj, attrs):
        """New user (account) created."""

    def user_attr_changed(self, userobj, attrs={}):
        """User attribute changed."""

    def user_deleted(self, user):
        """User and related account information have been deleted."""

    def user_logined(self, userobj, attrs):
        """User successfully logged into rdiffweb."""

    def user_password_changed(self, user, password):
        """Password changed."""


class UserObject(object):
    """Represent an instance of user."""

    _ATTRS = ['username', 'role', 'email', 'user_root', 'password']

    def __init__(self, store, data):
        """
        Create a new UserObject from a username or a record.

        `data` a dict or a SQLAlchemy row.

        """
        assert store
        assert 'userid' in data
        self._store = store
        self._record = {k: data[k] for k in self._ATTRS}
        self._userid = data[_USERS.c.userid]

    def add_authorizedkey(self, key, comment=None):
        """
        Add the given key to the user. Adding the key to his `authorized_keys`
        file if it exists and adding it to database.
        """
        # Parse and validate ssh key
        assert key
        key = authorizedkeys.check_publickey(key)
        assert key, "invalid ssh key"

        # Remove option, replace comments.
        key = authorizedkeys.AuthorizedKey(
            options=None,
            keytype=key.keytype,
            key=key.key,
            comment=comment or key.comment)

        # If a filename exists, use it by default.
        filename = os.path.join(self.user_root, '.ssh', 'authorized_keys')
        if os.path.isfile(filename):
            with open(filename, mode="r+", encoding='utf-8') as fh:
                if authorizedkeys.exists(fh, key):
                    raise DuplicateSSHKeyError(_("SSH key already exists"))
                logger.info(
                    "add key [%s] to [%s] authorized_keys", key, self.username)
                authorizedkeys.add(fh, key)
        else:
            # Also look in database.
            logger.info("add key [%s] to [%s] database", key, self.username)
            try:
                with self._store.engine.connect() as conn:
                    conn.execute(_SSHKEYS.insert().values(
                        userid=self._userid, fingerprint=key.fingerprint, key=key.getvalue()))
            except IntegrityError:
                raise DuplicateSSHKeyError(
                    _("Duplicate key. This key already exists or is associated to another user."))
        self._store._notify('user_attr_changed', self,
                            {'authorizedkeys': True})

    def valid_user_root(self):
        """
        Check if the current user_root is valid and readable
        """
        try:
            return os.access(self.user_root, os.F_OK) and os.path.isdir(self.user_root)
        except:
            return False

    def delete(self):
        """
        Delete the given user from password store.

        Return True if the user was deleted.
        Return False if the user didn't exists.
        Raise a ValueError when trying to delete the admin user.
        """
        # Make sure we are not trying to delete the admin user.
        if self.username == self._store._admin_user:
            raise ValueError(_("can't delete admin user"))

        # Delete user from database (required).
        logger.info("deleting user [%s] from database", self.username)
        with self._store.engine.connect() as conn:
            conn.execute(_SSHKEYS.delete(_SSHKEYS.c.userid == self._userid))
            conn.execute(_REPOS.delete(_REPOS.c.userid == self._userid))
            deleted = conn.execute(_USERS.delete(
                _USERS.c.userid == self._userid))
            assert deleted.rowcount, 'fail to delete user'
        self._store._notify('user_deleted', self.username)
        return True

    def delete_authorizedkey(self, fingerprint):
        """
        Remove the given key from the user. Remove the key from his
        `authorized_keys` file if it exists and from database database.
        """
        # If a filename exists, use it by default.
        filename = os.path.join(self.user_root, '.ssh', 'authorized_keys')
        if os.path.isfile(filename):
            with open(filename, mode='r+', encoding='utf-8') as fh:
                logger.info(
                    "removing key [%s] from [%s] authorized_keys", fingerprint, self.username)
                authorizedkeys.remove(fh, fingerprint)
        else:
            # Also look in database.
            logger.info(
                "removing key [%s] from [%s] database", fingerprint, self.username)
            with self._store.engine.connect() as conn:
                conn.execute(_SSHKEYS.delete(
                    and_(_SSHKEYS.c.userid == self._userid, _SSHKEYS.c.fingerprint == fingerprint)))
        self._store._notify('user_attr_changed', self,
                            {'authorizedkeys': True})

    def __eq__(self, other):
        return isinstance(other, UserObject) and self._userid == other._userid

    def __str__(self):
        return 'UserObject(%s)' % self._userid

    def _get_attr(self, key):
        """Return user's attribute"""
        assert key in self._ATTRS, "invalid attribute: " + key
        return self._record[key]

    def _get_authorizedkeys(self):
        """
        Return an iterator on the authorized key. Either from his
        `authorized_keys` file if it exists or from database.
        """
        # If a filename exists, use it by default.
        filename = os.path.join(self.user_root, '.ssh', 'authorized_keys')
        if os.path.isfile(filename):
            for k in authorizedkeys.read(filename):
                yield k

        # Also look in database.
        with self._store.engine.connect() as conn:
            result = conn.execute(_SSHKEYS.select(
                _SSHKEYS.c.userid == self._userid))
            for record in result:
                yield authorizedkeys.check_publickey(record['key'])

    def get_repo(self, repopath):
        """
        Return a repo object.
        """
        assert isinstance(repopath, bytes) or isinstance(repopath, str)
        if isinstance(repopath, bytes):
            repopath = os.fsdecode(repopath)
        repopath = repopath.strip('/')

        # Search the repo in database
        with self._store.engine.connect() as conn:
            result = conn.execute(_REPOS.select(
                and_(_REPOS.c.userid == self.userid, _REPOS.c.repopath == repopath)))
            record = result.fetchone()
        if record:
            return RepoObject(self, record)

        raise DoesNotExistError(self.userid, repopath)

    def _get_repos_obj(self):
        """
        Return list of repositories object to reflect the filesystem folders.

        Return a RepoObject for each sub directories under `user_root` with `rdiff-backup-data`.
        """

        with self._store.engine.connect() as conn:

            # Update the repositories by walking in the directory tree.
            def _onerror(unused):
                logger.error(
                    'error updating user [%s] repos' % self.username, exc_info=1)

            dirty = False
            records = list(conn.execute(_REPOS.select(
                _REPOS.c.userid == self._userid).order_by(_REPOS.c.repopath)))
            user_root = os.fsencode(self.user_root)
            for root, dirs, unused_files in os.walk(user_root, _onerror):
                for name in dirs:
                    if name == b'rdiff-backup-data':
                        repopath = os.path.relpath(root, start=user_root)
                        # Handle special scenario when the repo is the
                        # user_root
                        repopath = b'' if repopath == b'.' else repopath

                        # Check if repo path exists.
                        if any(record['repopath'] == os.fsdecode(repopath) for record in records):
                            del dirs[:]
                        else:
                            # Add repository to database.
                            dirty = True
                            conn.execute(_REPOS.insert().values(
                                userid=self._userid, repopath=os.fsdecode(repopath)))
                            del dirs[:]
                if root.count(SEP) - user_root.count(SEP) >= self._store._max_depth:
                    del dirs[:]

            # Return list of repository object.
            if dirty:
                records = conn.execute(_REPOS.select(
                    _REPOS.c.userid == self._userid).order_by(_REPOS.c.repopath))
            return [RepoObject(self, record) for record in records]

    @property
    def is_ldap(self):
        """Return True if this user is an LDAP user. (with a password)"""
        return not self._get_attr('password')

    def _is_role(self, role):
        assert role in ROLES.values()
        try:
            return int(self._get_attr('role')) <= role
        except:
            return False

    def _set_attr(self, key, value, notify=True):
        """Used to define an attribute"""
        assert key in self._ATTRS, "invalid attribute: " + key
        with self._store.engine.connect() as conn:
            updated = conn.execute(_USERS.update().where(
                _USERS.c.userid == self._userid).values(**{key: value}))
            assert updated.rowcount
        self._record[key] = value
        # Call notification listener
        if notify:
            self._store._notify('user_attr_changed', self, {key: value})

    def set_password(self, password, old_password=None):
        """
        Change the user's password. Raise a ValueError if the username or
        the password are invalid.
        """
        assert isinstance(password, str)
        assert old_password is None or isinstance(old_password, str)
        if not password:
            raise ValueError("password can't be empty")

        # Cannot update admin-password if defined
        if self.username == self._store._admin_user and self._store._admin_password:
            raise ValueError(
                _("can't update admin-password defined in configuration file"))

        # Try to update the user password in LDAP
        try:
            valid = self._store._ldap_store.are_valid_credentials(
                self.username, old_password)
            if valid:
                self._store._ldap_store.set_password(
                    self.username, password, old_password)
                return
        except:
            pass
        # Fallback to database
        if old_password and not check_password(old_password, self.hash_password):
            raise ValueError(_("Wrong password"))
        self.hash_password = hash_password(password)
        self._store._notify('user_password_changed', self.username, password)

    def _set_user_root(self, value):
        """
        Used to take care of updating the user_root.

        When user_root get update, we also want to update the repository list
        to reflect the filesystem.
        """
        # Update the value
        self._set_attr('user_root', value)
        # Refresh the list of repository.
        self._get_repos_obj()

    # Declare properties
    userid = property(fget=lambda x: x._userid)
    is_admin = property(fget=lambda x: x._is_role(ADMIN_ROLE))
    is_maintainer = property(fget=lambda x: x._is_role(MAINTAINER_ROLE))
    email = property(fget=lambda x: x._get_attr('email'),
                     fset=lambda x, y: x._set_attr('email', y))
    user_root = property(fget=lambda x: x._get_attr(
        'user_root'), fset=lambda x, y: x._set_user_root(y))
    username = property(fget=lambda x: x._get_attr('username'))
    role = property(fget=lambda x: x._get_attr('role'),
                    fset=lambda x, y: x._set_attr('role', int(y)))
    authorizedkeys = property(fget=lambda x: x._get_authorizedkeys())
    repo_objs = property(fget=lambda x: x._get_repos_obj())
    disk_quota = property(fget=lambda x: x._store.app.quota.get_disk_quota(
        x), fset=lambda x, y: x._store.app.quota.set_disk_quota(x, y))
    hash_password = property(fget=lambda x: x._get_attr(
        'password'), fset=lambda x, y: x._set_attr('password', y))
    disk_usage = property(fget=lambda x: x._store.app.quota.get_disk_usage(x))


class RepoObject(RdiffRepo):
    """Represent a repository."""

    _ATTRS = ['encoding', 'maxage', 'keepdays']

    def __init__(self, user_obj, data):
        """
        Create a new repository object

        `data` a dict or a SQLAlchemy row.

        """
        assert user_obj
        assert 'repoid' in data
        assert 'repopath' in data
        self._user_obj = user_obj
        self._repoid = data['repoid']
        self._repo = data['repopath']
        self._record = {k: data[k] for k in self._ATTRS}
        RdiffRepo.__init__(self, user_obj.user_root,
                           self._repo, encoding=DEFAULT_REPO_ENCODING)
        self._encoding = self._get_encoding()

    def __eq__(self, other):
        return (isinstance(other, RepoObject) and
                self._user_obj._userid == other._user_obj._userid and
                self._repo == other._repo)

    def __str__(self):
        return 'RepoObject[%s, %s]' % (self._user_obj._userid, self._repo)

    def _set_attr(self, key, value):
        """Used to define an attribute to the repository."""
        assert key in self._ATTRS, 'invalid attribute:' + key
        if key in ['maxage', 'keepdays']:
            value = int(value)
        with self._user_obj._store.engine.connect() as conn:
            updated = conn.execute(_REPOS.update().where(
                _REPOS.c.repoid == self._repoid).values(**{key: value}))
            assert updated.rowcount, 'update failed'
        self._record[key] = value

    def _get_attr(self, key, default=None):
        assert key in self._ATTRS, 'invalid attribute:' + key
        value = self._record.get(key, default)
        if key in ['maxage', 'keepdays']:
            return int(value) if value else default
        return value

    @property
    def displayname(self):
        # Repository displayName is the "repopath" too.
        return self._repo.strip('/')

    @property
    def name(self):
        # Repository name is the "repopath"
        return self._repo

    @property
    def owner(self):
        return self._user_obj.username

    def _get_encoding(self):
        """Return the repository encoding in a normalized format (lowercase and replace - by _)."""
        # For backward compatibility, look into the database and fallback to
        # the rdiffweb config file in the repo.
        encoding = self._get_attr('encoding')
        if encoding:
            return encodings.search_function(encoding.lower())

        # Fallback to default encoding.
        return encodings.search_function(DEFAULT_REPO_ENCODING)

    def _set_encoding(self, value):
        """Change the repository encoding"""
        # Validate if the value is a valid encoding before updating the database.
        codec = encodings.search_function(value.lower())
        if not codec:
            raise ValueError(_('invalid encoding %s') % value)

        logger.info("updating repository %s encoding %s", self, codec.name)
        self._set_attr('encoding', codec.name)
        self._encoding = codec

    def delete(self):
        """Properly remove the given repository by updating the user's repositories."""
        logger.info("deleting repository %s", self)
        # Remove data from disk in background
        RdiffRepo.delete(self)
        # Remove entry from database after deleting files.
        # Otherwise, refresh will add this repo back.
        with self._user_obj._store.engine.connect() as conn:
            conn.execute(_REPOS.delete(_REPOS.c.repoid == self._repoid))

    encoding = property(lambda x: x._encoding.name, _set_encoding)
    maxage = property(fget=lambda x: x._get_attr(
        'maxage', default=0), fset=lambda x, y: x._set_attr('maxage', y))
    keepdays = property(fget=lambda x: x._get_attr(
        'keepdays', default=-1), fset=lambda x, y: x._set_attr('keepdays', y))


class Store():
    """
    This class handle all data storage operations.
    """

    _ldap_add_user = Option("ldap_add_missing_user")
    _ldap_add_user_default_role = Option("ldap_add_user_default_role")
    _ldap_add_user_default_userroot = Option("ldap_add_user_default_userroot")
    _debug = Option('debug')
    _db_uri = Option("database_uri")
    _allow_add_user = Option("ldap_add_missing_user")
    _admin_user = Option("admin_user")
    _admin_password = Option("admin_password")
    _max_depth = Option('max_depth')

    def __init__(self, app):
        self.app = app
        self.app.store = self
        # Connect to database
        uri = self._db_uri if '://' in self._db_uri else "sqlite:///" + self._db_uri
        self.engine = create_engine(uri, echo=self._debug)
        # Create tables if missing.
        _META.create_all(self.engine)

        self._ldap_store = LdapPasswordStore(app)
        self._change_listeners = []
        self._update()

        # Register entry point.
        # @UndefinedVariable
        for entry_point in pkg_resources.iter_entry_points('rdiffweb.IUserChangeListener'):
            try:
                cls = entry_point.load()
                # Creating the listener should register it self.But let make sure of it.
                listener = cls(self.app)
                if listener not in self._change_listeners:
                    self._change_listeners.append(listener)
            except:
                logging.error(
                    "IUserChangeListener [%s] fail to load", entry_point)

    def create_admin_user(self):
        # Check if admin user exists. If not, created it.
        userobj = self.get_user(self._admin_user)
        if not userobj:
            userobj = self.add_user(self._admin_user, 'admin123')
            userobj.role = ADMIN_ROLE
            userobj.user_root = '/backups'
        # Also make sure to update the password with latest value from config file.
        if self._admin_password:
            userobj.hash_password = self._admin_password
            userobj.role = ADMIN_ROLE

    def add_change_listener(self, listener):
        self._change_listeners.append(listener)

    def remove_change_listener(self, listener):
        self._change_listeners.remove(listener)

    def add_user(self, user, password=None, attrs=None):
        """
        Used to add a new user with an optional password.
        """
        assert password is None or isinstance(password, str)
        # Check if user already exists.
        if self.get_user(user):
            raise RdiffError(_("User %s already exists." % (user,)))

        # Find a database where to add the user
        logger.info("adding new user [%s]", user)
        with self.engine.connect() as conn:
            inserted = conn.execute(_USERS.insert().values(
                username=user, password=hash_password(password) if password else ''))
            assert inserted.rowcount
            record = conn.execute(_USERS.select(
                _USERS.c.username == user)).fetchone()
        userobj = UserObject(self, record)
        self._notify('user_added', userobj, attrs)
        # Return user object
        return userobj

    def count_users(self):
        with self.engine.connect() as conn:
            result = conn.execute(select([count('*')]).select_from(_USERS))
            return result.fetchone()[0]

    def count_repos(self):
        with self.engine.connect() as conn:
            result = conn.execute(select([count('*')]).select_from(_REPOS))
            return result.fetchone()[0]

    def get_repo(self, name, as_user=None):
        """
        Return the repository identified as `name`.
        `name` should be <username>/<repopath>
        """
        username, repopath = _split_path(name)
        repopath = os.fsdecode(repopath)

        # Check permissions
        as_user = as_user or self.app.currentuser
        assert as_user, "as_user or current user must be defined"
        if username != as_user.username and not as_user.is_admin:
            raise AccessDeniedError(name)

        # Get the userid associated to the username.
        user_obj = self.get_user(username)
        if not user_obj:
            raise DoesNotExistError(name)

        # Get the repo object.
        return user_obj.get_repo(repopath)

    def get_repo_path(self, path, as_user=None):
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
                    repo_obj = self.get_repo(path[:pos], as_user)
                    path_obj = repo_obj.get_path(path[pos + 1:])
                    return repo_obj, path_obj
                except DoesNotExistError:
                    # continue looping
                    startpos = pos + 1
        except ValueError:
            raise DoesNotExistError(path)

    def get_user(self, user):
        """Return a user object."""
        with self.engine.connect() as conn:
            record = conn.execute(_USERS.select(
                _USERS.c.username == user)).fetchone()
            if record:
                return UserObject(self, record)
        return None

    def users(self, search=None, criteria=None):
        """
        Search users database. Return a generator of user object.

        search: Define a search term to look into email or username.
        criteria: Define a search filter: admins, ldap
        """
        with self.engine.connect() as conn:
            if search:
                term = '%' + search + '%'
                result = conn.execute(_USERS.select().where(
                    or_(_USERS.c.username.like(term), _USERS.c.email.like(term))))
            elif criteria:
                if criteria == 'admins':
                    result = conn.execute(_USERS.select().where(
                        _USERS.c.role == ADMIN_ROLE))
                elif criteria == 'ldap':
                    result = conn.execute(
                        _USERS.select().where(_USERS.c.password == ''))
                else:
                    return []
            else:
                result = conn.execute(_USERS.select())
            # return users
            return [UserObject(self, record) for record in result]

    def repos(self, search=None, criteria=None):
        """
        Quick listing of all the repository object for all user.

        search: Define a search term to look into path, email or username.
        criteria: Define a search filter: ok, failed, interrupted, in_progress
        """
        with self.engine.connect() as conn:
            if search:
                result = conn.execute(select([_REPOS, _USERS]).where(_USERS.c.userid == _REPOS.c.userid).where(or_(
                    _USERS.c.username.contains(search),
                    _USERS.c.email.contains(search),
                    _REPOS.c.repopath.contains(search),
                ))
                )
            else:
                result = conn.execute(select([_REPOS, _USERS]).where(
                    _USERS.c.userid == _REPOS.c.userid))
            for record in result:
                user_obj = UserObject(self, record)
                repo_obj = RepoObject(user_obj, record)
                if not criteria or criteria == repo_obj.status[0]:
                    yield repo_obj

    def login(self, user, password):
        """
        Called to authenticate the given user.

        Check if the credentials are valid. Then may actually add the user
        in database if allowed.

        If valid, return the username. Return False if the user exists but the
        password doesn't matches. Return None if the user was not found in any
        password store.
        The return user object. The username may not be equals to the given username.
        """
        assert isinstance(user, str)
        assert password is None or isinstance(user, str)
        # Validate credential using database first.
        logger.debug("validating user [%s] credentials", user)
        userobj = self.get_user(user)
        if userobj and userobj.hash_password:
            if not check_password(password, userobj.hash_password):
                return None
            self._notify('user_logined', userobj, None)
            return userobj

        # Fallback to LDAP
        if userobj or self._ldap_add_user:
            try:
                valid = self._ldap_store.are_valid_credentials(user, password)
                if valid:
                    real_user, attrs = valid
                    if not userobj:
                        # In case default values are invalid, let evaluate them before creating the user in database.
                        default_user_root = self._ldap_add_user_default_userroot.format(
                            **attrs)
                        default_role = ROLES.get(
                            self._ldap_add_user_default_role)
                        userobj = self.add_user(real_user, attrs=attrs)
                        userobj.user_root = default_user_root
                        userobj.role = default_role
                    self._notify('user_logined', userobj, attrs)
                    return userobj
            except:
                logger.warn('fail to validate credentials', exc_info=1)
        return None

    def _notify(self, mod, *args):
        for listener in self._change_listeners:
            # Support divergent account change listener implementations too.
            try:
                logger.debug('notify %s#%s()',
                             listener.__class__.__name__, mod)
                getattr(listener, mod)(*args)
            except:
                logger.warning(
                    'IUserChangeListener [%s] fail to run [%s]',
                    listener.__class__.__name__, mod, exc_info=1)

    def _update(self):
        """
        Called on startup to update database schema.
        """
        with self.engine.connect() as conn:
            # Remove preceding and leading slash (/) generated by previous
            # versions. Also rename '.' to ''
            reult = conn.execute(_REPOS.select())
            for row in reult:
                if row['repopath'].startswith('/') or row['repopath'].endswith('/'):
                    conn.execute(_REPOS.update().where(_REPOS.c.repoid == row['repoid']).values(
                        repopath=row['repopath'].strip('/')))
                if row['repopath'] == '.':
                    conn.execute(_REPOS.update().where(
                        _REPOS.c.repoid == row['repoid']).values(repopath=''))

            # Remove duplicates and nested repositories.
            reult = conn.execute(_REPOS.select().order_by(
                _REPOS.c.userid, _REPOS.c.repopath))
            prev_repo = (None, None)
            for row in reult:
                if prev_repo[0] == row['userid'] and (prev_repo[1] == row['repopath'] or row['repopath'].startswith(prev_repo[1] + '/')):
                    conn.execute(_REPOS.delete(
                        _REPOS.c.repoid == row['repoid']))
                else:
                    prev_repo = (row['userid'], row['repopath'])
