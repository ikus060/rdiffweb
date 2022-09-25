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
"""
Plugins to allows users to configure the SSH keys using the web
interface. Basically it's a UI for `~/.ssh/authorized_keys`. For this
plugin to work properly, the users home directory need to match a real
user home.
"""

import logging

from wtforms import validators
from wtforms.fields.core import StringField
from wtforms.validators import ValidationError
from wtforms.widgets.core import TextArea

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.cherrypy_wtf import CherryForm
from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.core import authorizedkeys
from rdiffweb.core.store import DuplicateSSHKeyError
from rdiffweb.tools.i18n import ugettext as _

_logger = logging.getLogger(__name__)


def validate_key(unused_form, field):
    """Custom validator to check the SSH Key."""
    try:
        authorizedkeys.check_publickey(field.data)
    except ValueError:
        raise ValidationError(_("Invalid SSH key."))


class SshForm(CherryForm):
    title = StringField(
        _('Title'),
        description=_('The title is an optional description to identify the key. e.g.: bob@thinkpad-t530'),
        validators=[
            validators.data_required(),
            validators.length(
                max=256,
                message=_('Title too long.'),
            ),
        ],
    )
    key = StringField(
        _('Key'),
        widget=TextArea(),
        description=_(
            "Enter a SSH public key. It should start with 'ssh-dss', 'ssh-ed25519', 'ssh-rsa', 'ecdsa-sha2-nistp256', 'ecdsa-sha2-nistp384' or 'ecdsa-sha2-nistp521'."
        ),
        validators=[validators.data_required(), validate_key],
    )
    fingerprint = StringField('Fingerprint')


class DeleteSshForm(CherryForm):
    fingerprint = StringField('Fingerprint')


class SSHKeysPlugin(Controller):
    """
    Plugin to configure SSH keys.
    """

    panel_id = 'sshkeys'

    panel_name = _('SSH Keys')

    def _add_key(self, action, form):
        assert action == 'add'
        assert form
        if not form.validate():
            for unused, messages in form.errors.items():
                for message in messages:
                    flash(message, level='warning')
            return
        try:
            self.app.currentuser.add_authorizedkey(key=form.key.data, comment=form.title.data)
        except DuplicateSSHKeyError as e:
            flash(str(e), level='error')
        except Exception:
            flash(_("Unknown error while adding the SSH Key"), level='error')
            _logger.warning("error adding ssh key", exc_info=1)

    def _delete_key(self, action, form):
        assert action == 'delete'
        assert form
        if not form.validate():
            for unused, messages in form.errors.items():
                for message in messages:
                    flash(message, level='warning')
            return
        is_maintainer()
        try:
            self.app.currentuser.delete_authorizedkey(form.fingerprint.data)
        except Exception:
            flash(_("Unknown error while removing the SSH Key"), level='error')
            _logger.warning("error removing ssh key", exc_info=1)

    def render_prefs_panel(self, panelid, action=None, **kwargs):  # @UnusedVariable

        # Handle action
        form = SshForm()
        delete_form = DeleteSshForm()
        if action == "add" and form.is_submitted():
            self._add_key(action, form)
        elif action == 'delete' and delete_form.is_submitted():
            self._delete_key(action, DeleteSshForm())

        # Get SSH keys if file exists.
        params = {'form': form}
        try:
            params["sshkeys"] = [
                {'title': key.comment or (key.keytype + ' ' + key.key[:18]), 'fingerprint': key.fingerprint}
                for key in self.app.currentuser.authorizedkeys
            ]
        except IOError:
            params["sshkeys"] = []
            flash(_("Failed to get SSH keys"), level='error')
            _logger.warning("error reading SSH keys", exc_info=1)

        return "prefs_sshkeys.html", params
