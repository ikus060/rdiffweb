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
"""
Plugins to allows users to configure the SSH keys using the web
interface. Basically it's a UI for `~/.ssh/authorized_keys`. For this
plugin to work properly, the users home directory need to match a real
user home.
"""

import cherrypy
from cherrypy_foundation.flash import flash
from cherrypy_foundation.tools.i18n import gettext_lazy as _
from wtforms import validators
from wtforms.fields import HiddenField, StringField
from wtforms.validators import ValidationError
from wtforms.widgets.core import TextArea

from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.controller.formdb import DbForm
from rdiffweb.core import authorizedkeys


def validate_key(unused_form, field):
    """Custom validator to check the SSH Key."""
    try:
        authorizedkeys.check_publickey(field.data)
    except ValueError:
        raise ValidationError(_("Invalid SSH key."))


class SshForm(DbForm):
    action = HiddenField(default="add")
    title = StringField(
        _('Key Name'),
        description=_('Give this key a recognizable name so you can identify it later.'),
        validators=[
            validators.data_required(),
            validators.length(
                max=256,
                message=_('Title too long.'),
            ),
        ],
        render_kw={"placeholder": _("e.g. My laptop, Work desktop…")},
    )
    key = StringField(
        _('Public Key'),
        widget=TextArea(),
        description=_("Begins with ssh-rsa, ssh-ed25519, ecdsa-sha2-nistp256, etc."),
        validators=[validators.data_required(), validate_key],
        render_kw={"placeholder": _("ssh-ed25519 AAAA... or ssh-rsa AAAA...")},
    )

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.action.default in self.action.raw_data

    def populate_obj(self, userobj):
        userobj.add_authorizedkey(key=self.key.data, comment=self.title.data)


class DeleteSshForm(DbForm):
    action = HiddenField(default="delete")
    fingerprint = StringField('Fingerprint', validators=[validators.data_required()])

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.action.default in self.action.raw_data

    def populate_obj(self, userobj):
        is_maintainer()
        userobj.delete_authorizedkey(self.fingerprint.data)


class PagePrefSshKeys:
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    @cherrypy.tools.jinja2(template="prefs_sshkeys.html")
    def default(self, **kwargs):
        """
        Show user's SSH keys
        """
        currentuser = cherrypy.serving.request.currentuser
        cfg = cherrypy.tree.apps[''].cfg
        # Handle action
        form = SshForm()
        delete_form = DeleteSshForm()
        if not cfg.disable_ssh_keys:
            if form.validate_on_submit():
                if form.save_to_db(currentuser):
                    raise cherrypy.HTTPRedirect("")
            elif delete_form.validate_on_submit():
                if delete_form.save_to_db(currentuser):
                    raise cherrypy.HTTPRedirect("")
            if form.error_message:
                flash(form.error_message, level='warning')
            if delete_form.error_message:
                flash(delete_form.error_message, level='warning')
        # Get SSH keys if file exists.
        params = {
            'disable_ssh_keys': cfg.disable_ssh_keys,
            'form': form,
            'sshkeys': currentuser.authorizedkeys,
        }
        return params


@cherrypy.expose
@cherrypy.tools.json_out()
class ApiSshKeys:
    def list(self):
        """
        List current user keys

        Returns a list of registered public SSH keys for the current user.

        **Example Response**

        ```json
        [{"title": "my-laptop", "fingerprint": "b5:f0:40:ee:41:53:9d:68:e1:9b:02:3e:39:99:a8:9b"}]
        ```

        **Fields in JSON Payload**

        - `title`: The title or name associated with the SSH key.
        - `fingerprint`: The fingerprint of the public SSH key.

        """
        currentuser = cherrypy.serving.request.currentuser
        return [{'title': key.comment, 'fingerprint': key.fingerprint} for key in currentuser.authorizedkeys]

    def get(self, fingerprint):
        """
        Return SSH key for given fingerprint

        Returns SSH key information identified by `<fingerprint>`.

        **Example Response**

        ```json
        {"title": "my-laptop", "fingerprint": "b5:f0:40:ee:41:53:9d:68:e1:9b:02:3e:39:99:a8:9b"}
        ```
        """
        currentuser = cherrypy.serving.request.currentuser
        for key in currentuser.authorizedkeys:
            if key.fingerprint == fingerprint:
                return {'title': key.comment, 'fingerprint': key.fingerprint}
        raise cherrypy.HTTPError(404)

    @cherrypy.tools.required_scope(scope='all,write_user')
    def delete(self, fingerprint):
        """
        Delete a SSH key

        Deletes the SSH key identified by `<fingerprint>`.

        Returns status 200 OK on success.
        """
        currentuser = cherrypy.serving.request.currentuser
        form = DeleteSshForm(fingerprint=fingerprint)
        if form.validate() and form.save_to_db(currentuser):
            return {}
        raise cherrypy.HTTPError(400, form.error_message)

    @cherrypy.tools.required_scope(scope='all,write_user')
    def post(self, **kwargs):
        """
        Add a SSH key to current user

        Registers a new public SSH key for the current user.
        """
        currentuser = cherrypy.serving.request.currentuser
        # Validate input data.
        form = SshForm(json=1)
        if form.strict_validate():
            # Create the SSH Key
            if form.save_to_db(currentuser):
                return kwargs
        raise cherrypy.HTTPError(400, form.error_message)
