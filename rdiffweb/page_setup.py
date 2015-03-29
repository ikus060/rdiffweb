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

import cherrypy
import os
import stat
import logging
import page_main

# Define the logger
logger = logging.getLogger(__name__)


class rdiffSetupPage(page_main.rdiffPage):

    """
    Helps the user through initial rdiffweb setup.
    This page is displayed with rdiffweb is not yet configured.
    """

    @cherrypy.expose
    def index(self, **kwargs):
        setup_enabled = True
        warning = ""
        message = ""
        error = ""

        # Check if users already exists
        try:
            if len(self.getUserDB().list()) > 0:
                setup_enabled = False
                message = "rdiffweb is already configured !"
        except:
            logger.exception("fail to get users")
            setup_enabled = False
            warning = _("""can't determine if rdiffweb is configured! Check application log.""")

        # Check if configuration file exists
        try:
            self._ensure_config_file_exists()
        except:
            setup_enabled = False
            warning = _("""rdiffweb doesn't have read-write access to the configuration file. You may try to change the permissions of this file.""")

        # if no post data, return plain page.
        if not setup_enabled or not self._is_submit():
            return self._writePage("setup.html",
                                   setup_enabled=setup_enabled,
                                   message=message,
                                   warning=warning,
                                   error=error)

        logger.info("validating root password")
        completed = False
        try:
            # Get parameters
            admin_username = "admin"
            admin_password = "admin123"
            admin_root = "/var/backups/"
            # Execute the setup
            self._set_admin_user(admin_username, admin_password)
            self._set_admin_root(admin_username, admin_root)
            logger.info("setup completed")
            completed = True
        except ValueError as e:
            logger.exception("fail to complete setup")
            error = "Error! " + str(e)

        return self._writePage("setup.html",
                               setup_enabled=setup_enabled,
                               completed=completed,
                               admin_username=admin_username,
                               admin_password=admin_password,
                               message=message,
                               warning=warning,
                               error=error)

    def _set_admin_user(self, username, password):
        # Create the user
        self.getUserDB().add_user(username)
        self.getUserDB().set_password(username, None, password)

    def _set_admin_root(self, username, userRoot):
        # Sets admin root
        self.getUserDB().set_info(username, userRoot, True)

    def _ensure_config_file_exists(self):
        """Try to access or create the configuration file. It raised an
        exception if the configuration file is not accessible."""
        try:
            if not os.path.exists("/etc/rdiffweb"):
                os.mkdir("/etc/rdiffweb", stat.S_IRWXU)
            if not os.path.exists("/etc/rdiffweb/rdw.conf"):
                open("/etc/rdiffweb/rdw.conf", "a").close()
                os.chmod("/etc/rdiffweb/rdw.conf", stat.S_IRWXU)
        except OSError as error:
            raise ValueError(str(error))
