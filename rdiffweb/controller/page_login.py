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
from wtforms.fields import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.tools.i18n import get_translation
from rdiffweb.tools.i18n import gettext_lazy as _

# Define the logger
logger = logging.getLogger(__name__)


class LoginForm(CherryForm):
    # Sanitize the redirect URL to avoid Open Redirect
    # redirect = HiddenField(default='/', filters=[lambda v: v if v.startswith('/') else '/'])
    login = StringField(
        _('Username'),
        # Default to last MFA username (if any).
        default=lambda: cherrypy.tools.auth.get_user_key() or "",
        validators=[DataRequired(), Length(max=256, message=_('Username too long.'))],
        render_kw={
            "autocorrect": "off",
            "autocapitalize": "none",
            "autocomplete": "off",
            "autofocus": "autofocus",
        },
    )
    password = PasswordField(_('Password'), validators=[DataRequired()], render_kw={"placeholder": _('Password')})
    persistent = BooleanField(
        _('Remember me'),
        default=lambda: cherrypy.tools.sessions_timeout.is_persistent(),
        render_kw={},
    )
    submit = SubmitField(
        _('Sign in'),
        render_kw={"class": "btn-primary btn-lg btn-block"},
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # If user got redirected to login page, let use the URL to fill the login name by default.
        # e.g.: /browse/<username>/reponame
        original_url = cherrypy.tools.auth.get_original_url()
        if (
            original_url
            and original_url.startswith('/browse/')
            and original_url.count('/') >= 3
            and not self.login.data
        ):
            self.login.data = original_url.strip('/').split('/', 2)[1]
        # Update place holder based on application config
        cfg = cherrypy.tree.apps[''].cfg
        self.login.render_kw['placeholder'] = _('Username or Email') if cfg.login_with_email else _('Username')
        # Add a tooltip on remember me to include session timeout.
        persistent_timeout = cherrypy.config.get('tools.sessions_timeout.persistent_timeout')
        idle_timeout = cherrypy.config.get('tools.sessions.timeout')
        title = _(
            "Check this to stay signed in for %d day(s). If you leave it unchecked, your session will last for %d hour(s)."
        ) % (persistent_timeout // 1440, idle_timeout // 60)
        self.persistent.render_kw['title'] = title
        self.persistent.render_kw['label-title'] = title


class LoginPage(Controller):
    """
    This page is used by the authentication to enter a user/pass.
    """

    @cherrypy.expose()
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.auth_mfa(on=False)
    @cherrypy.tools.ratelimit(methods=['POST'])
    def index(self, **kwargs):
        """
        Display form to authenticate user.
        """

        # Redirect user to location page if already login
        if getattr(cherrypy.request, 'login', False):
            raise cherrypy.HTTPRedirect('/')

        # Validate user's credentials
        form = LoginForm()
        if form.validate_on_submit():
            userobj = cherrypy.tools.auth.login_with_credentials(form.login.data, form.password.data)
            if userobj:
                cherrypy.tools.sessions_timeout.set_persistent(form.persistent.data)
                raise cherrypy.tools.auth.redirect_to_original_url()
            else:
                flash(_("Invalid username or password."))
        elif form.error_message:
            flash(form.error_message)
        cfg = self.app.cfg
        params = {
            'form': form,
            'oauth_enabled': cfg.oauth_client_id and cfg.oauth_client_secret,
            'oauth_provider_name': cfg.oauth_provider_name,
        }
        # Add welcome message to params. Try to load translated message.
        welcome_msg = self.app.cfg.welcome_msg
        if welcome_msg:
            default_welcome_msg = welcome_msg.get('')
            lang = get_translation().locale.language
            params["welcome_msg"] = welcome_msg.get(lang, default_welcome_msg)

        return self._compile_template("login.html", **params)


class LogoutPage(Controller):
    @cherrypy.expose()
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.auth(on=False)
    @cherrypy.tools.auth_mfa(on=False)
    @cherrypy.tools.ratelimit(methods=['POST'])
    def default(self, **kwargs):
        """
        Logout user
        """
        cherrypy.tools.auth.clear_session()
        raise cherrypy.HTTPRedirect('/')
