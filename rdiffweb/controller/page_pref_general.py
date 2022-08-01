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
from wtforms.fields import PasswordField, StringField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Regexp

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.tools.i18n import gettext_lazy as _

# Define the logger
_logger = logging.getLogger(__name__)

PATTERN_EMAIL = re.compile(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$')


class UserProfileForm(CherryForm):
    username = StringField(_('Username'), render_kw={'readonly': True})
    fullname = StringField(_('Fullname'))
    email = EmailField(_('Email'), validators=[DataRequired(), Regexp(PATTERN_EMAIL, message=_("Invalid email."))])

    def populate_obj(self, user):
        user.fullname = self.fullname.data
        user.email = self.email.data
        user.add()


class UserPasswordForm(CherryForm):
    current = PasswordField(
        _('Current password'),
        validators=[InputRequired(_("Current password is missing."))],
        description=_("You must provide your current password in order to change it."),
    )
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


class PagePrefsGeneral(Controller):
    """
    Plugin to change user profile and password.
    """

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

    @cherrypy.expose
    def default(self, action=None, **kwargs):
        # Process the parameters.
        profile_form = UserProfileForm(obj=self.app.currentuser)
        password_form = UserPasswordForm()
        if action == "set_profile_info":
            if profile_form.validate_on_submit():
                profile_form.populate_obj(self.app.currentuser)
                flash(_("Profile updated successfully."), level='success')
        elif action == "set_password":
            self._handle_set_password(action, password_form)
        elif action == "update_repos":
            self.app.currentuser.refresh_repos(delete=True)
            flash(_("Repositories successfully updated"), level='success')
        elif action is not None:
            _logger.warning("unknown action: %s", action)
            raise cherrypy.NotFound("Unknown action")
        params = {
            'profile_form': profile_form,
            'password_form': password_form,
        }
        return self._compile_template("prefs_general.html", **params)
