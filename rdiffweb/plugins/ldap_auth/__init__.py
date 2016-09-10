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
"""
LDAP UserDB backend used to validate credentials. This plugin will
use SQLite database for user's data. Both, LDAP and SQLite plugin must be
enabled.

The LDAP plugin cannot create new users. Users must already exist in the
LDAP directory. It would be difficult to create a new LDAP user, as the
creation of a LDAP user requires properties which are not made available
to the LDAP plugin.
"""
# Define the logger

from __future__ import unicode_literals

from builtins import bytes
from builtins import str
import ldap
import logging
import time

from rdiffweb.core import RdiffError
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_config import Option, BoolOption, IntOption
from rdiffweb.rdw_plugin import IPasswordStore


logger = logging.getLogger(__name__)


class LdapPasswordStore(IPasswordStore):

    """Wrapper for LDAP authentication.

    This implementation assume the LDAP is using the system encoding."""

    uri = Option("LdapUri", doc="Get Ldap URI")
    base_dn = Option("LdapBaseDn", "", doc="Get Base DN")
    scope = Option("LdapScope", "subtree")
    tls = BoolOption("LdapTls", "false", doc="Check if TLs is enabled")
    attribute = Option("LdapAttribute", "uid", doc="Get attribute")
    filter = Option("LdapFilter", "(objectClass=*)")
    bind_dn = Option("LdapBindDn", "")
    bind_password = Option("LdapBindPassword", "")
    version = IntOption("LdapVersion", "3")
    network_timeout = IntOption("LdapNetworkTimeout", "100")
    timeout = IntOption("LdapTimeout", "300")
    encoding = Option("LdapEncoding", "utf-8", doc="Get default LdapEncoding")
    allow_password_change = BoolOption("LdapAllowPasswordChange", "false", doc="Check if password change are allowed.")
    check_shadow_expire = BoolOption("LdapCheckShadowExpire", "false", doc="Enable verification of Shadow Expire.")

    def activate(self):
        """Called by the plugin manager to setup the plugin."""
        super(IPasswordStore, self).activate()

    def are_valid_credentials(self, username, password):
        """Check if the given credential as valid according to LDAP."""
        assert isinstance(username, str)
        assert isinstance(password, str)

        def check_crendential(l, r):
            # Check results
            if len(r) != 1:
                logger.debug("user [%s] not found in LDAP", username)
                return None

            # Bind using the user credentials. Throws an exception in case of
            # error.
            l.simple_bind_s(r[0][0], password)
            l.unbind_s()
            logger.info("user [%s] found in LDAP", username)

            # Verify the shadow expire
            shadow_expire = self._attr_shadow_expire(r)
            if self.check_shadow_expire and shadow_expire:
                # Convert nb. days into seconds.
                shadow_expire = shadow_expire * 24 * 60 * 60
                if shadow_expire < time.time():
                    logger.warn("user account %s expired: %s", username, shadow_expire)
                    raise RdiffError(_('User account %s expired.' % username))

            # Return the username
            return self._decode(r[0][1][self.attribute][0])

        # Execute the LDAP operation
        try:
            return self._execute(username, check_crendential)
        except:
            logger.exception("can't validate user [%s] credentials", username)
            return False

    def _attr(self, r, attr):
        if isinstance(attr, list):
            return dict([(x, r[0][1][x])
                         for x in attr
                         if x in r[0][1]])
        elif attr in r[0][1]:
            if isinstance(r[0][1][attr], list):
                return [self._decode(x)
                        for x in r[0][1][attr]]
            else:
                return self._decode(r[0][1][attr])
        return None

    def _attr_shadow_expire(self, r):
        """Get Shadow Expire value from `r`."""
        # get Shadow expire value
        shadow_expire = self._attr(r, 'shadowExpire')
        if not shadow_expire:
            return None
        if isinstance(shadow_expire, list):
            shadow_expire = shadow_expire[0]
        return int(shadow_expire)

    def _decode(self, value):
        """If required, decode the given bytes str into unicode."""
        if isinstance(value, bytes):
            value = value.decode(encoding=self.encoding)
        return value

    def _execute(self, username, function):
        assert isinstance(username, str)

        """Reusable method to run LDAP operation."""

        assert self.uri, "LdapUri must be define in configuration"
        assert self.base_dn, "LdapBaseDn must be define in configuration"
        if self.scope == "base":
            scope = ldap.SCOPE_BASE
        elif self.scope == "onelevel":
            scope = ldap.SCOPE_ONELEVEL
        else:
            scope = ldap.SCOPE_SUBTREE

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
                self.uri, self.base_dn, self.attribute, scope,
                search_filter))
            r = l.search_s(self.base_dn, scope, search_filter)

            # Execute operation
            return function(l, r)
        except ldap.LDAPError as e:
            l.unbind_s()
            # Handle the LDAP exception and build a nice user message.
            logger.warning('ldap error', exc_info=1)
            msg = _("An LDAP error occurred: %s")
            ldap_msg = str(e)
            if hasattr(e, 'message') and isinstance(e.message, dict):
                if 'desc' in e.message:
                    ldap_msg = e.message['desc']
                if 'info' in e.message:
                    ldap_msg = e.message['info']
            raise RdiffError(msg % ldap_msg)

    def has_password(self, username):
        """Check if the user exists in LDAP"""

        def check_user_exists(l, r):  # @UnusedVariable
            # Check the results
            if len(r) != 1:
                logger.debug("user [%s] not found", username)
                return False

            logger.debug("user [%s] found", username)
            return True

        # Execute the LDAP operation
        return self._execute(username, check_user_exists)

    def get_email(self, username):
        """Get user mail."""
        logger.debug("get email for user [%s]", username)
        value = self.get_user_attr(username, 'mail')
        if value:
            return value[0]
        return None

    def get_home_dir(self, username):
        """Get user home directory."""
        logger.debug("get email for user [%s]", username)
        value = self.get_user_attr(username, 'homeDirectory')
        if isinstance(value, list):
            value = value[0]
        return value

    def get_user_attr(self, username, attr):
        """Get user attributes."""
        assert isinstance(username, str)

        def fetch_user_email(l, r):  # @UnusedVariable
            if len(r) != 1:
                logger.warning("user [%s] not found", username)
                return ""
            return self._attr(r, attr)

        # Execute the LDAP operation
        try:
            return self._execute(username, fetch_user_email)
        except:
            logger.exception("can't get user email")
            return ""

    def set_password(self, username, password, old_password=None):
        """Update the password of the given user."""
        assert isinstance(username, str)
        assert old_password is None or isinstance(old_password, str)
        assert isinstance(password, str)

        # Do nothing if password is empty
        if not password:
            raise RdiffError(_("Password can't be empty."))
        # Check if users are allowed to change their password in LDAP.
        if not self.allow_password_change:
            raise RdiffError(_("LDAP users are not allowed to change their password."))

        # Check if old_password id valid
        if old_password and not self.are_valid_credentials(username, old_password):
            raise RdiffError(_("Wrong password."))

        # Update the username password of the given user. If possible.
        return self._set_password_in_ldap(username, old_password, password)

    def _set_password_in_ldap(self, username, old_password, password):

        def change_passwd(l, r):
            if len(r) != 1:
                raise RdiffError(_("User %s not found." % (username,)))
            # Bind using the user credentials. Throws an exception in case of
            # error.
            if old_password is not None:
                l.simple_bind_s(r[0][0], old_password)
            l.passwd_s(r[0][0], old_password, password)
            l.unbind_s()
            logger.info("password for user [%s] is updated in LDAP", username)
            # User updated, return False
            return False

        # Execute the LDAP operation
        logger.debug("updating password for [%s] in LDAP", username)
        return self._execute(username, change_passwd)

    def supports(self, operation):
        if operation == 'set_password':
            return self.allow_password_change
        return hasattr(self, operation)
