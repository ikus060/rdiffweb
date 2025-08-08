# LDAP Plugins for cherrypy
# # Copyright (C) 2025 IKUS Software
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

import cherrypy
import ldap3
from cherrypy.process.plugins import SimplePlugin
from ldap3.core.exceptions import LDAPException, LDAPInvalidCredentialsResult

logger = logging.getLogger(__name__)

_safe = ldap3.utils.conv.escape_filter_chars


def all_attribute(attributes, keys, default=None):
    """
    Extract the all value from LDAP attributes.
    """
    # Skip loopkup if key is not defined.
    if not keys:
        return default
    # Convert key to a list.
    keys = keys if isinstance(keys, list) else [keys]
    # Loop on each attribute name.
    values = []
    for attr in keys:
        try:
            value = attributes[attr]
            if isinstance(value, list) and len(value) > 0:
                values.append(value[0])
            else:
                values.append(value)
        except KeyError:
            pass
    # Default to None.
    return values if values else default


def first_attribute(attributes, keys, default=None):
    """
    Extract the first value from LDAP attributes.
    """
    # Skip loopkup if key is not defined.
    if not keys:
        return default
    # Convert key to a list.
    keys = keys if isinstance(keys, list) else [keys]
    # Loop on each attribute name to find a value.
    for attr in keys:
        try:
            value = attributes[attr]
            if isinstance(value, list) and len(value) > 0:
                return value[0]
            else:
                return value
        except KeyError:
            pass
    # Default to None.
    return default


class LdapPlugin(SimplePlugin):
    """
    Used this plugin to authenticate user against an LDAP server.

    `authenticate(username, password)` return None if the credentials are not
    valid. Otherwise it return a tuple or username and extra attributes.
    The extra attribute may contains `_fullname` and `_email`.
    """

    uri = None
    base_dn = None
    bind_dn = ''
    bind_password = ''
    scope = 'subtree'
    tls = False
    user_filter = '(objectClass=*)'
    username_attribute = 'uid'
    required_group = None
    group_attribute = 'member'
    group_attribute_is_dn = False
    group_filter = '(objectClass=*)'
    version = 3
    network_timeout = 10
    timeout = 10
    fullname_attribute = None
    firstname_attribute = None
    lastname_attribute = None
    email_attribute = None

    def start(self):
        # Don't configure this plugin if the ldap URI is not provided.
        if not self.uri:
            return
        self.bus.log('Start LDAP connection')
        # Set up the LDAP server object
        server = ldap3.Server(self.uri, connect_timeout=self.network_timeout, mode=ldap3.IP_V4_PREFERRED)
        # Create a pool of reusable connections
        self._pool = ldap3.Connection(
            server,
            user=self.bind_dn,
            password=self.bind_password,
            auto_bind=ldap3.AUTO_BIND_TLS_BEFORE_BIND if self.tls else ldap3.AUTO_BIND_NO_TLS,
            version=self.version,
            raise_exceptions=True,
            client_strategy=ldap3.REUSABLE,
        )

    def stop(self):
        self.bus.log('Stop LDAP connection')
        # Release the connection pool.
        if hasattr(self, '_pool'):
            self._pool.unbind()

    def authenticate(self, username, password):
        """
        Check if the given credential as valid according to LDAP.
        Return False if invalid.
        Return None if the plugin is unavailable to validate credentials or if the plugin is disabled.
        Return tuple (<username>, <attributes>) if the credentials are valid.
        """
        assert isinstance(username, str)
        assert isinstance(password, str)

        if not hasattr(self, '_pool'):
            return None

        # Connect to LDAP Server.
        with self._pool as conn:
            try:
                # Search the LDAP server for user's DN.
                search_filter = "(&{}({}={}))".format(self.user_filter, _safe(self.username_attribute), _safe(username))
                response = self._search(conn, search_filter)
                if not response:
                    logger.info("user %s not found in LDAP", username)
                    return False
                logger.info("user %s found in LDAP", username)
                user_dn = response[0]['dn']

                # Let "rebind" with user's full DN to verify password.
                if not conn.rebind(user=user_dn, password=password):
                    logger.info("user %s not found in LDAP", username)
                    return False

                # Get username
                attrs = response[0]['attributes']
                new_username = first_attribute(attrs, self.username_attribute)
                if not new_username:
                    logger.info(
                        "user object %s was found but the username attribute %s doesn't exists",
                        user_dn,
                        self.username_attribute,
                    )
                    return False

                # Verify if the user is member of the required group
                if self.required_group:
                    if not isinstance(self.required_group, list):
                        self.required_group = [self.required_group]
                    user_value = user_dn if self.group_attribute_is_dn else new_username
                    group_filter = '(&(%s=%s)(|%s)%s)' % (
                        _safe(self.group_attribute),
                        _safe(user_value),
                        ''.join(['(cn=%s)' % _safe(group) for group in self.required_group]),
                        self.group_filter,
                    )
                    # Search LDAP Server for matching groups.
                    logger.info(
                        "check if user %s is member of any group %s",
                        user_value,
                        ' '.join(self.required_group),
                    )
                    response = self._search(conn, group_filter, attributes=['cn'])
                    if not response:
                        logger.info(
                            "user %s was found but is not member of any group(s) %s",
                            user_value,
                            ' '.join(self.required_group),
                        )
                        return False

                # Extract common attribute from LDAP
                attrs['email'] = first_attribute(attrs, self.email_attribute)
                attrs['fullname'] = fullname = first_attribute(attrs, self.fullname_attribute)
                if not fullname:
                    firstname = first_attribute(attrs, self.firstname_attribute, '')
                    lastname = first_attribute(attrs, self.lastname_attribute, '')
                    attrs['fullname'] = ' '.join([name for name in [firstname, lastname] if name])
                return (new_username, attrs)
            except LDAPInvalidCredentialsResult:
                return False
            except LDAPException:
                logger.exception("can't validate user %s credentials", username)
            finally:
                # Rebind to original user.
                conn.unbind()
                conn.user = self.bind_dn
                conn.password = self.bind_password
                conn.authentication = ldap3.SIMPLE if self.bind_dn else ldap3.ANONYMOUS
            return None

    def search(self, filter, attributes=ldap3.ALL_ATTRIBUTES, search_base=None, paged_size=None):
        with self._pool as conn:
            return self._search(
                conn, filter=filter, attributes=attributes, search_base=search_base, paged_size=paged_size
            )

    def _search(self, conn, filter, attributes=ldap3.ALL_ATTRIBUTES, search_base=None, paged_size=None):
        search_scope = {'base': ldap3.BASE, 'onelevel': ldap3.LEVEL, 'subtree': ldap3.SUBTREE}.get(
            self.scope, ldap3.SUBTREE
        )
        logger.debug(
            "search ldap server: {}/{}?{}?{}?{}".format(
                self.uri, self.base_dn, self.username_attribute, search_scope, filter
            )
        )
        msg_id = conn.search(
            search_base=search_base or self.base_dn,
            search_filter=filter,
            search_scope=search_scope,
            time_limit=self.timeout,
            attributes=attributes,
            paged_size=paged_size,
        )
        response, _result_unused = conn.get_response(msg_id)
        return response


cherrypy.ldap = LdapPlugin(cherrypy.engine)
cherrypy.ldap.subscribe()

cherrypy.config.namespaces['ldap'] = lambda key, value: setattr(cherrypy.ldap, key, value)
