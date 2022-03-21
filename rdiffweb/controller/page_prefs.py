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
from rdiffweb.controller.pref_general import PrefsGeneralPanelProvider
from rdiffweb.controller.pref_notification import NotificationPref
from rdiffweb.controller.pref_sshkeys import SSHKeysPlugin
from rdiffweb.core.config import Option

# Define the logger
logger = logging.getLogger(__name__)


@cherrypy.popargs('panelid')
class PreferencesPage(Controller):

    disable_ssh_keys = Option('disable_ssh_keys')

    @cherrypy.expose
    def default(self, panelid=None, **kwargs):
        if isinstance(panelid, bytes):
            panelid = panelid.decode('ascii')

        # Lazy create the list of "panels".
        if not hasattr(self, 'panels'):
            self.panels = [PrefsGeneralPanelProvider(), NotificationPref()]
            # Show SSHKeys only if enabled.
            if not self.disable_ssh_keys:
                self.panels += [SSHKeysPlugin()]

        # Select the right panelid. Default to the first one if not define by url.
        panelid = panelid or self.panels[0].panel_id

        # Search the panelid within our providers.
        provider = next((x for x in self.panels if x.panel_id == panelid), None)
        if not provider:
            raise cherrypy.HTTPError(404)

        # Render the page.
        template, params = provider.render_prefs_panel(panelid, **kwargs)

        # Create a params with a default panelid.
        params.update(
            {
                "panels": [(x.panel_id, x.panel_name) for x in self.panels],
                "active_panelid": panelid,
                "template_content": template,
            }
        )

        return self._compile_template("prefs.html", **params)
