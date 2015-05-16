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

from rdiffweb import page_main
from rdiffweb import rdw_plugin
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_helpers import unquote_url, decode_s

# Define the logger
logger = logging.getLogger(__name__)


class PreferencesPage(page_main.MainPage):

    def _cp_dispatch(self, vpath):
        """
        Used to dispatch `/prefs/<panelid>`
        The `panelid` make reference to a plugin panel.
        """
        # Notice vpath contains bytes.
        if len(vpath) > 0:
            # /the/full/path/
            path = []
            while len(vpath) > 0:
                path.append(decode_s(unquote_url(vpath.pop(0))))
            cherrypy.request.params['panelid'] = "/".join(path)
            return self
        return vpath

    @cherrypy.expose
    def index(self, panelid="", **kwargs):

        # Get the panels
        panels, providers = self._get_panels()
        if not panels:
            raise cherrypy.HTTPError(message=_("No user prefs panels available. Check your config."))

        # Sort the panels to have a deterministic order.
        def _panel_order(p1, p2):
            if p1[0] == 'general':
                if p2[0] == 'general':
                    return cmp(p1[1:], p2[1:])
                return -1
            elif p2[0] == 'general':
                return 1
            return cmp(p1, p2)
        panels.sort(_panel_order)

        # Select the right panelid. Default to the first one if not define by url.
        panelid = panelid or panels[0][0]

        # Search the panelid withint our providers.
        provider = providers.get(panelid)
        if not provider:
            raise cherrypy.HTTPError(message=_("Unknown user prefs panel."))

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
                assert isinstance(panelid, basestring)
                assert isinstance(panelname, basestring)
                panels.append((panelid, panelname))
                providers[panelid] = x

        # Add panel entry for each plugins.
        self.app.plugins.run(
            add_panelid,
            rdw_plugin.IPreferencesPanelProvider.CATEGORY)

        return panels, providers
