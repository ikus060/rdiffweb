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

from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_helpers import encode_s, decode_s
from rdiffweb.rdw_plugin import IPasswordStore
from rdiffweb.core import RdiffError

# Define the logger
logger = logging.getLogger(__name__)


class LdapPasswordStore(IPasswordStore):

    """Wrapper for LDAP authentication.

    This implementation assume the LDAP is using the system encoding."""

    def activate(self):
        """Called by the plugin manager to setup the plugin."""
        super(LdapPasswordStore, self).activate()

        # Get Ldap URI
        self.uri = self.app.cfg.get_config(
            "LdapUri", "")
        if not self.uri:
            raise "LdapUri must be define in configuration"
        # Check if TLs is enabled
        self.tls = self.app.cfg.get_config_bool(
            "LdapTls", "false")
        # Get Base DN
        self.base_dn = self.app.cfg.get_config(
            "LdapBaseDn", "")
        if not self.base_dn:
            raise "LdapBaseDn must be define in configuration"
        # Get attribute
        self.attribute = self.app.cfg.get_config(
            "LdapAttribute", "uid")
        # Get Scope
        self.scope = self.app.cfg.get_config(
            "LdapScope", "subtree")
        if self.scope == "base":
            self.scope = ldap.SCOPE_BASE
        elif self.scope == "onelevel":
            self.scope = ldap.SCOPE_ONELEVEL
        else:
            self.scope = ldap.SCOPE_SUBTREE
        # Filter
        self.filter = self.app.cfg.get_config(
            "LdapFilter", "(objectClass=*)")
        # Bind Dn
        self.bind_dn = self.app.cfg.get_config(
            "LdapBindDn", "")
        # Bind password
        self.bind_password = self.app.cfg.get_config(
            "LdapBindPassword", "")
        # Get Version
        self.version = self.app.cfg.get_config_int(
            "LdapVersion", "3")
        # Get Network timeout
        self.network_timeout = self.app.cfg.get_config_int(
            "LdapNetworkTimeout", "100")
        # Get Timeout
        self.timeout = self.app.cfg.get_config_int(
            "LdapTimeout", "300")
        # Check if password change are allowed.
        self.allow_password_change = self.app.cfg.get_config_bool(
            "LdapAllowPasswordChange", "false")

    def are_valid_credentials(self, username, password):
        """Check if the given credential as valid according to LDAP."""
        assert isinstance(username, unicode)
        assert isinstance(password, unicode)

        def check_crendential(l, r):
            # Check results
            if len(r) != 1:
                logger.debug("user [%s] not found in LDAP" % username)
                return None

            # Bind using the user credentials. Throws an exception in case of
            # error.
            l.simple_bind_s(r[0][0], encode_s(password))
            l.unbind_s()
            logger.info("user [%s] found in LDAP" % username)
            # Return the username
            return decode_s(r[0][1][self.attribute][0])

        # Execute the LDAP operation
        try:
            return self._execute(username, check_crendential)
        except:
            logger.exception("can't validate credentials")
            return False

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
            logger.debug("search ldap server: {}/{}?{}?{}?{}".format(
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
                raise RdiffError(e.message['desc'])
            raise RdiffError(unicode(repr(e)))

    def has_password(self, username):
        """Check if the user exists in LDAP"""

        def check_user_exists(l, r):  # @UnusedVariable
            # Check the results
            if len(r) != 1:
                logger.debug("user [%s] not found" % username)
                return False

            logger.debug("user [%s] found" % username)
            return True

        # Execute the LDAP operation
        return self._execute(username, check_user_exists)

    def get_email(self, username):
        """Get user mail."""
        logger.debug("get email for user [%s]" % username)
        value = self.get_user_attr(username, 'mail')
        if value:
            return value[0]
        return None

    def get_home_dir(self, username):
        """Get user home directory."""
        logger.debug("get email for user [%s]" % username)
        value = self.get_user_attr(username, 'homeDirectory')
        if isinstance(value, list):
            value = value[0]
        return value

    def get_user_attr(self, username, attr):
        """Get user attributes."""
        assert isinstance(username, unicode)

        def fetch_user_email(l, r):  # @UnusedVariable
            if len(r) != 1:
                logger.warn("user [%s] not found" % username)
                return ""
            if isinstance(attr, list):
                return dict([(x, r[0][1][x])
                             for x in attr
                             if x in r[0][1]])
            elif attr in r[0][1]:
                if isinstance(r[0][1][attr], list):
                    return [decode_s(x)
                            for x in r[0][1][attr]]
                else:
                    return decode_s(r[0][1][attr])
            return None

        # Execute the LDAP operation
        try:
            return self._execute(username, fetch_user_email)
        except:
            logger.exception("can't get user email")
            return ""

    def set_password(self, username, password, old_password=None):
        """Update the password of the given user."""
        assert isinstance(username, unicode)
        assert old_password is None or isinstance(old_password, unicode)
        assert isinstance(password, unicode)

        # Do nothing if password is empty
        if not password:
            raise ValueError(_("password can't be empty"))
        # Check if users are allowed to change their password in LDAP.
        if not self.allow_password_change:
            raise RdiffError(_("LDAP users are not allowed to change their password."))

        # Check if old_password id valid
        if old_password and not self.are_valid_credentials(username, old_password):
            raise ValueError(_("wrong password"))

        # Update the username password of the given user. If possible.
        return self._set_password_in_ldap(username, old_password, password)

    def _set_password_in_ldap(self, username, old_password, password):

        def change_passwd(l, r):
            if len(r) != 1:
                raise ValueError(_("user %s not found)" % (username,)))
            # Bind using the user credentials. Throws an exception in case of
            # error.
            if old_password is not None:
                l.simple_bind_s(r[0][0], encode_s(old_password))
            l.passwd_s(r[0][0], encode_s(old_password), encode_s(password))
            l.unbind_s()
            logger.info("password for user [%s] is updated in LDAP" % username)
            # User updated, return False
            return False

        # Execute the LDAP operation
        logger.debug("updating password for [%s] in LDAP" % username)
        return self._execute(username, change_passwd)

    def supports(self, operation):
        if operation == 'set_password':
            return self.allow_password_change
        return hasattr(self, operation)
