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
from wtforms.fields import BooleanField, StringField, SubmitField
from wtforms.validators import ValidationError

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.tools.auth_form import LOGIN_PERSISTENT
from rdiffweb.tools.i18n import gettext_lazy as _

# Define the logger
logger = logging.getLogger(__name__)


class MfaForm(CherryForm):
    code = StringField(
        _('Verification code'),
        render_kw={
            "class": "form-control-lg",
            "placeholder": _('Enter verification code here'),
            "autocomplete": "off",
            "autocorrect": "off",
            "autofocus": "autofocus",
        },
    )
    persistent = BooleanField(
        _('Remember me'),
        default=lambda: cherrypy.session.get(LOGIN_PERSISTENT, False),
    )
    submit = SubmitField(
        _('Sign in'),
        render_kw={"class": "btn-primary btn-lg btn-block"},
    )
    resend_code = SubmitField(
        _('Resend code to my email'),
        render_kw={"class": "btn-link btn-sm btn-block"},
    )

    def validate_code(self, field):
        # Code is required when submit.
        if self.submit.data:
            if not self.code.data:
                raise ValidationError(_('Invalid verification code.'))
            # Validate verification code.
            if not cherrypy.tools.auth_mfa.verify_code(code=self.code.data, persistent=self.persistent.data):
                raise ValidationError(_('Invalid verification code.'))

    def validate(self, extra_validators=None):
        if not (self.submit.data or self.resend_code.data):
            raise ValidationError(_('Invalid operation'))
        return super().validate()


class MfaPage(Controller):
    @cherrypy.expose()
    @cherrypy.tools.ratelimit(methods=['POST'])
    def index(self, **kwargs):
        form = MfaForm()

        # Validate MFA
        if form.is_submitted():
            if form.validate():
                if form.submit.data:
                    cherrypy.tools.auth_mfa.redirect_to_original_url()
                elif form.resend_code.data:
                    self.send_code()
        if cherrypy.tools.auth_mfa.is_code_expired():
            # Send verification code if previous code expired.
            self.send_code()
        params = {
            'form': form,
        }
        # Add welcome message to params. Try to load translated message.
        welcome_msg = self.app.cfg.welcome_msg
        if welcome_msg:
            params["welcome_msg"] = welcome_msg.get('')
            if hasattr(cherrypy.response, 'i18n'):
                locale = cherrypy.response.i18n.locale.language
                params["welcome_msg"] = welcome_msg.get(locale, params["welcome_msg"])
        return self._compile_template("mfa.html", **params)

    def send_code(self):
        # Send verification code by email
        userobj = cherrypy.serving.request.currentuser
        if not userobj.email:
            flash(
                _(
                    "Multi-factor authentication is enabled for your account, but your account does not have a valid email address to send the verification code to. Check your account settings with your administrator."
                )
            )
            return
        code = cherrypy.tools.auth_mfa.generate_code()
        body = self.app.templates.compile_template(
            "email_verification_code.html", **{"header_name": self.app.cfg.header_name, 'user': userobj, 'code': code}
        )
        cherrypy.engine.publish('queue_mail', to=userobj.email, subject=_("Your verification code"), message=body)
        flash(_("A new verification code has been sent to your email."))
