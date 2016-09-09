#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 Patrik Dufresne Service Logiciel
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

from builtins import str
import cherrypy
from datetime import date
import logging
import os

from rdiffweb.core import RdiffError, RdiffWarning
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_plugin import IPreferencesPanelProvider

from . import authorizedkeys


_logger = logging.getLogger(__name__)


class SSHKeysPlugin(IPreferencesPanelProvider):
    """
    Plugin to configure SSH keys.
    """

    def get_prefs_panels(self):
        """
        Return a single page.
        """
        yield ('sshkeys', _('SSH Keys'))

    def _handle_add(self, filename, **kwargs):
        """
        Called to add a new key to an authorized_keys file.
        """
        assert 'key' in kwargs, "key is missing"

        # Validate the content of the key.
        try:
            key = authorizedkeys.check_publickey(kwargs['key'])
        except:
            raise RdiffWarning(_("Invalid SSH key."))

        # Check if already exists
        if authorizedkeys.exists(filename, key):
            raise RdiffWarning(_("SSH key already exists."))

        # Check size.
        if key.size and key.size < 2048:
            raise RdiffWarning(_("SSH key is too short. RSA key of at least 2048 bits is required."))

        # Add comment to the key.
        comment = key.comment
        if 'title' in kwargs:
            comment = kwargs['title'].strip()

        key = authorizedkeys.KeySplit(
            lineno=key.lineno,
            options=key.options,
            keytype=key.keytype,
            key=key.key,
            comment=comment)

        # Add key to file
        _logger.info("add key [%s] to [%s]", key, filename)
        authorizedkeys.add(filename, key)

    def _handle_delete(self, filename, **kwargs):
        """
        Called for delete a key from an authorized_keys file.
        """

        # Check if key is valid.
        assert 'key' in kwargs, "key is missing"
        lineno = int(kwargs['key'])

        # Remove the key
        _logger.info("removing key [%s] from [%s]", lineno, filename)
        authorizedkeys.remove(filename, lineno)

    def render_prefs_panel(self, panelid, **kwargs):  # @UnusedVariable
        # Get user root directory
        filename = None
        user_root = self.app.currentuser.user_root
        if user_root:
            filename = os.path.join(user_root, '.ssh', 'authorized_keys')

        # Handle action
        params = {}
        if 'action' in kwargs:
            try:
                action = kwargs['action']
                if action == 'add':
                    self._handle_add(filename, **kwargs)
                elif action == 'delete':
                    self._handle_delete(filename, **kwargs)
            except RdiffWarning as e:
                params['warning'] = str(e)
            except RdiffError as e:
                params['error'] = str(e)
            except Exception as e:
                _logger.warning("unknown error processing action", exc_info=True)
                params['error'] = _("Unknown error")

        # Get SSH keys if file exists.
        params["sshkeys"] = []
        if filename:
            try:
                params["sshkeys"] = [
                    {'title': key.comment or (key.keytype + ' ' + key.key[:18]),
                     'fingerprint': key.fingerprint,
                     'lineno': key.lineno}
                    for key in authorizedkeys.read(filename)]
            except IOError:
                params['error'] = _("error reading SSH keys file")
                _logger.warning("error reading SSH keys file [%s]", filename)
        else:
            params['error'] = _("error reading SSH keys file")
            _logger.warning("SSH keys file [%s] is not accessible", filename)

        return "prefs_sshkeys.html", params
