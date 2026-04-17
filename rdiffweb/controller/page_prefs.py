# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

import cherrypy
from cherrypy_foundation.url import url_for

from rdiffweb.controller.page_pref_general import PagePrefsGeneral
from rdiffweb.controller.page_pref_mfa import PagePrefMfa
from rdiffweb.controller.page_pref_session import PagePrefSession
from rdiffweb.controller.page_pref_sshkeys import PagePrefSshKeys
from rdiffweb.controller.page_pref_tokens import PagePrefTokens

# Define the logger
logger = logging.getLogger(__name__)


class PreferencesPage:
    general = PagePrefsGeneral()
    mfa = PagePrefMfa()
    session = PagePrefSession()
    sshkeys = PagePrefSshKeys()
    tokens = PagePrefTokens()

    @cherrypy.expose
    def index(self, panelid=None, **kwargs):
        """
        Redirect user to general settings
        """
        raise cherrypy.HTTPRedirect(url_for('/prefs/general'))
