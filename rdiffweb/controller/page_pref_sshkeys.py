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

import cherrypy
from wtforms import validators
from wtforms.fields import StringField
from wtforms.validators import ValidationError
from wtforms.widgets.core import TextArea

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.dispatch import restapi
from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.controller.form import CherryForm
from rdiffweb.core import authorizedkeys
from rdiffweb.core.model import DuplicateSSHKeyError
from rdiffweb.tools.i18n import gettext_lazy as _

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

    def populate_obj(self, userobj):
        try:
            userobj.add_authorizedkey(key=self.key.data, comment=self.title.data)
            userobj.commit()
        except DuplicateSSHKeyError as e:
            userobj.rollback()
            flash(str(e), level='error')
            _logger.warning("trying to add duplicate ssh key")
        except Exception:
            userobj.rollback()
            flash(_("Unknown error while adding the SSH Key"), level='error')
            _logger.warning("error adding ssh key", exc_info=1)


class DeleteSshForm(CherryForm):
    fingerprint = StringField('Fingerprint', validators=[validators.data_required()])

    def populate_obj(self, userobj):
        is_maintainer()
        try:
            userobj.delete_authorizedkey(self.fingerprint.data)
            userobj.commit()
        except Exception:
            userobj.rollback()
            if hasattr(cherrypy.serving, 'session'):
                flash(_("Unknown error while removing the SSH Key"), level='error')
            _logger.warning("error removing ssh key", exc_info=1)


class PagePrefSshKeys(Controller):
    @cherrypy.expose
    def default(self, action=None, **kwargs):

        # Handle action
        form = SshForm()
        delete_form = DeleteSshForm()
        if not self.app.cfg.disable_ssh_keys:
            if action == 'add' and form.is_submitted():
                if form.validate():
                    form.populate_obj(self.app.currentuser)
                else:
                    flash(form.error_message, level='warning')
            elif action == 'delete' and delete_form.is_submitted():
                if delete_form.validate():
                    delete_form.populate_obj(self.app.currentuser)
                else:
                    flash(delete_form.error_message, level='warning')

        # Get SSH keys if file exists.
        params = {
            'disable_ssh_keys': self.app.cfg.disable_ssh_keys,
            'form': form,
        }
        try:
            params["sshkeys"] = [
                {'title': key.comment, 'fingerprint': key.fingerprint} for key in self.app.currentuser.authorizedkeys
            ]
        except IOError:
            params["sshkeys"] = []
            flash(_("Failed to get SSH keys"), level='error')
            _logger.warning("error reading SSH keys", exc_info=1)

        return self._compile_template("prefs_sshkeys.html", **params)


@restapi()
@cherrypy.tools.json_out()
class ApiSshKeys(Controller):
    @cherrypy.expose
    def list(self):
        return [{'title': key.comment, 'fingerprint': key.fingerprint} for key in self.app.currentuser.authorizedkeys]

    @cherrypy.expose
    def get(self, fingerprint):
        for key in self.app.currentuser.authorizedkeys:
            if key.fingerprint == fingerprint:
                return {'title': key.comment, 'fingerprint': key.fingerprint}
        raise cherrypy.HTTPError(404)

    @cherrypy.expose
    def delete(self, fingerprint):
        form = DeleteSshForm(fingerprint=fingerprint)
        if form.validate():
            form.populate_obj(self.app.currentuser)
            return {}
        else:
            raise cherrypy.HTTPError(400, form.error_message)

    @cherrypy.expose
    def post(self, **kwargs):
        form = SshForm()
        if form.validate():
            # Create the SSH Key
            userobj = self.app.currentuser
            try:
                userobj.add_authorizedkey(key=form.key.data, comment=form.title.data)
                userobj.commit()
            except DuplicateSSHKeyError as e:
                userobj.rollback()
                raise cherrypy.HTTPError(400, str(e))
            return kwargs
        else:
            raise cherrypy.HTTPError(400, form.error_message)
