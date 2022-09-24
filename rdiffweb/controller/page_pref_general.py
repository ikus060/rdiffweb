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
from wtforms.fields import HiddenField, PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Length, Regexp

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.tools.i18n import gettext_lazy as _

# Define the logger
_logger = logging.getLogger(__name__)

PATTERN_EMAIL = re.compile(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$')


class UserProfileForm(CherryForm):
    action = HiddenField(default='set_profile_info')
    username = StringField(_('Username'), render_kw={'readonly': True})
    fullname = StringField(_('Fullname'))
    email = EmailField(
        _('Email'),
        validators=[
            DataRequired(),
            Length(max=256, message=_("Invalid email.")),
            Regexp(PATTERN_EMAIL, message=_("Invalid email.")),
        ],
    )
    set_profile_info = SubmitField(_('Save changes'))

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.action.data == 'set_profile_info'

    def populate_obj(self, user):
        user.fullname = self.fullname.data
        user.email = self.email.data
        user.add()


class UserPasswordForm(CherryForm):
    action = HiddenField(default='set_password')
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
    set_password = SubmitField(_('Update password'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new.validators += [
            Length(
                min=self.app.cfg.password_min_length,
                max=self.app.cfg.password_max_length,
                message=_('Password must have between %(min)d and %(max)d characters.'),
            )
        ]

    @property
    def app(self):
        return cherrypy.request.app

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.action.data == 'set_password'

    def populate_obj(self, user):
        try:
            user.set_password(self.new.data, old_password=self.current.data)
            flash(_("Password updated successfully."), level='success')
        except ValueError as e:
            flash(str(e), level='warning')


class RefreshForm(CherryForm):
    action = HiddenField(default='update_repos')
    update_repos = SubmitField(
        _('Refresh repositories'),
        description=_(
            "Refresh the list of repositories associated to your account. If you recently add a new repository and it doesn't show, you may try to refresh the list."
        ),
    )

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.action.data == 'update_repos'

    def populate_obj(self, user):
        try:
            user.refresh_repos(delete=True)
            flash(_("Repositories successfully updated"), level='success')
        except ValueError as e:
            flash(str(e), level='warning')


class PagePrefsGeneral(Controller):
    """
    Plugin to change user profile and password.
    """

    @cherrypy.expose
    def default(self, **kwargs):
        # Process the parameters.
        profile_form = UserProfileForm(obj=self.app.currentuser)
        password_form = UserPasswordForm()
        refresh_form = RefreshForm()
        if profile_form.is_submitted():
            if profile_form.validate():
                profile_form.populate_obj(self.app.currentuser)
                flash(_("Profile updated successfully."), level='success')
            else:
                flash(profile_form.error_message, level='error')
        elif password_form.is_submitted():
            if password_form.validate():
                password_form.populate_obj(self.app.currentuser)
            else:
                flash(password_form.error_message, level='error')
        elif refresh_form.is_submitted():
            if refresh_form.validate():
                refresh_form.populate_obj(self.app.currentuser)
            else:
                flash(refresh_form.error_message, level='error')
        params = {
            'profile_form': profile_form,
            'password_form': password_form,
            'refresh_form': refresh_form,
        }
        return self._compile_template("prefs_general.html", **params)
