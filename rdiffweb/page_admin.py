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

from __future__ import unicode_literals

import page_main
import cherrypy
import logging
import os
import rdw_spider_repos

# Define the logger
logger = logging.getLogger(__name__)


class rdiffAdminPage(page_main.rdiffPage):

    def _check_user_exists(self, username):
        """Raise an exception if the user doesn't exists."""
        if not self.getUserDB().exists(username):
            raise ValueError("The user does not exist.")

    def _check_user_root_dir(self, directory):
        """Raised an exception if the directory is not valid."""
        if not os.access(directory, os.F_OK):
            raise ValueError("User root directory [%s] is not accessible!"
                             % directory)
        if not os.path.isdir(directory):
            raise ValueError("User root directory [%s] is not accessible!"
                             % directory)

    @cherrypy.expose
    def index(self):

        # Check if user is an administrator
        if not self._user_is_admin():
            return self._writeErrorPage("Access denied.")

        params = {}
        try:
            users = self.getUserDB().list()
            repos = set()
            for user in users:
                for repo in self.getUserDB().get_repos(user):
                    repos.add(repo)

            params = {"user_count": len(users),
                      "repo_count": len(repos)}
        except:
            logger.exception("fail to get stats", **params)
            return self._writeErrorPage("Can't get admin information.")

        return self._writePage("admin.html", **params)

    @cherrypy.expose
    def users(self, userfilter=u"", usersearch=u"", action=u"", username=u"",
              email=u"", password=u"", user_root=u"", is_admin=u""):
        assert isinstance(userfilter, unicode)
        assert isinstance(usersearch, unicode)

        # Check if user is an administrator
        if not self._user_is_admin():
            return self._writeErrorPage("Access denied.")

        # If we're just showing the initial page, just do that
        params = {}
        if self._is_submit():
            try:
                params = self._users_handle_action(action, username,
                                                   email, password, user_root,
                                                   is_admin)
            except ValueError as e:
                params['error'] = unicode(e)
            except Exception as e:
                logger.exception("unknown error processing action")
                params['error'] = "Fail to execute operation."

        # Get page parameters
        try:
            params.update(
                self._users_get_params_for_page(userfilter, usersearch))
        except:
            logger.exception("fail to get user list")
            return self._writeErrorPage("Can't get user list.")

        # Build users page
        return self._writePage("admin_users.html", **params)

    def _users_get_params_for_page(self, userfilter, usersearch):
        usernames = self.getUserDB().list()
        users = [{"username": username,
                  "email": self.getUserDB().get_email(username),
                  "is_admin": self.getUserDB().is_admin(username),
                  "user_root": self.getUserDB().get_root_dir(username)
                  } for username in usernames]

        # Apply the filters.
        filtered_users = users
        if userfilter == "admins":
            filtered_users = filter(lambda x: x["is_admin"],
                                    filtered_users)
        # Apply the search.
        if usersearch:
            filtered_users = filter(lambda x: usersearch in x["username"]
                                    or usersearch in x["email"],
                                    filtered_users)

        return {"ldap_enabled": self.getUserDB().is_ldap(),
                "userfilter": userfilter,
                "usersearch": usersearch,
                "filtered_users": filtered_users,
                "users": users}

    def _users_handle_action(self, action, username, email, password,
                             user_root, is_admin):

        success = ""
        warning = ""

        # We need to change values. Change them, then give back that main
        # page again, with a message
        if username == self.getUsername():
            # Don't allow the user to changes it's "admin" state.
            is_admin = self.getUserDB().is_admin(username)

        # Fork the behaviour according to the action.
        if action == "edit":
            self._check_user_exists(username)
            logger.info("updating user info")
            if password:
                self.getUserDB().set_password(username, None, password)
            self.getUserDB().set_info(username, user_root, is_admin)
            self.getUserDB().set_email(username, email)
            success = "User information modified successfully."

            # Check and update user directory
            try:
                self._check_user_root_dir(user_root)
                logger.info("COUCOU1")
                rdw_spider_repos.findReposForUser(username,
                                                  self.getUserDB())
                logger.info("COUCOU2")
            except ValueError as e:
                success = ""
                warning = unicode(e)

        elif action == "add":

            if self.getUserDB().exists(username):
                raise ValueError("The specified user already exists.")
            elif username == "":
                raise ValueError("The username is invalid.")
            logger.info("adding user [%s]" % username)
            self.getUserDB().add_user(username)
            self.getUserDB().set_password(username, None, password)
            self.getUserDB().set_info(username, user_root, is_admin)
            self.getUserDB().set_email(username, email)

            # Check and update user directory
            try:
                self._check_user_root_dir(user_root)
                rdw_spider_repos.findReposForUser(username,
                                                  self.getUserDB())
            except ValueError as e:
                warning = unicode(e)
            success = "User added successfully."

        if action == "delete":

            self._check_user_exists(username)
            if username == self.getUsername():
                raise ValueError("You cannot remove your own account!.")
            logger.info("deleting user [%s]" % username)
            self.getUserDB().delete_user(username)
            success = "User account removed."

        # Return messages
        return {'success': success,
                'warning': warning}
