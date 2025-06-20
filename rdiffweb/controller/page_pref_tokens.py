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


import logging

import cherrypy
from markupsafe import Markup, escape
from wtforms.fields import DateTimeField, SelectMultipleField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import html_params

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.model import Token
from rdiffweb.tools.i18n import gettext_lazy as _

try:
    # wtform>=3
    from wtforms.widgets import DateInput
except ImportError:
    # wtform<3
    from wtforms.widgets.html5 import DateInput

logger = logging.getLogger(__name__)


class ScopeField(SelectMultipleField):
    def __init__(self, label=None, **kwargs):
        choices = [
            ('all', _('Everything - Allow read write access to everything.')),
            (
                'read_user',
                _(
                    'Read user settings - Grant read access to your profile, notification settings, ssh keys and access token.'
                ),
            ),
            (
                'write_user',
                _(
                    'Write user settings - Grant write access to your profile, notification settings, ssh keys and access token.'
                ),
            ),
        ]
        # Include admin scope if user is admin.
        # This is only for display.
        currentuser = cherrypy.request.currentuser
        if currentuser.is_admin:
            choices.extend(
                [
                    (
                        'admin_read_users',
                        _('Admin read all user settings - Grant read access to all users data.'),
                    ),
                    (
                        'admin_write_user',
                        _('Admin write all user settings - Grant write access to all users data.'),
                    ),
                ]
            )
        super().__init__(label, choices=choices, **kwargs)

    def process_formdata(self, valuelist):
        try:
            self.data = list(self.coerce(x) for x in valuelist)
        except ValueError as exc:
            raise ValueError(self.gettext("Invalid choice(s): one or more data inputs could not be coerced.")) from exc

    def populate_obj(self, obj, name):
        """
        Populates `obj.<name>` with the field's data.

        :note: This is a destructive operation. If `obj.<name>` already exists,
               it will be overridden. Use with caution.
        """
        setattr(obj, name, self.data)

    def widget(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = []
        for entry in field.iter_choices():
            val = entry[0]
            label = entry[1]
            if ' - ' in label:
                label, description = label.split(' - ', 2)
            else:
                description = ''
            field_id = '%s_%s' % (field.id, val)
            html.append(
                '<div><input type="checkbox" %s/> <label %s data-toggle="tooltip" data-placement="right">%s</label></div>'
                % (
                    html_params(
                        id=field_id,
                        name=field.name,
                        value=val,
                        checked=entry[2],
                    ),
                    html_params(
                        for_=field_id,
                        title=description,
                    ),
                    escape(label),
                )
            )
        return Markup(''.join(html))


class TokenForm(CherryForm):
    name = StringField(
        _('Token name'),
        description=_(
            'Used only to identify the purpose of the token. For example, the application that uses the token.'
        ),
        validators=[
            DataRequired(),
            Length(max=256, message=_('Token name too long')),
        ],
    )
    expiration = DateTimeField(
        _('Expiration date'),
        description=_(
            'Allows the creation of a temporary token by defining an expiration date. Leave empty to keep the token forever.'
        ),
        render_kw={
            "placeholder": _('YYYY-MM-DD'),
        },
        format="%Y-%m-%d",
        widget=DateInput(),
        validators=[Optional()],
    )
    scope = ScopeField(_('Select scopes'), description=_('Scopes set the permissions level of this access token.'))
    add_access_token = SubmitField(_('Create access token'))

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.add_access_token.data

    def populate_obj(self, userobj):
        try:
            secret = userobj.add_access_token(
                name=self.name.data, expiration_time=self.expiration.data, scope=self.scope.data
            )
            userobj.commit()
            flash(
                _(
                    "Your new personal access token has been created.\n"
                    "Make sure to save it - you won't be able to access it again.\n"
                    "%s"
                )
                % secret,
                level='info',
            )
            return True
        except ValueError as e:
            userobj.rollback()
            flash(str(e), level='warning')
            return False
        except Exception:
            userobj.rollback()
            logger.exception("error adding access token: %s, %s" % (self.name.data, self.expiration.data))
            flash(_("Unknown error while adding the access token."), level='error')
            return False


class DeleteTokenForm(CherryForm):
    name = StringField(validators=[DataRequired()])
    revoke = SubmitField(_('Revoke'))

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.revoke.data

    def populate_obj(self, userobj):
        is_maintainer()
        try:
            userobj.delete_access_token(self.name.data)
            flash(_('The access token has been successfully deleted.'), level='success')
            return True
        except ValueError as e:
            userobj.rollback()
            flash(str(e), level='warning')
            return False
        except Exception:
            userobj.rollback()
            logger.exception("error removing access token: %s" % self.name.data)
            flash(_("Unknown error while removing the access token."), level='error')
            return False


class PagePrefTokens(Controller):
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    def default(self, **kwargs):
        """
        Show current user access token
        """
        form = TokenForm()
        delete_form = DeleteTokenForm()
        if form.is_submitted():
            if form.validate():
                if form.populate_obj(self.app.currentuser):
                    raise cherrypy.HTTPRedirect("")
            else:
                flash(form.error_message, level='error')
        elif delete_form.is_submitted():
            if delete_form.validate():
                if delete_form.populate_obj(self.app.currentuser):
                    raise cherrypy.HTTPRedirect("")
            else:
                flash(delete_form.error_message, level='error')
        params = {
            'form': form,
            'tokens': Token.query.filter(Token.userid == self.app.currentuser.userid),
        }
        return self._compile_template("prefs_tokens.html", **params)


@cherrypy.expose
@cherrypy.tools.json_out()
class ApiTokens(Controller):
    def _query(self, name):
        token = Token.query.filter(Token.userid == self.app.currentuser.userid, Token.name == name).first()
        if not token:
            raise cherrypy.NotFound()
        return token

    def _to_json(self, token):
        return {
            'title': token.name,
            'access_time': token.access_time,
            'creation_time': token.creation_time,
            'expiration_time': token.expiration_time,
            'scope': token.scope,
        }

    def list(self):
        """
        Return list of current user access token

        Lists the access tokens associated with the current user.

        **Example Response**

        ```json
        [
            {"title": "<h1>hold</h1>", "access_time": null, "creation_time": "2023-11-09T04:31:18Z", "expiration_time": null},
            {"title": "test2", "access_time": "2024-01-30T17:59:08Z", "creation_time": "2024-01-30T17:57:51Z", "expiration_time": null}
        ]
        ```

        **Fields in JSON Payload**

        - `title`: The title or name of the access token.
        - `access_time`: The time of the last access using the token (null if never used).
        - `creation_time`: The creation time of the access token.
        - `expiration_time`: The time when the access token expires (null if never expires).

        """
        tokens = Token.query.filter(Token.userid == self.app.currentuser.userid).all()
        return [self._to_json(token) for token in tokens]

    def get(self, name):
        """
        Return a specific access token info

        Returns access token information identified by `<name>`.

        **Example Response**

        ```json
        {"title": "test2", "access_time": "2024-01-30T17:59:08Z", "creation_time": "2024-01-30T17:57:51Z", "expiration_time": null}
        ```
        """
        token = self._query(name)
        return self._to_json(token)

    @cherrypy.tools.required_scope(scope='all,write_user')
    def delete(self, name):
        """
        Delete a specific access token.

        Revokes the access token identified by `<title>`.

        Returns status 200 OK on success.
        """
        userobj = self.app.currentuser
        self._query(name)
        userobj.delete_access_token(name)
        userobj.commit()
        return {}

    @cherrypy.tools.required_scope(scope='all,write_user')
    def post(self, **kwargs):
        """
        Create a new access token

        Returns status 200 OK on success.
        """
        # Validate input data.
        form = TokenForm(json=1)
        if not form.strict_validate():
            raise cherrypy.HTTPError(400, form.error_message)

        # Create the Access Token
        userobj = self.app.currentuser
        try:
            secret = userobj.add_access_token(
                name=form.name.data, expiration_time=form.expiration.data, scope=form.scope.data
            )
            userobj.commit()
            token = self._query(form.name.data)
            # Return token info as Json
            data = self._to_json(token)
            data['token'] = secret
            return data
        except Exception as e:
            userobj.rollback()
            raise cherrypy.HTTPError(400, str(e))
