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
Plugins to allows users to configure the SSH keys using the web
interface. Basically it's a UI for `~/.ssh/authorized_keys`. For this
plugin to work properly, the users home directory need to match a real
user home.
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
import os
from rdiffweb.controller import Controller
from rdiffweb.core import RdiffError, RdiffWarning
from rdiffweb.core import authorizedkeys
from rdiffweb.core.i18n import ugettext as _

from builtins import str

_logger = logging.getLogger(__name__)


class SSHKeysPlugin(Controller):
    """
    Plugin to configure SSH keys.
    """

    panel_id = 'sshkeys'
    
    panel_name = _('SSH Keys')
    
    def _handle_add(self, **kwargs):
        """
        Called to add a new key to an authorized_keys file.
        """
        assert 'key' in kwargs, "key is missing"

        # Add the key to the current user.
        try:
            self.app.currentuser.add_authorizedkey(key=kwargs['key'], comment=kwargs.get('title', None))
        except ValueError as e:
            _logger.warn("error adding ssh key", exc_info=1)
            raise RdiffWarning(e.message)
        except:
            _logger.warn("error adding ssh key", exc_info=1)
            raise RdiffWarning(_("Unknown error while adding the SSH Key"))

    def _handle_delete(self, **kwargs):
        """
        Called for delete a key from an authorized_keys file.
        """
        assert kwargs.get('key') , "key is missing"
        try:
            self.app.currentuser.remove_authorizedkey(key=kwargs['key'])
        except:
            _logger.warn("error removing ssh key", exc_info=1)
            raise RdiffWarning(_("Unknown error while removing the SSH Key"))

    def render_prefs_panel(self, panelid, **kwargs):  # @UnusedVariable

        # Handle action
        params = {}
        if 'action' in kwargs:
            try:
                action = kwargs['action']
                if action == 'add':
                    self._handle_add(**kwargs)
                elif action == 'delete':
                    self._handle_delete(**kwargs)
            except RdiffWarning as e:
                params['warning'] = str(e)
            except RdiffError as e:
                params['error'] = str(e)

        # Get SSH keys if file exists.
        params["sshkeys"] = []
        try:
            params["sshkeys"] = [
                {'title': key.comment or (key.keytype + ' ' + key.key[:18]),
                 'fingerprint': key.fingerprint}
                for key in self.app.currentuser.authorizedkeys]
        except IOError:
            params['error'] = _("error reading SSH keys file")
            _logger.warning("error reading SSH keys", exc_info=1)

        return "prefs_sshkeys.html", params
