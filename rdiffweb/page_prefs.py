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

from builtins import str
import cherrypy
import logging

from rdiffweb import page_main
from rdiffweb import rdw_plugin


# Define the logger
logger = logging.getLogger(__name__)


@cherrypy.popargs('panelid')
class PreferencesPage(page_main.MainPage):

    @cherrypy.expose
    def index(self, panelid=None, **kwargs):
        if isinstance(panelid, bytes):
            panelid = panelid.decode('ascii')

        # Get the panels
        panels, providers = self._get_panels()

        # Sort the panels to have a deterministic order. (Place general panel first)
        panels.sort(key=lambda p: (-1 if p[0] == 'general' else 0, p[1]))

        # Select the right panelid. Default to the first one if not define by url.
        template = None
        params = dict()
        if panels:
            panelid = panelid or panels[0][0]

            # Search the panelid within our providers.
            provider = providers.get(panelid)
            if not provider:
                raise cherrypy.HTTPError(404)

            # Render the page.
            template, params = provider.render_prefs_panel(panelid, **kwargs)

        # Create a params with a default panelid.
        params.update({
            "panels": panels,
            "active_panelid": panelid,
            "template_content": template,
        })

        return self._compile_template("prefs.html", **params)

    def _get_panels(self):
        """
        List all the panels available.
        """
        panels = list()
        providers = dict()

        # List panels
        def add_panelid(x):
            p = list(x.get_prefs_panels() or [])
            for panelid, panelname in p:
                assert isinstance(panelid, str)
                assert isinstance(panelname, str)
                panels.append((panelid, panelname))
                providers[panelid] = x

        # Add panel entry for each plugins.
        self.app.plugins.run(
            add_panelid,
            rdw_plugin.IPreferencesPanelProvider.CATEGORY)

        return panels, providers
