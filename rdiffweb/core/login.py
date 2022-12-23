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

import logging

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from rdiffweb.core.model import UserObject

logger = logging.getLogger(__name__)


class LoginPlugin(SimplePlugin):
    """
    This plugins register an "authenticate" listener to validate
    username and password of users. In addition, it provide a "login"
    listener to authenticate and possibly create the user in database.
    """

    add_missing_user = False
    add_user_default_role = UserObject.USER_ROLE
    add_user_default_userroot = None

    def start(self):
        self.bus.log('Start Login plugin')
        self.bus.subscribe("authenticate", self.authenticate)
        self.bus.subscribe("login", self.login)

    def stop(self):
        self.bus.log('Stop Login plugin')
        self.bus.unsubscribe("authenticate", self.authenticate)
        self.bus.unsubscribe("login", self.login)

    def authenticate(self, username, password):
        """
        Only verify the user's credentials using the database store.
        """
        user = UserObject.get_user(username)
        if user and user.validate_password(password):
            return username, {}
        return False

    def login(self, username, password):
        """
        Validate username password using database and LDAP.
        """
        # Validate credentials.
        authenticates = self.bus.publish('authenticate', username, password)
        authenticates = [a for a in authenticates if a]
        if not authenticates:
            return None
        real_username = authenticates[0][0]
        extra_attrs = authenticates[0][1]
        fullname = extra_attrs.get('_fullname', None)
        email = extra_attrs.get('_email', None)
        # When enabled, create missing userobj in database.
        userobj = UserObject.get_user(username)
        if userobj is None and self.add_missing_user:
            try:
                # At this point, we need to create a new user in database.
                # In case default values are invalid, let evaluate them
                # before creating the user in database.
                default_user_root = self.add_user_default_userroot and self.add_user_default_userroot.format(
                    **extra_attrs
                )
                default_role = UserObject.ROLES.get(self.add_user_default_role)
                userobj = UserObject.add_user(
                    username=real_username,
                    fullname=fullname,
                    email=email,
                    role=default_role,
                    user_root=default_user_root,
                ).commit()
            except Exception:
                logger.error('fail to create new user', exc_info=1)
        if userobj is None:
            # User doesn't exists in database
            return None

        # Update user attributes
        dirty = False
        if fullname:
            userobj.fullname = fullname
            dirty = True
        if email:
            userobj.email = email
            dirty = True
        if dirty:
            userobj.commit()
        self.bus.publish('user_login', userobj)
        return userobj


cherrypy.login = LoginPlugin(cherrypy.engine)
cherrypy.login.subscribe()

cherrypy.config.namespaces['login'] = lambda key, value: setattr(cherrypy.login, key, value)
