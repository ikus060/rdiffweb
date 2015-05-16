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

        if self._is_submit():
            # check for login credentials
            logger.info("check credentials for [%s]" % login)
            errorMsg = self.check_password(login, password)
            if not errorMsg:
                cherrypy.session['username'] = login
                if not redirect or redirect.startswith("/login/"):
                    redirect = "/"
                # The redirect url was unquoted by cherrypy, quote the
                # url again.
                logger.info("redirect user to %s" % redirect)
                raise cherrypy.HTTPRedirect(redirect)

            # update form values
            params["warning"] = errorMsg

        return self._compile_template("login.html", **params)

    def check_password(self, username, password):
        """
        Check credential using local database.
        """
        try:
            if self.app.userdb.are_valid_credentials(username, password):
                cherrypy.session['username'] = username  # @UndefinedVariable
                return False
            return _("Invalid username or password.")
        except:
            logger.exception("fail to validate user credential.")
            return _("Fail to validate user credential.")
