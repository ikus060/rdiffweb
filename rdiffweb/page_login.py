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
import logging
import page_main

from i18n import ugettext as _
from rdw_helpers import quote_url

# Define the logger
logger = logging.getLogger(__name__)


class LoginPage(page_main.MainPage):

    @cherrypy.expose
    def index(self, redirect=u"", login=u"", password=""):
        assert isinstance(redirect, unicode)
        assert isinstance(login, unicode)
        assert isinstance(password, unicode)

        # when parameters are sent using post, redirect URL doesn't need to be
        # quoted.
        if not self._is_submit():
            parts = redirect.partition("?")
            redirect = quote_url(parts[0])
            if parts[2]:
                redirect += "?"
                redirect += quote_url(parts[2], safe="/=&")

        params = {'redirect': redirect,
                  'login': login}

        # Add welcome message to params. Try to load translated message.
        params["welcome_msg"] = self.app.cfg.get_config("WelcomeMsg")
        if hasattr(cherrypy.response, 'i18n'):
            lang = cherrypy.response.i18n._lang
            params["welcome_msg"] = self.app.cfg.get_config("WelcomeMsg[%s]" % (lang), params["welcome_msg"])

        if self._is_submit():
            params.update(self.handle_login(login, password, redirect))

        return self._compile_template("login.html", **params)

    def handle_login(self, login, password, redirect):
        """
        Handle login.
        """
        # check for login credentials
        params = dict()
        logger.debug("check credentials for [%s]" % login)
        try:
            username = self.app.userdb.login(login, password)
        except:
            logger.exception("fail to validate user credential.")
            params["warning"] = _("Fail to validate user credential.")
        else:
            if username:
                # Login successful
                cherrypy.session['username'] = username  # @UndefinedVariable
                if not redirect or redirect.startswith("/login/"):
                    redirect = "/"
                # The redirect url was unquoted by cherrypy, quote the
                # url again.
                logger.info("redirect user to %s" % redirect)
                raise cherrypy.HTTPRedirect(redirect)
            else:
                logger.warn("invalid username or password")
                params["warning"] = _("Invalid username or password.")

        return params
