#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 Patrik Dufresne Service Logiciel
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
"""
Plugin used to send email to users when their repository is getting too old.
User can control the notification period.
"""
from __future__ import unicode_literals

import logging
from rdiffweb.controller import Controller
from rdiffweb.core import RdiffError, RdiffWarning
from rdiffweb.core.i18n import ugettext as _

from builtins import str
import cherrypy

_logger = logging.getLogger(__name__)


class NotificationPref(Controller):

    panel_id = 'notification'
    
    panel_name = _('Notification')
    
    def _handle_set_notification_info(self, **kwargs):

        # Loop trough user repo and update max age.
        for repo in self.app.currentuser.repo_objs:
            # Get value received for the repo.
            value = kwargs.get(repo.name, None)
            if value is None:
                continue
            try:
                value = int(value)
            except:
                continue
            # Update the maxage
            repo.maxage = value

    def render_prefs_panel(self, panelid, **kwargs):  # @UnusedVariable
        # Process the parameters.
        params = dict()
        action = kwargs.get('action')
        if action:
            try:
                if action == "set_notification_info":
                    self._handle_set_notification_info(**kwargs)
                else:
                    _logger.info("unknown action: %s", action)
                    raise cherrypy.NotFound("Unknown action")
            except RdiffWarning as e:
                params['warning'] = str(e)
            except RdiffError as e:
                params['error'] = str(e)
            except Exception as e:
                _logger.warning("unknown error processing action", exc_info=True)
                params['error'] = _("Unknown error")

        params.update({
            'email': self.app.currentuser.email,
            'repos': [
                {'name': r.name, 'maxage': r.maxage}
                for r in self.app.currentuser.repo_objs],
        })
        return "prefs_notification.html", params

