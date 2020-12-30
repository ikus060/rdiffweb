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

import logging

from wtforms import validators
from wtforms.fields.core import StringField
from wtforms.fields.simple import TextField
from wtforms.validators import ValidationError
from wtforms.widgets.core import TextArea

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.cherrypy_wtf import CherryForm
from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.core import authorizedkeys
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.store import DuplicateSSHKeyError


_logger = logging.getLogger(__name__)


def validate_key(unused_form, field):
    """Custom validator to check the SSH Key."""
    key = authorizedkeys.check_publickey(field.data)
    if not key:
        raise ValidationError(_("Invalid SSH key."))


class SSHForm(CherryForm):
    title = StringField(
        _('Title'),
        description=_('The title is an optional description to identify the key. e.g.: bob@thinkpad-t530'),
        validators=[validators.required()])
    key = TextField(
        _('Key'),
        widget=TextArea(),
        description=_("Enter a SSH public key. It should start with 'ssh-dss', 'ssh-ed25519', 'ssh-rsa', 'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384' or 'ecdsa-sha2-nistp521'."),
        validators=[validators.required(), validate_key])
    fingerprint = StringField('Fingerprint')


class SSHKeysPlugin(Controller):
    """
    Plugin to configure SSH keys.
    """

    panel_id = 'sshkeys'

    panel_name = _('SSH Keys')

    def render_prefs_panel(self, panelid, action=None, **kwargs):  # @UnusedVariable

        # Handle action
        form = SSHForm()
        if action == "add" and not form.validate():
            for unused_field, messages in form.errors.items():
                for message in messages:
                    flash(message, level='warning')
        elif action == 'add':
            # Add the key to the current user.
            try:
                self.app.currentuser.add_authorizedkey(key=form.key.data, comment=form.title.data)
            except DuplicateSSHKeyError as e:
                flash(str(e), level='error')
            except:
                flash(_("Unknown error while adding the SSH Key"), level='error')
                _logger.warning("error adding ssh key", exc_info=1)
        elif action == 'delete':
            is_maintainer()
            try:
                self.app.currentuser.delete_authorizedkey(form.fingerprint.data)
            except:
                flash(_("Unknown error while removing the SSH Key"), level='error')
                _logger.warning("error removing ssh key", exc_info=1)

        # Get SSH keys if file exists.
        params = {
            'form': form
        }
        try:
            params["sshkeys"] = [
                {'title': key.comment or (key.keytype + ' ' + key.key[:18]),
                 'fingerprint': key.fingerprint}
                for key in self.app.currentuser.authorizedkeys]
        except IOError:
            params["sshkeys"] = []
            flash(_("Failed to get SSH keys"), level='error')
            _logger.warning("error reading SSH keys", exc_info=1)

        return "prefs_sshkeys.html", params
