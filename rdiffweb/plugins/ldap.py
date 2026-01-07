# LDAP Plugins for cherrypy
# Copyright (C) 2025 IKUS Software
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

_safe = ldap3.utils.conv.escape_filter_chars


def all_attribute(attributes, keys, default=None):
    """
    Extract all values from LDAP attributes.
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
            if isinstance(value, list):
                if len(value) == 0:
                    pass
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
    username_attribute = ['uid']
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

    def graceful(self):
        """Reload of subscribers."""
        self.stop()
        self.start()

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
                safe_username = _safe(username)
                attr_filter = ''.join([f'({_safe(attr)}={safe_username})' for attr in self.username_attribute])
                search_filter = f"(&{self.user_filter}(|{attr_filter}))"
                response = self._search(conn, search_filter)
                if not response:
                    cherrypy.log(f"lookup failed username={username} reason=not_found", context='LDAP')
                    return False
                cherrypy.log(f"lookup successful username={username}", context='LDAP')
                user_dn = response[0]['dn']

                # Use a separate connection to validate credentials
                login_conn = ldap3.Connection(
                    self._pool.server,
                    user=user_dn,
                    password=password,
                    version=self.version,
                    raise_exceptions=True,
                    client_strategy=ldap3.ASYNC,
                )
                if not login_conn.bind():
                    cherrypy.log(
                        f'ldap authentication failed username={username} reason=wrong_password',
                        context='LDAP',
                        severity=logging.WARNING,
                    )
                    return False

                # Get username
                attrs = response[0]['attributes']
                new_username = first_attribute(attrs, self.username_attribute)
                if not new_username:
                    cherrypy.log(
                        f"object missing username attribute user_dn={user_dn} attribute={self.username_attribute}",
                        context='LDAP',
                        severity=logging.WARNING,
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
                    cherrypy.log(
                        f"group check start username={user_value} required_groups={' '.join(self.required_group)}",
                        context='LDAP',
                    )
                    response = self._search(conn, group_filter, attributes=['cn'])
                    if not response:
                        cherrypy.log(
                            f"group check failed username={user_value} required_groups={' '.join(self.required_group)}",
                            context='LDAP',
                        )
                        return False

                # Extract common attribute from LDAP
                attrs['dn'] = user_dn
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
                cherrypy.log(
                    f"unexpected error username={username}", context='LDAP', severity=logging.ERROR, traceback=True
                )
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
        search_base = search_base or self.base_dn
        cherrypy.log(f"search {self.uri}/{search_base}?{search_scope}?{filter}", context='LDAP')
        msg_id = conn.search(
            search_base=search_base,
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
