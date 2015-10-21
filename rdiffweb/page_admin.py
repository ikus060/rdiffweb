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

import page_main
import cherrypy
import logging
import os
import rdw_spider_repos

from i18n import ugettext as _

# Define the logger
logger = logging.getLogger(__name__)


class AdminPage(page_main.MainPage):
    """Administration pages. Allow to manage users database."""

    def _check_user_exists(self, username):
        """Raise an exception if the user doesn't exists."""
        if not self.app.userdb.exists(username):
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
        if not self.app.currentuser or not self.app.currentuser.is_admin:
            return self._compile_error_template(_("Access denied."))

        params = {}
        try:
            users = self.app.userdb.list()
            repos = set()
            for user in users:
                for repo in self.app.userdb.get_repos(user):
                    repos.add(repo)

            params = {"user_count": len(users),
                      "repo_count": len(repos)}
        except:
            logger.exception("fail to get stats", **params)
            return self._compile_error_template(_("Can't get admin information."))

        return self._compile_template("admin.html", **params)

    @cherrypy.expose
    def plugins(self):
        """
        Display the plugins page. Listing all the plugin.
        """
        # Check if user is an administrator
        if not self.app.currentuser or not self.app.currentuser.is_admin:
            return self._compile_error_template(_("Access denied."))

        params = {}
        try:
            params = self._plugins_get_params_for_page()
        except:
            logger.exception("fail to get list of plugins")
            params['error'] = _("Fail to get list of plugins.")

        return self._compile_template("admin_plugins.html", **params)

    def _plugins_get_params_for_page(self):
        """
        Build the list of params to display the page.
        """
        plugins = list()
        for plugin_info in self.app.plugins.locate_plugins():
            # Check if the plugin is currently enabled.
            plugin_enabled = self.app.plugins.get_plugin_by_name(
                plugin_info.name) is not None
            # Create a data structure to represent the plugin. Don't send the
            # PluginInfo to the templates !
            plugin = {"name": plugin_info.name,
                      "author": plugin_info.author,
                      "copyright": plugin_info.copyright,
                      "description": plugin_info.description,
                      "path": plugin_info.path,
                      "version": plugin_info.version,
                      "website": plugin_info.website,
                      "enabled": plugin_enabled,
                      }
            plugins.append(plugin)

        return {"plugins": plugins}

    @cherrypy.expose
    def users(self, userfilter=u"", usersearch=u"", action=u"", username=u"",
              email=u"", password=u"", user_root=u"", is_admin=u""):

        # Check if user is an administrator
        if not self.app.currentuser or not self.app.currentuser.is_admin:
            return self._compile_error_template(_("Access denied."))

        assert isinstance(userfilter, unicode)
        assert isinstance(usersearch, unicode)

        # If we're just showing the initial page, just do that
        params = {}
        if self._is_submit():
            try:
                params = self._users_handle_action(action, username,
                                                   email, password, user_root,
                                                   is_admin)
            except ValueError as e:
                logger.exception("unknown error processing action")
                params['error'] = unicode(e)
            except Exception as e:
                logger.exception("unknown error processing action")
                params['error'] = _("Fail to execute operation.")

        # Get page parameters
        try:
            params.update(
                self._users_get_params_for_page(userfilter, usersearch))
        except:
            logger.exception("fail to get user list")
            return self._compile_error_template(_("Can't get user list."))

        # Build users page
        return self._compile_template("admin_users.html", **params)

    def _users_get_params_for_page(self, userfilter, usersearch):
        usernames = self.app.userdb.list()
        users = [{"username": username,
                  "email": self.app.userdb.get_email(username),
                  "is_admin": self.app.userdb.is_admin(username),
                  "user_root": self.app.userdb.get_user_root(username)
                  } for username in usernames]

        # Apply the filters.
        filtered_users = users
        if userfilter == "admins":
            filtered_users = filter(lambda x: x["is_admin"],
                                    filtered_users)
        # Apply the search.
        if usersearch:
            filtered_users = filter(lambda x: usersearch in x["username"] or
                                    usersearch in x["email"],
                                    filtered_users)

        return {"userfilter": userfilter,
                "usersearch": usersearch,
                "filtered_users": filtered_users,
                "users": users}

    def _users_handle_action(self, action, username, email, password,
                             user_root, is_admin):

        success = ""
        warning = ""

        # We need to change values. Change them, then give back that main
        # page again, with a message
        if username == self.app.currentuser.username:
            # Don't allow the user to changes it's "admin" state.
            is_admin = self.app.currentuser.is_admin

        # Fork the behaviour according to the action.
        if action == "edit":
            self._check_user_exists(username)
            logger.info("updating user info")
            if password:
                self.app.userdb.set_password(username, password, old_password=None)
            self.app.userdb.set_user_root(username, user_root)
            self.app.userdb.set_is_admin(username, is_admin)
            self.app.userdb.set_email(username, email)
            success = _("User information modified successfully.")

            # Check and update user directory
            try:
                self._check_user_root_dir(user_root)
                rdw_spider_repos.find_repos_for_user(username, self.app.userdb)
            except ValueError as e:
                success = ""
                warning = unicode(e)

        elif action == "add":

            if self.app.userdb.exists(username):
                raise ValueError("The user %s already exists." % (username))
            elif username == "":
                raise ValueError("The username is invalid.")
            logger.info("adding user [%s]" % username)

            self.app.userdb.add_user(username, password)
            self.app.userdb.set_user_root(username, user_root)
            self.app.userdb.set_is_admin(username, is_admin)
            self.app.userdb.set_email(username, email)

            # Check and update user directory
            try:
                self._check_user_root_dir(user_root)
                rdw_spider_repos.find_repos_for_user(username, self.app.userdb)
            except ValueError as e:
                warning = unicode(e)
            success = "User added successfully."

        if action == "delete":

            self._check_user_exists(username)
            if username == self.app.currentuser.username:
                raise ValueError("You cannot remove your own account!.")
            logger.info("deleting user [%s]" % username)
            self.app.userdb.delete_user(username)
            success = "User account removed."

        # Return messages
        return {'success': success,
                'warning': warning}
