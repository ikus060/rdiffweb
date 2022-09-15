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

from rdiffweb.controller import Controller
from rdiffweb.controller.page_pref_general import PagePrefsGeneral
from rdiffweb.controller.page_pref_mfa import PagePrefMfa
from rdiffweb.controller.page_pref_notification import PagePrefNotification
from rdiffweb.controller.page_pref_session import PagePrefSession
from rdiffweb.controller.page_pref_sshkeys import PagePrefSshKeys
from rdiffweb.controller.page_pref_tokens import PagePrefTokens
from rdiffweb.core.rdw_templating import url_for

# Define the logger
logger = logging.getLogger(__name__)


class PreferencesPage(Controller):

    general = PagePrefsGeneral()
    mfa = PagePrefMfa()
    notification = PagePrefNotification()
    session = PagePrefSession()
    sshkeys = PagePrefSshKeys()
    tokens = PagePrefTokens()

    @cherrypy.expose
    def index(self, panelid=None, **kwargs):
        raise cherrypy.HTTPRedirect(url_for('/prefs/general'))
