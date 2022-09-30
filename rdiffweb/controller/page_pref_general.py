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

import cherrypy
from wtforms.fields import HiddenField, PasswordField, StringField, SubmitField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Length, Optional, Regexp

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.model import UserObject
from rdiffweb.tools.i18n import gettext_lazy as _

# Maximum number of password change attempt before logout
CHANGE_PASSWORD_MAX_ATTEMPT = 5
CHANGE_PASSWORD_ATTEMPTS = 'change_password_attempts'


class UserProfileForm(CherryForm):
    action = HiddenField(default='set_profile_info')
    username = StringField(_('Username'), render_kw={'readonly': True})
    fullname = StringField(
        _('Fullname'),
        validators=[
            Optional(),
            Length(max=256, message=_('Fullname too long.')),
            Regexp(UserObject.PATTERN_FULLNAME, message=_('Must not contain any special characters.')),
        ],
    )
    email = EmailField(
        _('Email'),
        validators=[
            DataRequired(),
            Length(max=256, message=_("Email too long.")),
            Regexp(UserObject.PATTERN_EMAIL, message=_("Must be a valid email address.")),
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

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.action.data == 'set_password'

    def populate_obj(self, user):
        # Check if current password is "valid" if Not, rate limit the
        # number of attempts and logout user after too many invalid attempts.
        if not user.validate_password(self.current.data):
            cherrypy.session[CHANGE_PASSWORD_ATTEMPTS] = cherrypy.session.get(CHANGE_PASSWORD_ATTEMPTS, 0) + 1
            attempts = cherrypy.session[CHANGE_PASSWORD_ATTEMPTS]
            if attempts >= CHANGE_PASSWORD_MAX_ATTEMPT:
                cherrypy.session.clear()
                cherrypy.session.regenerate()
                flash(
                    _("You were logged out because you entered the wrong password too many times."),
                    level='warning',
                )
                raise cherrypy.HTTPRedirect('/login/')
            flash(_("Wrong current password."), level='warning')
        else:
            # Clear number of attempts
            if CHANGE_PASSWORD_ATTEMPTS in cherrypy.session:
                del cherrypy.session[CHANGE_PASSWORD_ATTEMPTS]
            # If Valid, update password
            try:
                user.set_password(self.new.data)
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
