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

import cherrypy
import os
import stat
import crypt
import logging
import page_main

# Define the logger
logger = logging.getLogger(__name__)


class rdiffSetupPage(page_main.rdiffPage):

    """Helps the user through initial rdiffweb setup.
        This page is displayed with rdiffweb is not yet configured.
        """
    @cherrypy.expose
    def index(self, **kwargs):
        completed = False
        root_enabled = False
        error = ""
        message = ""

        # Check if root user is enabled
        try:
            root_enabled = self._rootAccountEnabled()
        except KeyError:
            error = "rdiffweb setup must be run with root privileges."

        # Check if configuration file exists
        try:
            self._ensureConfigFileExists()
        except:
            error = "rdiffweb configuration file doesn't exists."

        # Check if users already exists
        try:
            self.getUserDB().getUserList()
            message = "rdiffweb is already configured !"
        except:
            # Do nothing
            message = ""

        # if no post data, return plain page.
        if not self._is_submit():
            return self._writePage("setup.html",
                                   title='Setup rdiffweb',
                                   root_enabled=root_enabled,
                                   error=error)

        logger.info("validating root password")
        try:
            # Get parameters
            root_password = cherrypy.request.params["root_password"]
            admin_username = cherrypy.request.params["admin_username"]
            admin_password = cherrypy.request.params["admin_password"]
            admin_password_confirm = cherrypy.request.params[
                "admin_password_confirm"]
            admin_root = cherrypy.request.params["admin_root"]
            # Validate all the parameters
            self._validatePassword(root_password)
            self._validateAdminUser(
                admin_username, admin_password, admin_password_confirm)
            self._validateAdminRoot(admin_username, admin_root)
            # Execute the setup
            self._setAdminUser(
                admin_username, admin_password, admin_password_confirm)
            self._setAdminRoot(admin_username, admin_root)
            completed = True
        except ValueError as e:
            logger.exception("fail to complete setup")
            error = "Error! " + str(e)

        return self._writePage("setup.html",
                               title='Setup rdiffweb',
                               root_enabled=root_enabled,
                               completed=completed,
                               error=error)

    def _validatePassword(self, password):
        if self._rootAccountEnabled():
            # Check the root account
            if (self._checkSystemPassword("root", password)):
                return
        else:
            raise ValueError(
                "The root account has been disabled. Web-based setup is not supported.")
            # If the root account is disabled, check to see if another
            # user set up the account, in which case their password is valid.
            if password != "billfrank":
                raise ValueError("The password is invalid.")

    def _validateAdminUser(self, username, password, confirmPassword):
        if not username:
            raise ValueError("A username was not specified.")
        if not password:
            raise ValueError("The administrative user must have a password.")
        if password != confirmPassword:
            raise ValueError("The passwords do not match.")

    def _validateAdminRoot(self, username, userRoot):
        if not username:
            raise ValueError("A username was not specified.")
        if not userRoot:
            raise ValueError("A root directory was not specified.")
        if not os.path.exists(userRoot):
            raise ValueError("The specified directory does not exist.")

    def _checkSystemPassword(self, username, password):
        cryptedpasswd = self._getCryptedPassword(username)
        if crypt.crypt(password, cryptedpasswd) != cryptedpasswd:
            raise ValueError("Invalid root password.")

    def _setAdminUser(self, username, password, confirmPassword):
        # Validate parameters
        self._validateAdminUser(username, password, confirmPassword)
        # Create the user
        self.getUserDB().addUser(username)
        self.getUserDB().setUserPassword(username, password)

    def _setAdminRoot(self, username, userRoot):
        # Validate parameters
        self._validateAdminRoot(username, userRoot)
        # Sets admin root
        self.getUserDB().setUserInfo(username, userRoot, True)

    def _rootAccountEnabled(self):
        cryptedpasswd = self._getCryptedPassword("root")
        return cryptedpasswd != '!'

    def _ensureConfigFileExists(self):
        try:
            if not os.path.exists("/etc/rdiffweb"):
                os.mkdir("/etc/rdiffweb", stat.S_IRWXU)
            if not os.path.exists("/etc/rdiffweb/rdw.conf"):
                open("/etc/rdiffweb/rdw.conf", "a").close()
                os.chmod("/etc/rdiffweb/rdw.conf", stat.S_IRWXU)
        except OSError as error:
            raise ValueError(str(error))

    def _getCryptedPassword(self, username):
        try:
            import spwd
        except ImportError:
            return self._manualGetCryptedPassword(username)
        else:
            return spwd.getspnam(username)[1]

    def _manualGetCryptedPassword(self, username):
        pwlines = open("/etc/shadow").readlines()
        for line in pwlines:
            entryParts = line.split(":")
            if len(entryParts) == 9 and entryParts[0] == username:
                return entryParts[1]
