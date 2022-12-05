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


import logging

import cherrypy
from wtforms.fields import DateField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Optional

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.model import Token
from rdiffweb.tools.i18n import gettext_lazy as _

logger = logging.getLogger(__name__)


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
    expiration = DateField(
        _('Expiration date'),
        description=_(
            'Allows the creation of a temporary token by defining an expiration date. Leave empty to keep the token forever.'
        ),
        render_kw={
            "placeholder": _('YYYY-MM-DD'),
        },
        validators=[Optional()],
    )
    add_access_token = SubmitField(_('Create access token'))

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.add_access_token.data

    def populate_obj(self, userobj):
        try:
            token = userobj.add_access_token(self.name.data, self.expiration.data)
            userobj.commit()
            flash(
                _(
                    "Your new personal access token has been created.\n"
                    "Make sure to save it - you won't be able to access it again.\n"
                    "%s"
                )
                % token,
                level='info',
            )
        except ValueError as e:
            userobj.rollback()
            flash(str(e), level='warning')
        except Exception:
            userobj.rollback()
            logger.exception("error adding access token: %s, %s" % (self.name.data, self.expiration.data))
            flash(_("Unknown error while adding the access token."), level='error')


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
        except ValueError as e:
            userobj.rollback()
            flash(str(e), level='warning')
        except Exception:
            userobj.rollback()
            logger.exception("error removing access token: %s" % self.name.data)
            flash(_("Unknown error while removing the access token."), level='error')


class PagePrefTokens(Controller):
    @cherrypy.expose
    def default(self, action=None, **kwargs):
        form = TokenForm()
        delete_form = DeleteTokenForm()
        if form.is_submitted():
            if form.validate():
                form.populate_obj(self.app.currentuser)
            else:
                flash(form.error_message, level='error')
        elif delete_form.is_submitted():
            if delete_form.validate():
                delete_form.populate_obj(self.app.currentuser)
            else:
                flash(delete_form.error_message, level='error')
        params = {
            'form': form,
            'tokens': Token.query.filter(Token.userid == self.app.currentuser.userid),
        }
        return self._compile_template("prefs_tokens.html", **params)
