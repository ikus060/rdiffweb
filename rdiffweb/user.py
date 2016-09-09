#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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
from future.utils import python_2_unicode_compatible
from future.utils.surrogateescape import encodefilename
import logging

from rdiffweb.core import Component, InvalidUserError, RdiffError
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_plugin import IPasswordStore, IDatabase, IUserChangeListener
from rdiffweb.page_main import normpath


# Define the logger
logger = logging.getLogger(__name__)


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
        for r in self._db.get_repos(self._username):
            if name == normpath(encodefilename(r)):
                return RepoObject(self._db, self._username, r)
        raise KeyError(name)

    def set_attr(self, key, value, notify=True):
        """Used to define an attribute"""
        self.set_attrs(**{key: value, 'notify': notify})

    def set_attrs(self, **kwargs):
        """Used to define multiple attributes at once."""
        for key, value in kwargs.items():
            if key in ['is_admin', 'email', 'user_root', 'repos']:
                setter = getattr(self._db, 'set_%s' % key)
                setter(self._username, value)
        # Call notification listener
        if kwargs.get('notify', True):
            del kwargs['notify']
            self._userdb._notify('attr_changed', self._username, kwargs)

    # Declare properties
    is_admin = property(fget=lambda x: x._db.is_admin(x._username), fset=lambda x, y: x.set_attr('is_admin', y))
    email = property(fget=lambda x: x._db.get_email(x._username), fset=lambda x, y: x.set_attr('email', y))
    user_root = property(fget=lambda x: x._db.get_user_root(x._username), fset=lambda x, y: x.set_attr('user_root', y))
    repos = property(fget=lambda x: x._db.get_repos(x._username), fset=lambda x, y: x.set_attr('repos', y))
    repo_list = property(fget=lambda x: [RepoObject(x._db, x._username, r)
                                         for r in x._db.get_repos(x._username)])


@python_2_unicode_compatible
class RepoObject(object):
    """Represent a repository."""

    def __init__(self, db, username, repo):
        self._db = db
        self._username = username
        self._repo = repo

    def __eq__(self, other):
        return (isinstance(other, RepoObject) and
                self._username == other._username and
                self._repo == other._repo and
                self._db == other._db)

    def __str__(self):
        return 'RepoObject[%s]' % self._username

    def __repr__(self):
        return 'RepoObject(db, %r, %r)' % (self._username, self._repo)

    def set_attr(self, key, value):
        """Used to define an attribute to the repository."""
        self.set_attrs(**{key: value})

    def set_attrs(self, **kwargs):
        """Used to define multiple attribute to a repository"""
        for key, value in kwargs.items():
            assert isinstance(key, str) and key.isalpha() and key.islower()
            self._db.set_repo_attr(self._username, self._repo, key, value)

    def get_attr(self, key, default=None):
        assert isinstance(key, str)
        return self._db.get_repo_attr(self._username, self._repo, key, default)

    @property
    def name(self):
        return self._repo

    maxage = property(fget=lambda x: x._db.get_repo_maxage(x._username, x._repo), fset=lambda x, y: x._db.set_repo_maxage(x._username, x._repo, y))


class UserManager(Component):
    """
    This class handle all user operation. This class is greatly inspired from
    TRAC account manager class.
    """

    def __init__(self, app):
        Component.__init__(self, app)

    @property
    def _allow_add_user(self):
        return self.app.cfg.get_config_bool("AddMissingUser", "false")

    @property
    def _databases(self):
        """Return all configured database."""
        return self.app.plugins.get_plugins_of_category(IDatabase.CATEGORY)

    @property
    def _change_listeners(self):
        """Return list of IUserChangeListener"""
        return self.app.plugins.get_plugins_of_category(IUserChangeListener.CATEGORY)

    @property
    def _password_stores(self):
        """Return all configured password store."""
        return self.app.plugins.get_plugins_of_category(IPasswordStore.CATEGORY)

    def add_user(self, user, password=None):
        """
        Used to add a new user with an optional password.
        """
        assert password is None or isinstance(password, str)
        # Check if user already exists.
        db = self.find_user_database(user)
        if db:
            raise RdiffError(_("User %s already exists." % (user,)))
        # Find a database where to add the user
        db = self._get_supporting_database('add_user')
        logger.debug("adding new user [%s] to database [%s]", user, db)
        db.add_user(user)
        self._notify('added', user, password)
        # Find a password store where to set password
        if password:
            # Check if database support set password, otherwise try to set password as usual.
            if hasattr(db, 'set_password'):
                db.set_password(user, password)
            else:
                self.set_password(user, password)

        # Return user object
        return UserObject(self, db, user)

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
        db = self.find_user_database(user)
        if db:
            logger.info("deleting user [%s] from database [%s]", user, db)
            result |= db.delete_user(user)
        if not result:
            return result
        # Delete credentials from password store (optional).
        store = self.find_user_store(user)
        if hasattr(store, 'delete_user'):
            logger.info("deleting user [%s] from password store [%s]", user, store)
            result |= store.delete_user(user)
        self._notify('deleted', user)
        return True

    def exists(self, user):
        """
        Verify if the given user exists in our database.

        Return True if the user exists. False otherwise.
        """
        return self.find_user_database(user) is not None

    def find_user_store(self, user):
        """
        Locates which store contains the user specified.

        If the user isn't found in any IPasswordStore in the chain, None is
        returned.
        """
        assert isinstance(user, str)
        for store in self._password_stores:
            if store.has_password(user):
                return store
        return None

    def find_user_database(self, user):
        """
        Locates which database contains the user specified.

        If the user isn't found in any IDatabase in the chain, None is
        returned.
        """
        assert isinstance(user, str)
        for db in self._databases:
            if db.exists(user):
                return db
        return None

    def get_user(self, username):
        """Return a user object."""
        db = self.find_user_database(username)
        if not db:
            raise InvalidUserError(username)
        return UserObject(self, db, username)

    def _get_supporting_store(self, operation):
        """
        Returns the IPasswordStore that implements the specified operation.

        None is returned if no supporting store can be found.
        """
        for store in self._password_stores:
            if store.supports(operation):
                return store
        return None

    def _get_supporting_database(self, operation):
        """
        Returns the IDatabase that implements the specified operation.

        None is returned if no supporting store can be found.
        """
        for db in self._databases:
            if db.supports(operation):
                return db
        return None

    def list(self):
        """Search users database. Return a generator of user object."""
        # TODO Add criteria as required.
        for db in self._databases:
            for username in db.list():
                yield UserObject(self, db, username)

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
        real_user = False
        for store in self._password_stores:
            real_user = store.are_valid_credentials(user, password)
            if real_user:
                break
        if not real_user:
            return None
        # Check if user exists in database
        try:
            userobj = self.get_user(real_user)
            self._notify('logined', real_user, password)
            return userobj
        except InvalidUserError:
            # Check if user may be added.
            if not self._allow_add_user:
                logger.info("user [%s] not found in database", real_user)
                return None
            # Create user
            userobj = self.add_user(real_user)
            self._notify('logined', real_user, password)
            return userobj

    def set_password(self, user, password, old_password=None):
        # Check if user exists in database
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        # Try to update the user password.
        store = self.find_user_store(user)
        if store and not store.supports('set_password'):
            logger.warn("authentication backend for user [%s] does not support changing the password", user)
            raise RdiffError(_("You cannot change the user's password."))
        elif not store:
            store = self._get_supporting_store('set_password')
        if not store:
            logger.warn("none of the IPasswordStore supports setting the password")
            raise RdiffError(_("You cannot change the user's password."))
        store.set_password(user, password, old_password)
        self._notify('password_changed', user, password)

    def supports(self, operation, user=None):
        """
        Check if the users password store or user database supports the given operation.
        """
        assert isinstance(operation, str)
        assert user is None or isinstance(user, str)

        if user:
            if operation in ['set_password']:
                store = self.find_user_store(user)
                return store is not None and store.supports(operation)
            else:
                db = self.find_user_database(user)
                return db is not None and db.supports(operation)
        else:
            if operation in ['set_password']:
                return self._get_supporting_store(operation) is not None
            else:
                return self._get_supporting_database(operation) is not None

    def _notify(self, mod, *args):
        mod = '_'.join(['user', mod])
        for listener in self._change_listeners:
            # Support divergent account change listener implementations too.
            try:
                logger.debug('call [%s] [%s]', listener.__class__.__name__, mod)
                getattr(listener, mod)(*args)
            except:
                logger.warning(
                    'IUserChangeListener [%s] fail to run [%s]',
                    listener.__class__.__name__, mod, exc_info=1)
