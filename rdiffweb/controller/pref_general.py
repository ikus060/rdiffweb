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
Default preference page to show general user information. It allows user
to change password ans refresh it's repository view.
"""

import logging
import re

import cherrypy
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Length, Regexp

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.cherrypy_wtf import CherryForm
from rdiffweb.tools.i18n import ugettext as _

# Define the logger
_logger = logging.getLogger(__name__)

PATTERN_EMAIL = re.compile(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$')


class UserProfileForm(CherryForm):
    email = EmailField(
        _('Email'),
        validators=[
            DataRequired(),
            Length(max=256, message=_("Invalid email.")),
            Regexp(PATTERN_EMAIL, message=_("Invalid email.")),
        ],
    )


class UserPasswordForm(CherryForm):
    current = PasswordField(_('Current password'), validators=[InputRequired(_("Current password is missing."))])
    new = PasswordField(
        _('New password'),
        validators=[
            InputRequired(_("New password is missing.")),
            EqualTo('confirm', message=_("The new password and its confirmation do not match.")),
        ],
    )
    confirm = PasswordField(
        _('Confirm new password'), validators=[InputRequired(_("Confirmation password is missing."))]
    )

    def validate_new(self, field):
        validator = Length(
            min=self.app.cfg.password_min_length,
            max=self.app.cfg.password_max_length,
            message=_('Password must have between %(min)d and %(max)d characters.'),
        )
        validator(self, field)

    @property
    def app(self):
        return cherrypy.request.app


class PrefsGeneralPanelProvider(Controller):
    """
    Plugin to change user profile and password.
    """

    panel_id = 'general'

    panel_name = _('Profile')

    def _handle_set_password(self, action, form):
        """
        Called when changing user password.
        """
        assert self.app.currentuser
        assert action == 'set_password'
        assert form
        # Validate form
        if not form.validate():
            flash(form.error_message, level='error')
            return
        # Update user password
        try:
            self.app.currentuser.set_password(form.new.data, old_password=form.current.data)
            flash(_("Password updated successfully."), level='success')
        except ValueError as e:
            flash(str(e), level='warning')

    def _handle_set_profile_info(self, action, form):
        """
        Called when changing user profile.
        """
        assert self.app.currentuser
        assert action == 'set_profile_info'
        assert form
        # Validate form
        if not form.validate():
            flash(form.error_message, level='error')
            return
        # Update the user's email
        username = self.app.currentuser.username
        _logger.info("updating user [%s] email [%s]", username, form.email.data)
        self.app.currentuser.email = form.email.data
        # Report success
        flash(_("Profile updated successfully."), level='success')

    def render_prefs_panel(self, panelid, action=None, **kwargs):  # @UnusedVariable
        # Process the parameters.
        profile_form = UserProfileForm(email=self.app.currentuser.email)
        password_form = UserPasswordForm()
        if cherrypy.request.method == 'POST':
            if action == "set_profile_info":
                self._handle_set_profile_info(action, profile_form)
            elif action == "set_password":
                self._handle_set_password(action, password_form)
            elif action == "update_repos":
                self.app.currentuser.refresh_repos(delete=True)
                flash(_("Repositories successfully updated"), level='success')
            elif action is None:
                pass
            else:
                _logger.warning("unknown action: %s", action)
                raise cherrypy.NotFound("Unknown action")
        params = {
            'profile_form': profile_form,
            'password_form': password_form,
        }
        return "prefs_general.html", params
