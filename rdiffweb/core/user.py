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

from builtins import str
import encodings
from io import open
import logging
import os

import pkg_resources

from future.utils import python_2_unicode_compatible
from future.utils.surrogateescape import encodefilename
from rdiffweb.core import RdiffError, authorizedkeys
from rdiffweb.core.config import BoolOption, read_config, Option
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.librdiff import RdiffRepo, DoesNotExistError, FS_ENCODING, \
    AccessDeniedError
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


def split_path(path):
    "Split the given path into <username> / <path>"
    # First part is the username
    assert path
    if isinstance(path, str):
        path = encodefilename(path)
    path = path.strip(b'/')
    if b'/' in path:
        username, path = path.split(b'/', 1)
        return username.decode('utf-8'), path
    else:
        return path.decode('utf-8'), b''


class IUserChangeListener():
    """
    A listener to receive user changes event.
    """

    def __init__(self, app):
        self.app = app
        self.app.userdb.add_change_listener(self)

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
        username, name = split_path(name)
        
        # Check if user has permissions to access this path
        if username != self._username and not self.is_admin:
            raise AccessDeniedError(name)
            
        name = normpath(name)
        for r in self._db.get_repos(username):
            if name == normpath(encodefilename(r)):
                user_obj = self if username == self._username else UserObject(self._userdb, self._db, username)
                return RepoObject(user_obj, r)
        raise DoesNotExistError(name)
    
    def get_repo_path(self, path):
        """
        Return a the repository identified by the given `path`.
        """
        username, path = split_path(path)

        # Check if user has permissions to access this path
        if username != self._username and not self.is_admin:
            raise AccessDeniedError(path)
            
        path = normpath(path)
        for r in self._db.get_repos(username):
            repo = normpath(encodefilename(r))
            if path.startswith(repo):     
                user_obj = self if username == self._username else UserObject(self._userdb, self._db, username)
                repo_obj = RepoObject(user_obj, r)
                path_obj = repo_obj.get_path(path[len(repo):])
                return (repo_obj, path_obj)
        raise DoesNotExistError(path)

    @property
    def is_ldap(self):
        """Return True if this user is an LDAP user. (with a password)"""
        return not self._db.get_password(self._username)

    def set_attr(self, key, value, notify=True):
        """Used to define an attribute"""
        self.set_attrs(**{key: value, 'notify': notify})

    def set_attrs(self, **kwargs):
        """Used to define multiple attributes at once."""
        notify = kwargs.pop('notify', True)
        for key, value in kwargs.items():
            assert key in ['is_admin', 'email', 'user_root', 'repos']
            setter = getattr(self._db, 'set_%s' % key)
            setter(self._username, value)
        # Call notification listener
        if notify:
            self._userdb._notify('user_attr_changed', self, kwargs)

    @property
    def disk_usage(self):
        
        # Check quota
        entry_point = next(pkg_resources.iter_entry_points('rdiffweb.IUserQuota'), None)  # @UndefinedVariable
        if entry_point:
            try:
                cls = entry_point.load()
                return cls(self._userdb.app).get_disk_usage(self)
            except:
                logger.warning('IuserQuota [%s] fail to run', entry_point, exc_info=1)
                return None
        else:
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
            for k in authorizedkeys.read(filename):
                yield k
        
        # Also look in database.
        for k in self._db.get_authorizedkeys(self._username):
            yield authorizedkeys.check_publickey(k)
        
    def add_authorizedkey(self, key, comment=None):
        """
        Add the given key to the user. Adding the key to his `authorized_keys`
        file if it exists and adding it to database.
        """
        # Parse and validate ssh key
        assert key
        key = authorizedkeys.check_publickey(key)
        if not key:
            raise ValueError(_("Invalid SSH key."))
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
                    raise ValueError(_("SSH key already exists"))
                logger.info("add key [%s] to [%s] authorized_keys", key, self.username)
                authorizedkeys.add(fh, key)
        else:
            # Also look in database.
            logger.info("add key [%s] to [%s] database", key, self.username)
            self._db.add_authorizedkey(
                self._username,
                fingerprint=key.fingerprint,
                key=key.getvalue())
        self._userdb._notify('user_attr_changed', self, {'authorizedkeys': True })
        
    def remove_authorizedkey(self, fingerprint):
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
            self._db.remove_authorizedkey(self._username, fingerprint)
        self._userdb._notify('user_attr_changed', self, {'authorizedkeys': True })

    # Declare properties
    is_admin = property(fget=lambda x: x._db.is_admin(x._username), fset=lambda x, y: x.set_attr('is_admin', y))
    email = property(fget=lambda x: x._db.get_email(x._username), fset=lambda x, y: x.set_attr('email', y))
    user_root = property(fget=lambda x: x._db.get_user_root(x._username), fset=lambda x, y: x.set_attr('user_root', y))
    repos = property(fget=lambda x: [r.strip('/') for r in x._db.get_repos(x._username)], fset=lambda x, y: x.set_attr('repos', y))
    authorizedkeys = property(fget=lambda x: x.get_authorizedkeys())
    repo_objs = property(fget=lambda x: [RepoObject(x, r) for r in x._db.get_repos(x._username)])
    disk_quota = property(get_disk_quota, set_disk_quota)
    

@python_2_unicode_compatible
class RepoObject(RdiffRepo):
    """Represent a repository."""

    def __init__(self, user_obj, repo):
        assert isinstance(repo, str)
        self._repo = repo
        self._user_obj = user_obj
        self._username = self._user_obj._username
        RdiffRepo.__init__(self, user_obj.user_root, repo)
        self._encoding = self._get_encoding()

    def __eq__(self, other):
        return (isinstance(other, RepoObject) and
                self._username == other._username and
                self._repo == other._repo)

    def __str__(self):
        return 'RepoObject[%s, %s]' % (self._username, self._repo)

    def _set_attr(self, key, value):
        """Used to define an attribute to the repository."""
        self._set_attrs(**{key: value})

    def _set_attrs(self, **kwargs):
        """Used to define multiple attribute to a repository"""
        for key, value in kwargs.items():
            assert isinstance(key, str) and key.isalpha() and key.islower()
            self._user_obj._db.set_repo_attr(self._username, self._repo, key, value)

    def _get_attr(self, key, default=None):
        assert isinstance(key, str)
        return self._user_obj._db.get_repo_attr(self._username, self._repo, key, default)

    @property
    def name(self):
        return self._repo.strip('/')
    
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
                os.remove(conf_file)
                encoding = config.get('encoding')
                if encoding:
                    return encodings.search_function(encoding)
        except:
            logger.exception("fail to get repo encoding from file")
        
        # Fallback to default encoding.
        return encodings.search_function(FS_ENCODING)
        
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
        self._user_obj._db.delete_repo(self._user_obj._username, self._repo)
        RdiffRepo.delete(self)        

    encoding = property(lambda x: x._encoding.name, _set_encoding)
    maxage = property(fget=lambda x: int(x._get_attr('maxage', default='0')), fset=lambda x, y: x._set_attr('maxage', int(y)))
    keepdays = property(fget=lambda x: int(x._get_attr('keepdays', default='-1')), fset=lambda x, y: x._set_attr('keepdays', int(y)))


class UserManager():
    """
    This class handle all user operation. This class is greatly inspired from
    TRAC account manager class.
    """
    
    _db_file = Option("SQLiteDBFile", "/etc/rdiffweb/rdw.db")
    _allow_add_user = BoolOption("AddMissingUser", False)
    _admin_user = Option("AdminUser", "admin")

    def __init__(self, app):
        self.app = app
        self._database = SQLiteUserDB(self._db_file)
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
        
        # Check if admin user exists. If not, created it.
        if not self.exists(self._admin_user):
            userobj = self.add_user(self._admin_user, 'admin123')
            userobj.is_admin = True

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
            
        if user == self._admin_user:
            raise ValueError(_("can't delete admin user"))
            
        # Delete user from database (required).
        logger.info("deleting user [%s] from database", user)
        self._database.delete_user(user)
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
            return None
        return UserObject(self, self._database, user)

    def users(self, search=None, criteria=None):
        """
        Search users database. Return a generator of user object.
        
        search: Define a search term to look into email or username.
        criteria: Define a search filter: admins, ldap
        """
        # TODO Add criteria as required.
        for username in self._database.users(search, criteria):
            yield UserObject(self, self._database, username)

    def repos(self, search=None, criteria=None):
        """
        Quick listing of all the repository object for all user.
        
        search: Define a search term to look into path, email or username.
        criteria: Define a search filter: ok, failed, interrupted, in_progress
        """
        for username, repo in self._database.repos(search, criteria):
            user_obj = UserObject(self, self._database, username)
            repo_obj = RepoObject(user_obj, repo)
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
        # Validate the credentials
        logger.debug("validating user [%s] credentials", user)
        for store in [self._database] + self._password_stores:
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
        userobj = self.get_user(real_user)
        if not userobj:
            if self._allow_add_user:
                # Create user
                userobj = self.add_user(real_user, attrs=attrs)
            else:
                logger.info("user [%s] not found in database", real_user)
                return None
        self._notify('user_logined', userobj, attrs)
        return userobj

    def set_password(self, username, password, old_password=None):
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
