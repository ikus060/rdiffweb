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
from cherrypy_foundation.flash import flash
from cherrypy_foundation.form import CherryForm
from cherrypy_foundation.tools.i18n import get_translation
from cherrypy_foundation.tools.i18n import gettext_lazy as _
from wtforms.fields import BooleanField, StringField, SubmitField
from wtforms.validators import ValidationError

# Define the logger
logger = logging.getLogger(__name__)


class MfaForm(CherryForm):
    code = StringField(
        _('Verification code'),
        # Trim spaces
        filters=[lambda v: v.strip() if v else v],
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
        default=lambda: cherrypy.tools.sessions_timeout.is_persistent(),
        render_kw={"container_class": "col-6"},
    )
    resend_code = SubmitField(
        _('Resend code to my email'),
        render_kw={"class": "col btn-link btn-sm btn-block", "container_class": "col-6"},
    )

    def validate_code(self, field):
        if self.resend_code.data:
            return
        # Code is required when submit.
        if not self.code.data:
            raise ValidationError(_('Invalid verification code.'))
        # Validate verification code.
        if not cherrypy.tools.auth_mfa.verify_code(code=self.code.data, persistent=self.persistent.data):
            raise ValidationError(_('Invalid verification code.'))


class MfaPage:
    @cherrypy.expose()
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    @cherrypy.tools.jinja2(template="mfa.html")
    def index(self, **kwargs):
        """
        Show Multi Factor Authentication form
        """
        form = MfaForm()

        # Validate MFA
        if form.validate_on_submit():
            if form.resend_code.data:
                self.send_code()
            else:
                raise cherrypy.tools.auth.redirect_to_original_url()
        if cherrypy.tools.auth_mfa.is_code_expired():
            # Send verification code if previous code expired.
            self.send_code()
        params = {
            'form': form,
        }
        # Add welcome message to params. Try to load translated message.
        cfg = cherrypy.tree.apps[''].cfg
        welcome_msg = cfg.welcome_msg
        if welcome_msg:
            default_welcome_msg = welcome_msg.get('')
            lang = get_translation().locale.language
            params["welcome_msg"] = welcome_msg.get(lang, default_welcome_msg)
        return params

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
        cherrypy.notification._queue_mail(
            userobj,
            template="email_verification_code.html",
            code=code,
        )
        flash(_("A new verification code has been sent to your email."))
