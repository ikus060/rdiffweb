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
"""
LDAP UserDB backend used to validate credentials. This plugin will
use SQLite database for user's data. Both, LDAP and SQLite plugin must be
enabled.

The LDAP plugin cannot create new users. Users must already exist in the
LDAP directory. It would be difficult to create a new LDAP user, as the
creation of a LDAP user requires properties which are not made available
to the LDAP plugin.
"""

import ldap
import logging
import time

from rdiffweb.core import RdiffError
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.config import Option

logger = logging.getLogger(__name__)


class LdapPasswordStore():

    """Wrapper for LDAP authentication.

    This implementation assume the LDAP is using the system encoding."""

    uri = Option("ldap_uri")
    base_dn = Option("ldap_base_dn")
    scope = Option("ldap_scope")
    tls = Option("ldap_tls")
    attribute = Option("ldap_username_attribute")
    filter = Option("ldap_filter")
    require_group = Option("ldap_required_group")
    group_attribute = Option("ldap_group_attribute")
    group_attribute_is_dn = Option("ldap_group_attribute_is_dn")
    bind_dn = Option("ldap_bind_dn")
    bind_password = Option("ldap_bind_password")
    version = Option("ldap_version")
    network_timeout = Option("ldap_network_timeout")
    timeout = Option("ldap_timeout")
    encoding = Option("ldap_encoding")
    allow_password_change = Option("ldap_allow_password_change")
    check_shadow_expire = Option("ldap_check_shadow_expire")

    def __init__(self, app):
        self.app = app

    def are_valid_credentials(self, username, password):
        """Check if the given credential as valid according to LDAP."""
        assert isinstance(username, str)
        assert isinstance(password, str)
        # Skip validation if LdapUri is not provided
        if not self.uri:
            return False

        def check_crendential(l, r):
            # Check results
            # when the entire directory is searched, some null records are
            #  returned, so len(r) > 1 at all times
            # if, however, the first item returned is one of these, there will
            #  be no dn in the first record of the result set
            if not (r and r[0] and r[0][0]):
                logger.info("user [%s] not found in LDAP", username)
                return None

            # Bind using the user credentials. Throws an exception in case of
            # error.
            l.simple_bind_s(r[0][0], password)
            try:
                logger.info("user [%s] found in LDAP", username)

                # Verify the shadow expire
                if self.check_shadow_expire:
                    shadow_expire = self._attr_shadow_expire(r)
                    # Convert nb. days into seconds.
                    if shadow_expire and shadow_expire * 24 * 60 * 60 < time.time():
                        logger.warning("user account %s expired: %s", username, shadow_expire)
                        raise RdiffError(_('User account %s expired.' % username))

                # Get username
                dn = r[0][0]
                new_username = self._decode(r[0][1][self.attribute][0])

                # Verify if the user is member of the required group
                if self.require_group:
                    value = dn if self.group_attribute_is_dn else new_username
                    logger.info("check if user [%s] is member of [%s]", value, self.require_group)
                    if not l.compare_s(self.require_group, self.group_attribute, value):
                        raise RdiffError(_('Permissions denied for user account %s.' % username))
            finally:
                l.unbind_s()
            # Return the username
            return new_username, self._try_decode(r[0][1])

        # Execute the LDAP operation
        try:
            return self._execute(username, check_crendential)
        except Exception:
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

    def _try_decode(self, value):
        """
        Ldap attributes can be bytes, or lists of bytes.
        If the attribute is a list, loop through and run recursively
        If it is a byte, decode it
        """
        result = {}
        if isinstance(value, dict):
            for l in value:
                result[l] = self._try_decode(value[l])

            return result

        result = []
        if isinstance(value, list):
            for l in value:
                result.append(self._try_decode(l))

            return result

        if isinstance(value, bytes):
            try:
                # try to decode completely
                result = value.decode(encoding=self.encoding, errors='strict')
            except UnicodeDecodeError:
                # Sometimes, we can't decode bytes to str, so we'll replace the undecodable characters
                # with '?', and return that with a warning.
                result = value.decode(encoding=self.encoding, errors='replace')
                logger.warning("Unable to decode all of this: {}. Returning attempted decode: {}".format(
                    value, result))
            finally:
                return result

        # Not a list or bytes, return it as is
        return value

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

        # This tells the search not to follow referrals, and allows searching
        #  the entire directory as the base_dn
        l.set_option(ldap.OPT_REFERRALS, 0)

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

    def exists(self, username):
        """Check if the user exists in LDAP"""

        def check_user_exists(l, r):  # @UnusedVariable
            # Check the results
            if not (r and r[0] and r[0][0]):
                logger.debug("user [%s] not found", username)
                return False

            logger.debug("user [%s] found", username)
            return True

        # Execute the LDAP operation
        return self._execute(username, check_user_exists)

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
            logger.warning("authentication backend for user [%s] does not support changing the password", username)
            raise RdiffError(_("LDAP users are not allowed to change their password."))

        # Check if old_password id valid
        if old_password and not self.are_valid_credentials(username, old_password):
            raise RdiffError(_("Wrong password."))

        # Update the username password of the given user. If possible.
        return self._set_password_in_ldap(username, old_password, password)

    def _set_password_in_ldap(self, username, old_password, password):

        def change_passwd(l, r):
            if not (r and r[0] and r[0][0]):
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
