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

from . import page_main
import cherrypy
from . import rdw_spider_repos


class rdiffAdminPage(page_main.rdiffPage):

    @cherrypy.expose
    def index(self, **kwargs):
        if not self._user_is_admin():
            return self._writeErrorPage("Access denied.")

        # If we're just showing the initial page, just do that
        if not self._is_submit():
            return self._writeAdminPage()

        # We need to change values. Change them, then give back that main page
        # again, with a message
        action = cherrypy.request.params["action"]
        username = cherrypy.request.params.get("username")
        user_root = cherrypy.request.params.get("user_root")
        is_admin = cherrypy.request.params.get("is_admin", False)

        # Fork the behaviour according to the action.
        if action == "edit":
            if not self.getUserDB().userExists(username):
                return self._writeAdminPage(error="The user does not exist.")
            self.getUserDB().setUserInfo(username, user_root, is_admin)
            return self._writeAdminPage(success="User information modified successfully")
        elif action == "add":
            if self.getUserDB().userExists(username):
                return self._writeAdminPage(error="The specified user already exists.")
            if username == "":
                return self._writeAdminPage(error="The username is invalid.")
            self.getUserDB().addUser(username)
            self.getUserDB().setUserPassword(
                username, cherrypy.request.params["password"])
            self.getUserDB().setUserInfo(username, user_root, is_admin)
            return self._writeAdminPage(success="User added successfully.")
        if action == "delete":
            if not self.getUserDB().userExists(username):
                return self._writeAdminPage(error="The user does not exist.")
            if username == self.getUsername():
                return self._writeAdminPage(error="You cannot remove your own account!.")
            self.getUserDB().deleteUser(username)
            return self._writeAdminPage(success="User account removed.")

    # HELPER FUNCTIONS #

    def getParmsForPage(self):
        userNames = self.getUserDB().getUserList()
        users = [{"username": user,
                  "is_admin": self.getUserDB().userIsAdmin(user),
                  "user_root": self.getUserDB().getUserRoot(user)
                  } for user in userNames]
        return {"title": "Admin panel",
                "users": users}

    def _writeAdminPage(self, **kwargs):
        """Generate the admin page using template."""
        params = self.getParmsForPage()
        params.update(kwargs)
        return self._writePage("admin.html", **params)
