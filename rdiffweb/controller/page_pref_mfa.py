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


import cherrypy
from wtforms.fields import SelectField, StringField, SubmitField
from wtforms.validators import ValidationError
from wtforms.widgets import HiddenInput

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.model import UserObject
from rdiffweb.tools.i18n import gettext_lazy as _


class AbstractMfaForm(CherryForm):
    def __init__(self, obj, **kwargs):
        assert obj
        super().__init__(obj=obj, **kwargs)
        # Keep only one of the enable or disable button
        if obj.mfa:
            self.enable_mfa.widget = HiddenInput()
            self.enable_mfa.data = ''
        else:
            self.disable_mfa.widget = HiddenInput()
            self.disable_mfa.data = ''


class MfaStatusForm(AbstractMfaForm):
    mfa = SelectField(
        _('Two-Factor Authentication (2FA) Status'),
        coerce=int,
        choices=[
            (UserObject.DISABLED_MFA, _("Disabled")),
            (UserObject.ENABLED_MFA, _("Enabled")),
        ],
        render_kw={'readonly': True, 'disabled': True, 'data-beta': '1'},
    )
    enable_mfa = SubmitField(_('Enable Two-Factor Authentication'), render_kw={"class": "btn-success"})
    disable_mfa = SubmitField(_('Disable Two-Factor Authentication'), render_kw={"class": "btn-warning"})


class MfaToggleForm(AbstractMfaForm):
    code = StringField(
        _('Verification code'),
        render_kw={
            "placeholder": _('Enter verification code here'),
            "autocomplete": "off",
            "autocorrect": "off",
            "autofocus": "autofocus",
        },
    )
    enable_mfa = SubmitField(_('Enable Two-Factor Authentication'), render_kw={"class": "btn-success"})
    disable_mfa = SubmitField(_('Disable Two-Factor Authentication'), render_kw={"class": "btn-warning"})
    resend_code = SubmitField(
        _('Resend code to my email'),
        render_kw={"class": "btn-link"},
    )

    @property
    def app(self):
        return cherrypy.request.app

    def populate_obj(self, userobj):
        # Enable or disable MFA only when a code is provided.
        try:
            if self.enable_mfa.data:
                userobj.mfa = UserObject.ENABLED_MFA
                userobj.commit()
                flash(_("Two-Factor authentication enabled successfully."), level='success')
            elif self.disable_mfa.data:
                userobj.mfa = UserObject.DISABLED_MFA
                userobj.commit()
                flash(_("Two-Factor authentication disabled successfully."), level='success')
        except Exception as e:
            userobj.rollback()
            flash(str(e), level='warning')

    def validate_code(self, field):
        # Code is required for enable_mfa and disable_mfa
        if self.enable_mfa.data or self.disable_mfa.data:
            if not self.code.data:
                raise ValidationError(_("Enter the verification code to continue."))
            # Validate code
            if not cherrypy.tools.auth_mfa.verify_code(self.code.data, False):
                raise ValidationError(_("Invalid verification code."))

    def validate(self, extra_validators=None):
        if not (self.enable_mfa.data or self.disable_mfa.data or self.resend_code.data):
            raise ValidationError(_('Invalid operation'))
        return super().validate()


class PagePrefMfa(Controller):
    @cherrypy.expose
    @cherrypy.tools.ratelimit(methods=['POST'])
    def default(self, action=None, **kwargs):
        form = MfaToggleForm(obj=self.app.currentuser)
        if form.is_submitted():
            if form.validate():
                if form.resend_code.data:
                    self.send_code()
                elif form.enable_mfa.data or form.disable_mfa.data:
                    form.populate_obj(self.app.currentuser)
                    form = MfaStatusForm(obj=self.app.currentuser)
            # Send verification code if previous code expired.
            elif cherrypy.tools.auth_mfa.is_code_expired():
                self.send_code()
        else:
            form = MfaStatusForm(obj=self.app.currentuser)
        params = {
            'form': form,
        }
        return self._compile_template("prefs_mfa.html", **params)

    def send_code(self):
        userobj = self.app.currentuser
        if not userobj.email:
            flash(_("To continue, you must set up an email address for your account."), level='warning')
            return
        code = cherrypy.tools.auth_mfa.generate_code()
        body = self.app.templates.compile_template(
            "email_verification_code.html", **{"header_name": self.app.cfg.header_name, 'user': userobj, 'code': code}
        )
        cherrypy.engine.publish('queue_mail', to=userobj.email, subject=_("Your verification code"), message=body)
        flash(_("A new verification code has been sent to your email."))
