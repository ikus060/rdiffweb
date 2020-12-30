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
import sqlite3
import sys

import pkg_resources

from rdiffweb.core import RdiffError, authorizedkeys
from rdiffweb.core.config import BoolOption, read_config, Option, IntOption
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.ldap_auth import LdapPasswordStore
from rdiffweb.core.librdiff import RdiffRepo, DoesNotExistError, \
    AccessDeniedError
from rdiffweb.core.passwd import check_password, hash_password

# Define the logger
logger = logging.getLogger(__name__)

SEP = b'/'

DEFAULT_REPO_ENCODING = codecs.lookup((sys.getfilesystemencoding() or 'utf-8').lower()).name

# Define roles
ADMIN_ROLE = 0
MAINTAINER_ROLE = 5
USER_ROLE = 10
ROLES = [ADMIN_ROLE, MAINTAINER_ROLE, USER_ROLE]


def normpath(val):
    """
    Normalize path value.
    Remove leading /
    Add ending /
    """
    if not val.endswith(SEP):
        val += SEP
    if val.startswith(SEP):
        val = val[1:]
    return val


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

    def __init__(self, store, data):
        """
        Create a new UserObject from a username or a record.
        """
        assert store
        assert isinstance(data, int) or isinstance(data, dict)
        self._store = store
        self._db = store._database
        if isinstance(data, str):
            self._record = None
            self._userid = data
        else:
            self._record = data
            self._userid = data['userid']

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
                logger.info("add key [%s] to [%s] authorized_keys", key, self.username)
                authorizedkeys.add(fh, key)
        else:
            # Also look in database.
            logger.info("add key [%s] to [%s] database", key, self.username)
            try:
                inserted = self._db.insert('sshkeys',
                    userid=self._userid,
                    fingerprint=key.fingerprint,
                    key=key.getvalue())
                assert inserted
            except sqlite3.IntegrityError:  # @UndefinedVariable
                raise DuplicateSSHKeyError(_("Duplicate key. This key already exists or is associated to another user."))
        self._store._notify('user_attr_changed', self, {'authorizedkeys': True })

    def add_repo(self, repopath):
        """
        Add a Repo for the current user.
        """
        assert isinstance(repopath, bytes) or isinstance(repopath, str)
        if isinstance(repopath, bytes):
            repopath = os.fsdecode(repopath)
        repopath = repopath.strip('/')

        # Check if the repopath already exists.
        try:
            self.get_repo(repopath)
            raise ValueError('repo already exists: %s' % repopath)
        except DoesNotExistError:
            pass

        # Create entry in database
        assert self._db.insert('repos', userid=self._userid, repopath=repopath)
        return self.get_repo(repopath)

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
        self._db.delete('sshkeys', userid=self._userid)
        self._db.delete('repos', userid=self._userid)
        deleted = self._db.delete('users', userid=self._userid)
        assert deleted, 'fail to delete user'
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
                logger.info("removing key [%s] from [%s] authorized_keys", fingerprint, self.username)
                authorizedkeys.remove(fh, fingerprint)
        else:
            # Also look in database.
            logger.info("removing key [%s] from [%s] database", fingerprint, self.username)
            deleted = self._db.delete('sshkeys', userid=self._userid, fingerprint=fingerprint)
            assert deleted
        self._store._notify('user_attr_changed', self, {'authorizedkeys': True })

    def __eq__(self, other):
        return isinstance(other, UserObject) and self._userid == other._userid

    def __str__(self):
        return 'UserObject(%s)' % self._userid

    def _get_attr(self, key):
        """Return user's attribute"""
        assert key in ['userid', 'username', 'role', 'useremail', 'userroot', 'password'], "invalid attribute: " + key
        if not self._record:
            self._record = self._db.findone('users', userid=self._userid)
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
        for record in self._db.find('sshkeys', userid=self._userid):
            yield authorizedkeys.check_publickey(record['key'])

    def get_repo(self, repopath):
        """
        Return a repo object.
        """
        assert isinstance(repopath, bytes) or isinstance(repopath, str)
        if isinstance(repopath, bytes):
            repopath = os.fsdecode(repopath)
        repopath = repopath.strip('/')

        # Search the repo with and without leading "/"
        row = (self._db.findone('repos', userid=self.userid, repopath=repopath)
               or self._db.findone('repos', userid=self.userid, repopath="/" + repopath)
               or self._db.findone('repos', userid=self.userid, repopath=repopath + "/")
               or self._db.findone('repos', userid=self.userid, repopath="/" + repopath + "/"))
        if not row:
            raise DoesNotExistError(self.userid, repopath)
        return RepoObject(self, row)

    def _get_repos(self):
        """
        Get list of repos for the current `username`.
        """
        rows = self._db.find('repos', userid=self._userid)
        return [row['repopath'] for row in rows]

    @property
    def is_ldap(self):
        """Return True if this user is an LDAP user. (with a password)"""
        return not self._get_attr('password')

    def _is_role(self, role):
        assert role in ROLES
        try:
            return int(self._get_attr('role')) <= role
        except:
            return False

    def _set_attr(self, obj_key, key, value, notify=True):
        """Used to define an attribute"""
        assert key in ['role', 'useremail', 'userroot', 'password'], "invalid attribute: " + key
        updated = self._db.update('users', userid=self._userid, **{key: value})
        assert updated, 'update failed'
        if self._record:
            self._record[key] = value
        # Call notification listener
        if notify:
            self._store._notify('user_attr_changed', self, {obj_key: value})

    def set_password(self, password, old_password=None):
        """
        Change the user's password. Raise a ValueError if the username or
        the password are invalid.
        """
        assert isinstance(password, str)
        assert old_password is None or isinstance(old_password, str)
        if not password:
            raise ValueError("password can't be empty")

        # Try to update the user password in LDAP
        for store in self._store._password_stores:
            try:
                valid = store.are_valid_credentials(self.username, old_password)
                if valid:
                    store.set_password(self.username, password, old_password)
                    return
            except:
                pass
        # Fallback to database
        if old_password and not check_password(old_password, self.hash_password):
            raise ValueError(_("Wrong password"))
        self.hash_password = hash_password(password)
        self._store._notify('user_password_changed', self.username, password)

    def update_repos(self):
        """
        Refresh the users repositories.
        """
        # Remove slash generated by previous versions.
        for row in self._db.find('repos', userid=self._userid):
            if row['repopath'].startswith('/') or row['repopath'].endswith('/'):
                self._db.update('repos', repoid=row['repoid'], repopath=row['repopath'].strip('/'))

        # Remove duplicates and nested
        rows = sorted(self._db.find('repos', userid=self._userid), key=lambda row: row['repopath'])
        prev_repo = ''
        for row in rows:
            if row['repopath'] == prev_repo or row['repopath'].startswith(prev_repo + '/'):
                self._db.delete('repos', repoid=row['repoid'])
            else:
                prev_repo = row['repopath']

        # Update the repositories
        def _onerror(error):
            logger.error('error updating user [%s] repos' % self.username, exc_info=1)

        user_root = os.fsencode(self.user_root)
        for root, dirs, unused_files in os.walk(user_root, _onerror):
            for name in dirs:
                if name == b'rdiff-backup-data':
                    repopath = os.path.relpath(root, start=user_root)
                    # Handle special scenario when the repo is the user_root
                    repopath = b'' if repopath == b'.' else repopath
                    try:
                        self.get_repo(repopath)
                        del dirs[:]
                    except DoesNotExistError:
                        self.add_repo(repopath)
                        del dirs[:]
            if root.count(SEP) - user_root.count(SEP) >= self._store._max_depth:
                del dirs[:]

    # Declare properties
    userid = property(fget=lambda x: x._get_attr('userid'))
    is_admin = property(fget=lambda x: x._is_role(ADMIN_ROLE))
    is_maintainer = property(fget=lambda x: x._is_role(MAINTAINER_ROLE))
    email = property(fget=lambda x: x._get_attr('useremail'), fset=lambda x, y: x._set_attr('email', 'useremail', y))
    user_root = property(fget=lambda x: x._get_attr('userroot'), fset=lambda x, y: x._set_attr('user_root', 'userroot', y))
    username = property(fget=lambda x: x._get_attr('username'))
    repos = property(fget=lambda x: list(map(lambda y: y, x._get_repos())))
    role = property(fget=lambda x: x._get_attr('role'), fset=lambda x, y: x._set_attr('role', 'role', int(y)))
    authorizedkeys = property(fget=lambda x: x._get_authorizedkeys())
    repo_objs = property(fget=lambda x: [RepoObject(x, r) for r in x._get_repos()])
    disk_quota = property(fget=lambda x: x._store.app.quota.get_disk_quota(x), fset=lambda x, y: x._store.app.quota.set_disk_quota(x, y))
    hash_password = property(fget=lambda x: x._get_attr('password'), fset=lambda x, y: x._set_attr('password', 'password', y))
    disk_usage = property(fget=lambda x: x._store.app.quota.get_disk_usage(x))


class RepoObject(RdiffRepo):
    """Represent a repository."""

    def __init__(self, user_obj, data):
        assert user_obj
        assert isinstance(data, str) or isinstance(data, dict)
        self._db = user_obj._db
        self._user_obj = user_obj
        self._userid = user_obj._userid
        if isinstance(data, str):
            self._repo = data
            self._record = None
        else:
            self._repo = data['repopath']
            self._record = data
        RdiffRepo.__init__(self, user_obj.user_root, self._repo, encoding=DEFAULT_REPO_ENCODING)
        self._encoding = self._get_encoding()

    def __eq__(self, other):
        return (isinstance(other, RepoObject) and
                self._userid == other._userid and
                self._repo == other._repo)

    def __str__(self):
        return 'RepoObject[%s, %s]' % (self._userid, self._repo)

    def _set_attr(self, key, value):
        """Used to define an attribute to the repository."""
        assert key in ['encoding', 'maxage', 'keepdays'], 'invalid attribute:' + key
        if key in ['maxage', 'keepdays']:
            value = int(value)
        updated = self._db.update('repos', **{'userid': self._userid, 'repopath': self._repo, key: value})
        assert updated, 'update failed'
        if self._record:
            self._record[key] = value

    def _get_attr(self, key, default=None):
        assert key in ['encoding', 'maxage', 'keepdays'], 'invalid attribute:' + key
        if not self._record:
            self._record = self._db.findone('repos', userid=self._userid, repopath=self._repo)
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

        # Read encoding value from obsolete config file.
        try:
            conf_file = os.path.join(self._data_path, b'rdiffweb')
            if os.access(conf_file, os.F_OK) and os.path.isfile(conf_file):
                config = read_config(conf_file)
                encoding = config.get('encoding')
                if encoding:
                    return encodings.search_function(encoding)
        except:
            logger.exception("fail to get repo encoding from file")

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
        rowcount = self._db.delete('repos', userid=self._userid, repopath=self._repo)
        assert rowcount, 'fail to delete repository'
        RdiffRepo.delete(self)

    encoding = property(lambda x: x._encoding.name, _set_encoding)
    maxage = property(fget=lambda x: x._get_attr('maxage', default=0), fset=lambda x, y: x._set_attr('maxage', y))
    keepdays = property(fget=lambda x: x._get_attr('keepdays', default=-1), fset=lambda x, y: x._set_attr('keepdays', y))


class Store():
    """
    This class handle all data storage operations.
    """

    _db_file = Option("SQLiteDBFile", "/etc/rdiffweb/rdw.db")
    _allow_add_user = BoolOption("AddMissingUser", False)
    _admin_user = Option("AdminUser", "admin")
    _max_depth = IntOption('MaxDepth', default=5)

    def __init__(self, app):
        self.app = app
        from rdiffweb.core.store_sqlite import SQLiteBackend
        self._database = SQLiteBackend(self._db_file)
        self._password_stores = [LdapPasswordStore(app)]
        self._change_listeners = []

        # Register entry point.
        for entry_point in pkg_resources.iter_entry_points('rdiffweb.IUserChangeListener'):  # @UndefinedVariable
            try:
                cls = entry_point.load()
                # Creating the listener should register it self.But let make sure of it.
                listener = cls(self.app)
                if listener not in self._change_listeners:
                    self._change_listeners.append(listener)
            except:
                logging.error("IUserChangeListener [%s] fail to load", entry_point)

    def create_admin_user(self):
        # Check if admin user exists. If not, created it.
        if not self.get_user(self._admin_user):
            userobj = self.add_user(self._admin_user, 'admin123')
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
        if password:
            inserted = self._database.insert('users', username=user, password=hash_password(password))
        else:
            inserted = self._database.insert('users', username=user, password='')
        assert inserted
        record = self._database.findone('users', username=user)
        userobj = UserObject(self, record)
        self._notify('user_added', userobj, attrs)
        # Return user object
        return userobj

    def count_users(self):
        return self._database.count('users')

    def count_repos(self):
        return self._database.count('repos')

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
        record = self._database.findone('users', username=user)
        if record:
            return UserObject(self, record)
        return None

    def users(self, search=None, criteria=None):
        """
        Search users database. Return a generator of user object.
        
        search: Define a search term to look into email or username.
        criteria: Define a search filter: admins, ldap
        """
        if search:
            users = self._database.search('users', search, 'username', 'useremail')
        elif criteria:
            if criteria == 'admins':
                users = self._database.find('users', role=ADMIN_ROLE)
            elif criteria == 'ldap':
                users = self._database.find('users', password='')
            else:
                return
        else:
            users = self._database.find('users')
        for record in users:
            yield UserObject(self, record)

    def repos(self, search=None, criteria=None):
        """
        Quick listing of all the repository object for all user.
        
        search: Define a search term to look into path, email or username.
        criteria: Define a search filter: ok, failed, interrupted, in_progress
        """
        if search:
            repos = self._database.search('repos', search, 'RepoPath', 'username', 'useremail')
        else:
            repos = self._database.find('repos')

        for record in repos:
            user_record = self._database.findone('users', userid=record['userid'])
            user_obj = UserObject(self, user_record)
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
        if userobj or self._allow_add_user:
            for store in self._password_stores:
                try:
                    valid = store.are_valid_credentials(user, password)
                    if valid:
                        real_user, attrs = valid
                        if not userobj:
                            userobj = self.add_user(real_user, attrs=attrs)
                        self._notify('user_logined', userobj, attrs)
                        return userobj
                except:
                    logger.warn('fail to validate credentials', exc_info=1)
        return None

    def _notify(self, mod, *args):
        for listener in self._change_listeners:
            # Support divergent account change listener implementations too.
            try:
                logger.debug('notify %s#%s()', listener.__class__.__name__, mod)
                getattr(listener, mod)(*args)
            except:
                logger.warning(
                    'IUserChangeListener [%s] fail to run [%s]',
                    listener.__class__.__name__, mod, exc_info=1)
