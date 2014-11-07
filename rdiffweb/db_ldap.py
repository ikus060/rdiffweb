#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffweb contributors
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

import ldap
import logging
import db
import rdw_config

# Define the logger
logger = logging.getLogger(__name__)


class ldapUserDB(db.userDB):

    def __init__(self, delegate, configFilePath=None):
        """Create a new LDAP Database for authentication. Some behavior are
            delegate to external database."""
        self.delegate = delegate
        self.configFilePath = configFilePath

        # Get LDAP configuration parameters
        self.uri = rdw_config.getConfigSetting(
            "LdapUri", self.configFilePath, None)
        if self.uri is None:
            raise "LdapUri must be define in configuration"
        self.tls = rdw_config.getConfigSetting(
            "LdapTls", self.configFilePath).lower() == "true"
        self.base_dn = rdw_config.getConfigSetting(
            "LdapBaseDn", self.configFilePath, None)
        if self.uri is None:
            raise "LdapUri must be define in configuration"
        self.attribute = rdw_config.getConfigSetting(
            "LdapAttribute", self.configFilePath, "uid")
        self.scope = rdw_config.getConfigSetting(
            "LdapScope", self.configFilePath, "subtree")
        if self.scope == "base":
            self.scope = ldap.SCOPE_BASE
        elif self.scope == "onelevel":
            self.scope = ldap.SCOPE_ONELEVEL
        else:
            self.scope = ldap.SCOPE_SUBTREE
        self.filter = rdw_config.getConfigSetting(
            "LdapFilter", self.configFilePath, "(objectClass=*)")
        self.bind_dn = rdw_config.getConfigSetting(
            "LdapBindDn", self.configFilePath, "")
        self.bind_password = rdw_config.getConfigSetting(
            "LdapBindPassword", self.configFilePath, "")

        # Get Version
        try:
            self.version = int(rdw_config.getConfigSetting(
                "LdapVersion", self.configFilePath, "3"))
        except ValueError:
            logger.warn("LdapVersion shoud be either 2 or 3")

        # Get Network timeout
        self.network_timeout = 100
        try:
            self.network_timeout = int(rdw_config.getConfigSetting(
                "LdapNetworkTimeout", self.configFilePath, "10"))
        except ValueError:
            logger.warn("LdapNetworkTimeout shoud be an integer")

        # Get Timeout
        try:
            self.timeout = int(rdw_config.getConfigSetting(
                "LdapTimeout", self.configFilePath, "300"))
        except ValueError:
            logger.warn("LdapTimeout shoud be an integer")

    def modificationsSupported(self):
        return True

    def userExists(self, username):
        return self.delegate.userExists(username)

    def areUserCredentialsValid(self, username, password):
        # Check LDAP credential only.
        l = ldap.initialize(self.uri)

        # Set v2 or v3
        if self.version == 2:
            l.protocol_version = ldap.VERSION2
        else:
            l.protocol_version = ldap.VERSION3

        # try STARTLS if configured
        if self.tls:
            try:
                l.start_tls_s()
            except ldap.LDAPError as e:
                if isinstance(e.message, dict) and 'desc' in e.message:
                    logger.exception(
                        "error connecting ldap server: " + e.message['desc'])
                else:
                    logger.exception(
                        "error connecting ldap server: " + e.message['info'])
                return False

        # Sets the scope for the search

        # Try to bind with username/password
        try:
            # Bind to the LDAP server
            logger.info("binding to ldap server {}".format(self.uri))
            l.simple_bind_s(self.bind_dn, self.bind_password)

            # Search the LDAP server
            search_filter = "(&{}({}={}))".format(
                self.filter, self.attribute, username)
            logger.info("search ldap server: {}/{}?{}?{}?{}".format(
                self.uri, self.base_dn, self.attribute, self.scope,
                self.filter))
            r = l.search_s(self.base_dn, self.scope, search_filter)
            if len(r) != 1:
                logger.warn("user [%s] not found" % username)
                return False

            # Bind using the user credentials. Throws an exception in case of
            # error.
            l.simple_bind_s(r[0][0], password)
            l.unbind_s()
            logger.warn("user [%s] found" % username)
            return True
        except ldap.LDAPError as e:
            l.unbind_s()
            if isinstance(e.message, dict) and 'desc' in e.message:
                logger.exception(
                    "error connecting ldap server: " + e.message['desc'])
            else:
                logger.exception(
                    "error connecting ldap server: " + e.message['info'])
            return False

    def getUserRoot(self, username):
        return self.delegate.getUserRoot(username)

    def getUserRepoPaths(self, username):
        return self.delegate.getUserRepoPaths(username)

    def getUserEmail(self, username):
        return self.delegate.getUserEmail(username)

    def getUserList(self):
        return self.delegate.getUserList()

    def addUser(self, username):
        return self.delegate.addUser(username)

    def deleteUser(self, username):
        return self.delegate.deleteUser(username)

    def setUserInfo(self, username, userRoot, isAdmin):
        return self.delegate.setUserInfo(username, userRoot, isAdmin)

    def setUserEmail(self, username, userEmail):
        # TODO May try to get email from LDAP.
        return self.delegate.setUserEmail(username, userEmail)

    def setUserRepos(self, username, repoPaths):
        return self.delegate.setUserRepos(username, repoPaths)

    def setUserPassword(self, username, password):
        # Do nothing. LDAP cannot change password.
        return

    def setRepoMaxAge(self, username, repoPath, maxAge):
        return self.delegate.setRepoMaxAge(username, repoPath, maxAge)

    def getRepoMaxAge(self, username, repoPath):
        return self.delegate.getRepoMaxAge(username, repoPath)

    def userIsAdmin(self, username):
        return self.delegate.userIsAdmin(username)
