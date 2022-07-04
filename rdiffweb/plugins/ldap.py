# -*- coding: utf-8 -*-
# LDAP Plugins for cherrypy
# # Copyright (C) 2022 IKUS Software
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

import logging

import cherrypy
import ldap3
from cherrypy.process.plugins import SimplePlugin
from ldap3.core.exceptions import LDAPException, LDAPInvalidCredentialsResult, LDAPNoSuchObjectResult

logger = logging.getLogger(__name__)


def _first_attribute(attributes, key, default=None):
    """
    Extract the first value from LDAP attributes.
    """
    # Skip loopkup if key is not defined.
    if not key:
        return default
    # Convert key to a list.
    keys = key if isinstance(key, list) else [key]
    # Loop on each attribute name to find a value.
    for attr in keys:
        value = attributes.get(attr, None)
        if isinstance(value, list) and len(value) > 0:
            return value[0]
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
    filter = '(objectClass=*)'
    username_attribute = 'uid'
    required_group = None
    group_attribute = 'member'
    group_attribute_is_dn = False
    version = 3
    network_timeout = 10
    timeout = 10
    fullname_attribute = None
    firstname_attribute = None
    lastname_attribute = None
    email_attribute = None

    def start(self):
        if self.uri:
            self.bus.log('Start LDAP connection')
            self.bus.subscribe("authenticate", self.authenticate)

    def stop(self):
        self.bus.log('Stop LDAP connection')
        self.bus.unsubscribe("authenticate", self.authenticate)

    def authenticate(self, username, password):
        """
        Check if the given credential as valid according to LDAP.
        Return False if invalid.
        Return None if the plugin is unavailable to validate credentials or if the plugin is disabled.
        Return tuple (<username>, <attributes>) if the credentials are valid.
        """
        assert isinstance(username, str)
        assert isinstance(password, str)

        server = ldap3.Server(self.uri, connect_timeout=self.network_timeout)
        conn = ldap3.Connection(
            server,
            user=self.bind_dn,
            password=self.bind_password,
            auto_bind=False,
            version=self.version,
            client_strategy=ldap3.SYNC,
            raise_exceptions=True,
        )
        conn.raise_exceptions = True

        try:
            if self.tls:
                conn.start_tls()

            # Bind to the LDAP server
            logger.debug("binding to ldap server {}".format(self.uri))
            conn.bind()

            # Search the LDAP server
            search_filter = "(&{}({}={}))".format(self.filter, self.username_attribute, username)
            search_scope = {'base': ldap3.BASE, 'onelevel': ldap3.LEVEL, 'subtree': ldap3.SUBTREE}.get(
                self.scope, ldap3.SUBTREE
            )
            logger.debug(
                "search ldap server: {}/{}?{}?{}?{}".format(
                    self.uri, self.base_dn, self.username_attribute, search_scope, search_filter
                )
            )
            status = conn.search(
                search_base=self.base_dn,
                search_filter=search_filter,
                search_scope=search_scope,
                time_limit=self.timeout,
                attributes=ldap3.ALL_ATTRIBUTES,
            )
            if not status:
                logger.info("user %s not found in LDAP", username)
                return False

            logger.info("user %s found in LDAP", username)
            response = conn.response
            user_dn = response[0]['dn']
            conn.rebind(user=user_dn, password=password)

            # Get username
            attrs = response[0]['attributes']
            new_username = _first_attribute(attrs, self.username_attribute)
            if not new_username:
                logger.info(
                    "user object %s was found but the username attribute %s doesn't exists",
                    user_dn,
                    self.username_attribute,
                )
                return False

            # Verify if the user is member of the required group
            if self.required_group:
                user_value = user_dn if self.group_attribute_is_dn else new_username
                logger.info("check if user %s is member of %s", user_value, self.required_group)
                try:
                    if not conn.compare(self.required_group, self.group_attribute, user_value):
                        logger.info("user %s was found but is not member of group %s", user_value, self.required_group)
                        return False
                except LDAPNoSuchObjectResult:
                    logger.exception("group %s not found", self.required_group)
                    return False
            # Remove entryDN from attributes list.
            if 'entryDN' in attrs:
                del attrs['entryDN']
            # Extract common attribute from LDAP
            attrs['_email'] = _first_attribute(attrs, self.email_attribute)
            attrs['_fullname'] = fullname = _first_attribute(attrs, self.fullname_attribute)
            if not fullname:
                firstname = _first_attribute(attrs, self.firstname_attribute, '')
                lastname = _first_attribute(attrs, self.lastname_attribute, '')
                if firstname or lastname:
                    attrs['_fullname'] = '%s %s' % (firstname, lastname)
            return (new_username, attrs)
        except LDAPInvalidCredentialsResult:
            return False
        except LDAPException:
            logger.exception("can't validate user %s credentials", username)
        finally:
            conn.unbind()
        return None


cherrypy.ldap = LdapPlugin(cherrypy.engine)
cherrypy.ldap.subscribe()

cherrypy.config.namespaces['ldap'] = lambda key, value: setattr(cherrypy.ldap, key, value)
