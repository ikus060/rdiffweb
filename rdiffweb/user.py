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

import logging

from rdiffweb.core import RdiffError, Component, InvalidUserError
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_plugin import IPasswordStore, IDatabase, IUserChangeListener

# Define the logger
logger = logging.getLogger(__name__)


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
        return [x.plugin_object
                for x in self.app.plugins.get_plugins_of_category(IDatabase.CATEGORY)]

    @property
    def _change_listeners(self):
        """Return list of IUserChangeListener"""
        return [x.plugin_object
                for x in self.app.plugins.get_plugins_of_category(IUserChangeListener.CATEGORY)]

    @property
    def _password_stores(self):
        """Return all configured password store."""
        return [x.plugin_object
                for x in self.app.plugins.get_plugins_of_category(IPasswordStore.CATEGORY)]

    def add_user(self, user, password=None):
        """
        Used to add a new user with an optional password.
        """
        assert password is None or isinstance(password, unicode)
        # Check if user already exists.
        db = self.find_user_database(user)
        if db:
            raise ValueError(_("user %s already exists" % (user,)))
        # Find a database where to add the user
        db = self._get_supporting_database('add_user')
        logger.info("adding new user [%s] to database [%s]", user, db)
        db.add_user(user)
        self._notify('added', user, password)
        # Find a password store where to set password
        if password:
            # Check if database support set password, otherwise try to set password as usual.
            if hasattr(db, 'set_password'):
                db.set_password(user, password)
            else:
                self.set_password(user, password)

    def delete_user(self, user):
        """
        Delete the given user from password store.

        Return True if the user was deleted. Return False if the user didn't
        exists.
        """
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
        assert isinstance(user, unicode)
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
        assert isinstance(user, unicode)
        for db in self._databases:
            if db.exists(user):
                return db
        return None

    def get_email(self, user):
        """Return the user email. Return the first email found."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        return db.get_email(user)

    def is_admin(self, user):
        """Return True if the user is Admin."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        return db.is_admin(user)

    def get_repos(self, user):
        """Get list of repos for the given `user`."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        return db.get_repos(user)

    def get_repo_maxage(self, user, repo_path):
        """Return the max age of the given repo."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        return db.get_repo_maxage(user, repo_path)

    def get_user_root(self, user):
        """Get user root directory."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        return db.get_user_root(user)

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
        """List all users from databases."""
        users = []
        for store in self._databases:
            users.extend(store.list())
        return users

    def login(self, user, password):
        """
        Called to authenticate the given user.

        Check if the credentials are valid. Then may actually add the user
        in database if allowed.

        If valid, return the username. Return False if the user exists but the
        password doesn't matches. Return None if the user was not found in any
        password store.
        The return value may not be equals to the given username.
        """
        assert isinstance(user, unicode)
        assert password is None or isinstance(user, unicode)
        # Validate the credentials
        logger.info("validating user [%s] credentials", user)
        real_user = False
        for store in self._password_stores:
            real_user = store.are_valid_credentials(user, password)
            if real_user:
                break
        if not real_user:
            self._notify('logined', user, password)
            return real_user
        # Check if user exists in database
        if self.exists(real_user):
            return real_user
        # Check if user may be added.
        if not self._allow_add_user:
            logger.info("user [%s] not found in database", real_user)
            return None
        # Create user
        self.add_user(real_user)
        self._notify('logined', user, password)
        return real_user

    def set_email(self, user, email):
        """Sets the given user email."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        db.set_email(user, email)

    def set_is_admin(self, user, is_admin):
        """Sets the user root directory."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        db.set_is_admin(user, is_admin)

    def set_user_root(self, user, user_root):
        """Sets the user root directory."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        db.set_user_root(user, user_root)

    def set_password(self, user, password, old_password=None):
        # Check if user exists in database
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        # Try to update the user password.
        store = self.find_user_store(user)
        if store and not store.supports('set_password'):
            raise RdiffError(_("""The authentication backend for user %s does
            not support setting the password""" % user))
        elif not store:
            store = self._get_supporting_store('set_password')
        if not store:
            raise RdiffError(_("none of the IPasswordStore supports setting the password"))
        store.set_password(user, password, old_password)
        self._notify('password_changed', user, password)

    def set_repos(self, user, repo_paths):
        """Sets the list of repos for the given user."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        db.set_repos(user, repo_paths)

    def set_repo_maxage(self, user, repo_path, max_age):
        """Sets the max age for the given repo."""
        db = self.find_user_database(user)
        if not db:
            raise InvalidUserError(user)
        db.set_repo_maxage(user, repo_path, max_age)

    def supports(self, operation, user=None):
        """
        Check if the users password store or user database supports the given operation.
        """
        assert isinstance(operation, unicode)
        assert user is None or isinstance(user, unicode)

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
                logger.debug('call [%s] [%s]' % (listener.__class__.__name__, mod))
                getattr(listener, mod)(*args)
            except:
                logger.warn(
                    'IUserChangeListener [%s] fail to run [%s]'
                    % (listener.__class__.__name__, mod), exc_info=1)
