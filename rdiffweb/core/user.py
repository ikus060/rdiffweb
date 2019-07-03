#!/usr/bin/python
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

from __future__ import unicode_literals

from builtins import str, bytes
import encodings
from io import StringIO
from io import open
import logging
import os

import pkg_resources

from future.utils import python_2_unicode_compatible
from future.utils.surrogateescape import encodefilename
from rdiffweb.core import InvalidUserError, RdiffError, authorizedkeys
from rdiffweb.core.config import BoolOption, read_config
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.librdiff import RdiffRepo, DoesNotExistError, FS_ENCODING
from rdiffweb.core.user_ldap_auth import LdapPasswordStore
from rdiffweb.core.user_sqlite import SQLiteUserDB

# Define the logger
logger = logging.getLogger(__name__)

SEP = b'/'


def normpath(val):
    "Normalize path value"
    if not val.endswith(SEP):
        val += SEP
    if val.startswith(SEP):
        val = val[1:]
    return val


class IUserChangeListener():
    """
    A listener to receive user changes event.
    """

    def __init__(self, app):
        self.app = app
        self.app.userdb.add_change_listener(self)

    def user_added(self, userobj, attrs):
        """New user (account) created."""

    def user_attr_changed(self, username, attrs={}):
        """User attribute changed."""

    def user_deleted(self, user):
        """User and related account information have been deleted."""

    def user_logined(self, userobj, attrs):
        """User successfully logged into rdiffweb."""

    def user_password_changed(self, user, password):
        """Password changed."""


class IUserQuota():
    """
    Extension point to get user quotas
    """
    
    def get_disk_usage(self, userobj):
        """
        Return the user disk space.
        """

    def get_disk_quota(self, userobj, value):
        """
        Return the current user's quota.
        """

    def set_disk_quota(self, userobj, value):
        """
        Sets the user's quota.
        """


@python_2_unicode_compatible
class UserObject(object):
    """Represent an instance of user."""

    def __init__(self, userdb, db, username):
        assert userdb
        assert db
        assert username
        self._userdb = userdb
        self._db = db
        self._username = username

    def __eq__(self, other):
        return (isinstance(other, UserObject) and
                self._username == other._username and
                self._db == other._db)

    def __str__(self):
        return 'UserObject[%s]' % self._username

    @property
    def username(self):
        return self._username

    def get_repo(self, name):
        """
        Return the repository identified as `name`.
        `name` may be a bytes string or unicode string.
        """
        assert isinstance(name, str) or isinstance(name, bytes)
        if isinstance(name, str):
            name = encodefilename(name)
        name = normpath(name)
        for r in self._get_repos():
            if name == normpath(encodefilename(r)):
                return RepoObject(self, r)
        raise DoesNotExistError(name)
    
    def get_repo_path(self, path):
        """
        Return a the repository identified by the given `path`.
        """
        assert isinstance(path, str) or isinstance(path, bytes)
        if isinstance(path, str):
            path = encodefilename(path)
        path = normpath(path)
        for r in self._get_repos():
            repo = normpath(encodefilename(r))
            if path.startswith(repo):                
                repo_obj = RepoObject(self, r)
                path_obj = repo_obj.get_path(path[len(repo):])
                return (repo_obj, path_obj)
        raise DoesNotExistError(path)

    def _get_repos(self):
        """Return list of repository name."""
        return [r.strip('/') for r in self._db.get_repos(self._username)]

    def set_attr(self, key, value, notify=True):
        """Used to define an attribute"""
        self.set_attrs(**{key: value, 'notify': notify})

    def set_attrs(self, **kwargs):
        """Used to define multiple attributes at once."""
        notify = kwargs.pop('notify', True)
        for key, value in kwargs.items():
            assert key in ['is_admin', 'email', 'user_root', 'repos', 'authorizedkeys']
            setter = getattr(self._db, 'set_%s' % key)
            setter(self._username, value)
        # Call notification listener
        if notify:
            self._userdb._notify('user_attr_changed', self._username, kwargs)

    @property
    def disk_usage(self):
        
        # Check quota
        for entry_point in pkg_resources.iter_entry_points('rdiffweb.IUserQuota'):  # @UndefinedVariable
            try:
                cls = entry_point.load()
                return cls(self._userdb.app).get_disk_usage(self)
            except:
                logger.warning('IuserQuota [%s] fail to run', entry_point, exc_info=1)
        
        # Fall back to disk spaces.
        # Get the value from os and store in session.
        try:
            statvfs = os.statvfs(self.user_root)
            return {  # @UndefinedVariable
                'avail': statvfs.f_frsize * statvfs.f_bavail,
                'used': statvfs.f_frsize * (statvfs.f_blocks - statvfs.f_bavail),
                'size': statvfs.f_frsize * statvfs.f_blocks}
        except:
            return None

    def set_disk_quota(self, value):
        """
        Sets usr's quota using one of the IUserQuota. If none available, raise an exception.
        """
        for entry_point in pkg_resources.iter_entry_points('rdiffweb.IUserQuota'):  # @UndefinedVariable
            cls = entry_point.load()
            cls(self._userdb.app).set_disk_quota(self, value)
        
    def get_disk_quota(self):
        """
        Get user's quota using one of the IUserQuota. If none available, raise an exception.
        """
        for entry_point in pkg_resources.iter_entry_points('rdiffweb.IUserQuota'):  # @UndefinedVariable
            try:
                cls = entry_point.load()
                return cls(self._userdb.app).get_disk_quota(self)
            except:
                logger.warning('IuserQuota [%s] fail to run', entry_point, exc_info=1)
        return 0
    
    def get_authorizedkeys(self):
        """
        Return an iterator on the authorized key. Either from his
        `authorized_keys` file if it exists or from database.
        """
        # If a filename exists, use it by default.
        filename = os.path.join(self.user_root, '.ssh', 'authorized_keys')
        if os.path.isfile(filename):
            return authorizedkeys.read(filename)
        
        # Also look in database.
        data = self._db.get_authorizedkeys(self._username)
        return authorizedkeys.read(StringIO(data))
        
    def add_authorizedkey(self, key, comment=None):
        """
        Add the given key to the user. Adding the key to his `authorized_keys`
        file if it exists and adding it to database.
        """
        # Parse and validate ssh key
        assert key
        try:
            key = authorizedkeys.check_publickey(key)
        except ValueError:
            raise ValueError(_("Invalid SSH key."))
        
        if comment:
            key = authorizedkeys.AuthorizedKey(
                options=key.options,
                keytype=key.keytype,
                key=key.key,
                comment=comment)
        
        # If a filename exists, use it by default.
        filename = os.path.join(self.user_root, '.ssh', 'authorized_keys')
        if os.path.isfile(filename):
            with open(filename, mode="r+", encoding='utf-8') as fh:
                if authorizedkeys.exists(fh, key):
                    raise ValueError(_("SSH key already exists"))
                logger.info("add key [%s] to [%s]", key, self.username)
                authorizedkeys.add(fh, key)
                fh.seek(0, 0)
                data = fh.read()
        else:
            # Also look in database.
            data = self._db.get_authorizedkeys(self._username)
            fh = StringIO(data)
            if authorizedkeys.exists(fh, key):
                raise ValueError(_("SSH key already exists."))
            # Add key to file
            logger.info("add key [%s] to [%s]", key, self.username)
            fh = StringIO(data)
            authorizedkeys.add(fh, key)
            data = fh.getvalue()
        self.set_attr('authorizedkeys', data)
        
    def remove_authorizedkey(self, key):
        """
        Remove the given key from the user. Remove the key from his
        `authorized_keys` file if it exists and from database database.
        
        `key` should define a fingerprint
        """
        # If a filename exists, use it by default.
        filename = os.path.join(self.user_root, '.ssh', 'authorized_keys')
        if os.path.isfile(filename):
            with open(filename, mode='r+', encoding='utf-8') as fh:
                logger.info("removing key [%s] from [%s]", key, self.username)
                authorizedkeys.remove(fh, key)
                fh.seek(0, 0)
                data = fh.read()
        else:
            # Also look in database.
            data = self._db.get_authorizedkeys(self._username)
            fh = StringIO(data)
            logger.info("removing key [%s] from [%s]", key, self.username)
            authorizedkeys.remove(fh, key)
            data = fh.getvalue()
        self.set_attr('authorizedkeys', data)

    # Declare properties
    is_admin = property(fget=lambda x: x._db.is_admin(x._username), fset=lambda x, y: x.set_attr('is_admin', y))
    email = property(fget=lambda x: x._db.get_email(x._username), fset=lambda x, y: x.set_attr('email', y))
    user_root = property(fget=lambda x: x._db.get_user_root(x._username), fset=lambda x, y: x.set_attr('user_root', y))
    repos = property(_get_repos, fset=lambda x, y: x.set_attr('repos', y))
    authorizedkeys = property(fget=lambda x: x.get_authorizedkeys())
    repo_objs = property(fget=lambda x: [x.get_repo(name) for name in x.repos])
    disk_quota = property(get_disk_quota, set_disk_quota)
    

@python_2_unicode_compatible
class RepoObject(RdiffRepo):
    """Represent a repository."""

    def __init__(self, user_obj, repo):
        assert isinstance(repo, str)
        self._repo = repo
        self._user_obj = user_obj
        RdiffRepo.__init__(self, user_obj.user_root, repo)
        self._encoding = encodings.search_function(self.encoding)

    def __eq__(self, other):
        return (isinstance(other, RepoObject) and
                self._user_obj.username == other._user_obj._username and
                self._repo == other._repo)

    def __str__(self):
        return 'RepoObject[%s, %s]' % (self._user_obj.username, self._repo)

    def __repr__(self):
        return 'RepoObject(%r, %r)' % (self._user_obj, self._repo)

    def _set_attr(self, key, value):
        """Used to define an attribute to the repository."""
        self._set_attrs(**{key: value})

    def _set_attrs(self, **kwargs):
        """Used to define multiple attribute to a repository"""
        for key, value in kwargs.items():
            assert isinstance(key, str) and key.isalpha() and key.islower()
            self._user_obj._db.set_repo_attr(self._user_obj._username, self._repo, key, value)

    def _get_attr(self, key, default=None):
        assert isinstance(key, str)
        return self._user_obj._db.get_repo_attr(self._user_obj._username, self._repo, key, default)

    @property
    def name(self):
        return self._repo
    
    def _get_encoding(self):
        """Return the repository encoding in a normalized format (lowercase and replace - by _)."""
        # For backward compatibility, look into the database and fallback to
        # the rdiffweb config file in the repo.
        default = encodings.normalize_encoding(FS_ENCODING)
        encoding = self._get_attr('encoding')
        if encoding:
            return encodings.normalize_encoding(encoding.lower())
        conf_file = os.path.join(self._data_path, b'rdiffweb')
        if os.access(conf_file, os.F_OK) and os.path.isfile(conf_file):
            config = read_config(conf_file)
            return encodings.normalize_encoding(config.get('encoding', default))
        return default
        
    def _set_encoding(self, value):
        """Change the repository encoding"""
        # Validate if the value is a valid encoding before updating the database.
        codec = encodings.search_function(value)
        if not codec:
            raise ValueError(_('invalid encoding %s') % value)
        
        logger.info("updating repository %s encoding %s", self, codec.name)
        self._set_attr('encoding', codec.name)
        self._encoding = codec

    def delete(self):
        """Properly remove the given repository by updating the user's repositories."""
        repos = self._user_obj.repos
        repos.remove(self._repo)
        logger.info("deleting repository %s", self)
        RdiffRepo.delete(self)
        self._user_obj.repos = repos

    encoding = property(_get_encoding, _set_encoding)
    maxage = property(fget=lambda x: int(x._get_attr('maxage', default='0')), fset=lambda x, y: x._set_attr('maxage', int(y)))
    keepdays = property(fget=lambda x: int(x._get_attr('keepdays', default='-1')), fset=lambda x, y: x._set_attr('keepdays', int(y)))


class UserManager():
    """
    This class handle all user operation. This class is greatly inspired from
    TRAC account manager class.
    """
    
    _allow_add_user = BoolOption("AddMissingUser", False)

    def __init__(self, app):
        self.app = app
        self._database = SQLiteUserDB(app)
        self._password_stores = [LdapPasswordStore(app)]
        self._change_listeners = []
        
        # Register entry point.
        for entry_point in pkg_resources.iter_entry_points('rdiffweb.IUserChangeListener'):  # @UndefinedVariable
            cls = entry_point.load()
            # Creating the listener should register it self.But let make sure of it. 
            listener = cls(self.app)
            if listener not in self._change_listeners:
                self._change_listeners.append(listener)

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
        if self._database.exists(user):
            raise RdiffError(_("User %s already exists." % (user,)))
        # Find a database where to add the user
        logger.debug("adding new user [%s]", user)
        self._database.add_user(user, password)
        userobj = UserObject(self, self._database, user)
        self._notify('user_added', userobj, attrs)
        # Return user object
        return userobj

    def delete_user(self, user):
        """
        Delete the given user from password store.

        Return True if the user was deleted. Return False if the user didn't
        exists.
        """
        if hasattr(user, 'username'):
            user = user.username
        result = False
        # Delete user from database (required).
        if self._database.exists(user):
            logger.info("deleting user [%s] from database", user)
            result |= self._database.delete_user(user)
        if not result:
            return result
        self._notify('user_deleted', user)
        return True

    def exists(self, user):
        """
        Verify if the given user exists in our database.

        Return True if the user exists. False otherwise.
        """
        return self._database.exists(user)

    def get_user(self, user):
        """Return a user object."""
        if not self.exists(user):
            raise InvalidUserError(user)
        return UserObject(self, self._database, user)

    def list(self):
        """Search users database. Return a generator of user object."""
        # TODO Add criteria as required.
        for username in self._database.list():
            yield UserObject(self, self._database, username)

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
        # Validate the credentials
        logger.debug("validating user [%s] credentials", user)
        for store in self._password_stores + [self._database]:
            try:
                valid = store.are_valid_credentials(user, password)
                if valid:
                    break
            except:
                pass
        if not valid:
            return None
        # Get real username and external attributes.
        # Some password store provide extra attributes.
        if isinstance(valid, str):
            real_user, attrs = valid, None
        else:
            real_user, attrs = valid
        # Check if user exists in database
        try:
            userobj = self.get_user(real_user)
        except InvalidUserError:
            # Check if user may be added.
            if not self._allow_add_user:
                logger.info("user [%s] not found in database", real_user)
                return None
            # Create user
            userobj = self.add_user(real_user, attrs=attrs)
        self._notify('user_logined', userobj, attrs)
        return userobj

    def set_password(self, username, password, old_password=None):
        # Check if user exists in database
        if not self.exists(username):
            raise InvalidUserError(username)
        # Try to update the user password.
        for store in self._password_stores:
            try:
                valid = store.are_valid_credentials(username, old_password)
                if valid:
                    store.set_password(username, password, old_password)
                    return
            except:
                pass
        # Fallback to database
        self._database.set_password(username, password, old_password)
        self._notify('user_password_changed', username, password)

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
