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

import ldap
import logging

from rdiffweb.rdw_helpers import encode_s
from rdiffweb.rdw_plugin import IUserDBPlugin
from rdiffweb.rdw_app import RdiffwebApp

# Define the logger
logger = logging.getLogger(__name__)


class LdapUserDB(IUserDBPlugin):

    """Wrapper for LDAP authentication.

    This implementation assume the LDAP is using the system encoding."""

    def activate(self):
        """Called by the plugin manager to setup the plugin."""
        IUserDBPlugin.activate(self)

        # Get Ldap URI
        self.uri = self.app.config.get_config(
            "LdapUri", "")
        if not self.uri:
            raise "LdapUri must be define in configuration"
        # Check if TLs is enabled
        self.tls = self.app.config.get_config_bool(
            "LdapTls", "false")
        # Get Base DN
        self.base_dn = self.app.config.get_config(
            "LdapBaseDn", "")
        if not self.base_dn:
            raise "LdapBaseDn must be define in configuration"
        # Get attribute
        self.attribute = self.app.config.get_config(
            "LdapAttribute", "uid")
        # Get Scope
        self.scope = self.app.config.get_config(
            "LdapScope", "subtree")
        if self.scope == "base":
            self.scope = ldap.SCOPE_BASE
        elif self.scope == "onelevel":
            self.scope = ldap.SCOPE_ONELEVEL
        else:
            self.scope = ldap.SCOPE_SUBTREE
        # Filter
        self.filter = self.app.config.get_config(
            "LdapFilter", "(objectClass=*)")
        # Bind Dn
        self.bind_dn = self.app.config.get_config(
            "LdapBindDn", "")
        # Bind password
        self.bind_password = self.app.config.get_config(
            "LdapBindPassword", "")
        # Get Version
        self.version = self.app.config.get_config_int(
            "LdapVersion", "3")
        # Get Network timeout
        self.network_timeout = self.app.config.get_config_int(
            "LdapNetworkTimeout", "100")
        # Get Timeout
        self.timeout = self.app.config.get_config_int(
            "LdapTimeout", "300")
        # Check if password change are allowed.
        self.allow_password_change = self.app.config.get_config_bool(
            "LdapAllowPasswordChange", "false")

        # Plugins system doesn't allow direct access to plugin via "import".
        # So we need to get reference to the plugin via the plugin manager.
        sqlite_plugin = self.app.plugins.get_plugin_by_name("SQLite", "UserDB")
        if sqlite_plugin is None:
            raise ValueError("cannot find SQLite plugin.")
        self.delegate = sqlite_plugin.plugin_object

    def are_valid_credentials(self, username, password):
        """Check if the given credential as valid according to LDAP."""
        assert isinstance(username, unicode)
        assert isinstance(password, unicode)

        # Check with local database first.
        if self.delegate.are_valid_credentials(username, password):
            logger.debug(("valid credentials for [%s]" +
                         "according to local database") % username)
            return True

        # Check if exists exists
        if not self.delegate.exists(username):
            logger.debug("user [%s] doesn't exists in local database" % username)
            return False

        def check_crendential(l, r):
            # Check results
            if len(r) != 1:
                logger.warn("user [%s] not found in LDAP" % username)
                return False

            # Bind using the user credentials. Throws an exception in case of
            # error.
            l.simple_bind_s(r[0][0], encode_s(password))
            l.unbind_s()
            logger.info("user [%s] found in LDAP" % username)
            return True

        # Execute the LDAP operation
        try:
            return self._execute(username, check_crendential)
        except:
            logger.exception("can't validate credentials")
            return False

    def add_user(self, username):
        # Then add it to internal database.
        return self.delegate.add_user(username)

    def delete_user(self, username):
        # Only delete eser from internal database.
        return self.delegate.delete_user(username)

    def _execute(self, username, function):
        assert isinstance(username, unicode)

        """Reusable method to run LDAP operation."""

        # try STARTLS if configured
        if self.tls:
            ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

        # Check LDAP credential only.
        l = ldap.initialize(self.uri)

        # Set v2 or v3
        if self.version == 2:
            l.protocol_version = ldap.VERSION2
        else:
            l.protocol_version = ldap.VERSION3

        try:
            # Bind to the LDAP server
            logger.debug("binding to ldap server {}".format(self.uri))
            l.simple_bind_s(self.bind_dn, self.bind_password)

            # Search the LDAP server
            search_filter = "(&{}({}={}))".format(
                self.filter, self.attribute, username)
            logger.info("search ldap server: {}/{}?{}?{}?{}".format(
                self.uri, self.base_dn, self.attribute, self.scope,
                search_filter))
            r = l.search_s(encode_s(self.base_dn),
                           self.scope,
                           encode_s(search_filter))

            # Execute operation
            return function(l, r)
        except ldap.LDAPError as e:
            l.unbind_s()
            if isinstance(e.message, dict) and 'desc' in e.message:
                raise ValueError(e.message['desc'])
            else:
                raise ValueError(e.message['info'])

    def exists(self, username):
        return self.delegate.exists(username)

    def _exists_in_ldap(self, username):
        """Check if the user exists in LDAP"""

        def check_user_exists(l, r):
            # Check the results
            if len(r) != 1:
                logger.warn("user [%s] not found" % username)
                return False

            logger.info("user [%s] found" % username)
            return True

        # Execute the LDAP operation
        return self._execute(username, check_user_exists)

    def get_email(self, username):
        assert isinstance(username, unicode)

        # Get email from local database.
        email = self.delegate.get_email(username)
        if email:
            return email
        # Get from LDAP
        logger.debug("get email for user [%s]" % username)
        return self._get_email_from_ldap(username)

    def _get_email_from_ldap(self, username):
        """Query LDAP server for email."""

        def fetch_user_email(l, r):
            if len(r) != 1:
                logger.warn("user [%s] not found" % username)
                return ""
            if 'mail' in r[0][1] and len(r[0][1]['mail']) > 0:
                return r[0][1]['mail'][0]
            return ""

        # Execute the LDAP operation
        try:
            return self._execute(username, fetch_user_email)
        except:
            logger.exception("can't get user email")
            return ""

    def get_root_dir(self, username):
        return self.delegate.get_root_dir(username)

    def get_repos(self, username):
        return self.delegate.get_repos(username)

    def get_repo_maxage(self, username, repoPath):
        return self.delegate.get_repo_maxage(username, repoPath)

    def list(self):
        return self.delegate.list()

    def is_admin(self, username):
        return self.delegate.is_admin(username)

    def is_ldap(self):
        return True

    def is_modifiable(self):
        return True

    def set_email(self, username, userEmail):
        return self.delegate.set_email(username, userEmail)

    def set_info(self, username, userRoot, isAdmin):
        return self.delegate.set_info(username, userRoot, isAdmin)

    def set_password(self, username, old_password, password):
        """Update the password of the given user."""
        assert isinstance(username, unicode)
        assert old_password is None or isinstance(old_password, unicode)
        assert isinstance(password, unicode)

        # Check if the user is in LDAP.
        if self._exists_in_ldap(username):
            # Do nothing if password is empty
            if not password:
                return
            # Check if users are allowed to change their password in LDAP.
            if not self.allow_password_change:
                raise ValueError("""LDAP users are not allowed to change their
                                 password with rdiffweb.""")
            # Update the username password of the given user. If possible.
            return self._set_password_in_ldap(username, old_password, password)
        else:
            return self.delegate.set_password(username, old_password, password)

    def _set_password_in_ldap(self, username, old_password, password):

        def check_user_exists(l, r):
            if len(r) != 1:
                raise ValueError("user [%s] not found" % username)
            # Bind using the user credentials. Throws an exception in case of
            # error.
            l.simple_bind_s(r[0][0], encode_s(old_password))
            l.passwd_s(r[0][0], encode_s(old_password), encode_s(password))
            l.unbind_s()
            logger.info("password for user [%s] is updated in LDAP" % username)

        # Execute the LDAP operation
        logger.debug("updating password for [%s] in LDAP" % username)
        return self._execute(username, check_user_exists)

    def set_repos(self, username, repoPaths):
        return self.delegate.set_repos(username, repoPaths)

    def set_repo_maxage(self, username, repoPath, maxAge):
        return self.delegate.set_repo_maxage(username, repoPath, maxAge)
