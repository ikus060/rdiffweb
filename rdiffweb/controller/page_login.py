# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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
from wtforms.fields import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import InputRequired, Length

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.tools.auth_form import LOGIN_PERSISTENT, SESSION_KEY
from rdiffweb.tools.i18n import get_translation
from rdiffweb.tools.i18n import gettext_lazy as _

# Define the logger
logger = logging.getLogger(__name__)


class LoginForm(CherryForm):
    # Sanitize the redirect URL to avoid Open Redirect
    # redirect = HiddenField(default='/', filters=[lambda v: v if v.startswith('/') else '/'])
    login = StringField(
        _('Username'),
        default=lambda: cherrypy.session.get(SESSION_KEY, None),
        validators=[InputRequired(), Length(max=256, message=_('Username too long.'))],
        render_kw={
            "placeholder": _('Username'),
            "autocorrect": "off",
            "autocapitalize": "none",
            "autocomplete": "off",
            "autofocus": "autofocus",
        },
    )
    password = PasswordField(_('Password'), validators=[InputRequired()], render_kw={"placeholder": _('Password')})
    persistent = BooleanField(
        _('Remember me'),
        default=lambda: cherrypy.session.get(LOGIN_PERSISTENT, False),
    )
    submit = SubmitField(
        _('Sign in'),
        render_kw={"class": "btn-primary btn-lg btn-block"},
    )


class LoginPage(Controller):
    """
    This page is used by the authentication to enter a user/pass.
    """

    @cherrypy.expose()
    @cherrypy.tools.auth_mfa(on=False)
    @cherrypy.tools.ratelimit(methods=['POST'])
    def index(self, **kwargs):
        """
        Called by auth_form to generate the /login/ page.
        """
        form = LoginForm()

        # Validate user's credentials
        if form.validate_on_submit():
            try:
                results = [r for r in cherrypy.engine.publish('login', form.login.data, form.password.data) if r]
            except Exception:
                logger.exception('fail to validate user [%s] credentials', form.login.data)
                flash(_("Failed to validate user credentials."), level='error')
            else:
                if len(results) > 0 and results[0]:
                    cherrypy.tools.auth_form.login(username=results[0].username, persistent=form.persistent.data)
                    cherrypy.tools.auth_form.redirect_to_original_url()
                else:
                    flash(_("Invalid username or password."))
        else:
            if not form.login.data:
                # If user got redirected to login page, let use the URL to fill the login name by default.
                redirect_url = cherrypy.tools.auth_form._get_redirect_url()
                parts = redirect_url.strip('/').split('/', 2)
                if len(parts) == 3:
                    form.login.data = parts[1]

        params = {
            'form': form,
        }
        # Add welcome message to params. Try to load translated message.
        welcome_msg = self.app.cfg.welcome_msg
        if welcome_msg:
            default_welcome_msg = welcome_msg.get('')
            lang = get_translation().locale.language
            params["welcome_msg"] = welcome_msg.get(lang, default_welcome_msg)

        return self._compile_template("login.html", **params)
