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
from wtforms.validators import DataRequired, EqualTo, InputRequired, Length, Optional, Regexp, ValidationError

try:
    from wtforms.fields import EmailField  # wtform >=3
except ImportError:
    from wtforms.fields.html5 import EmailField  # wtform <3

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.model import UserObject
from rdiffweb.tools.i18n import gettext_lazy as _


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
        try:
            user.fullname = self.fullname.data
            user.email = self.email.data
            user.commit()
        except Exception as e:
            user.rollback()
            flash(str(e), level='warning')


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

    def validate_new(self, field):
        """
        Make sure new password if not equals to old password.
        """
        if self.new.data and self.new.data == self.current.data:
            raise ValidationError(_('The new password must be different from the current password.'))

    def populate_obj(self, user):
        # Check if current password is "valid" if Not, rate limit the
        # number of attempts and logout user after too many invalid attempts.
        if not user.validate_password(self.current.data):
            self.current.errors = [_("Wrong current password.")]
            return False
        try:
            user.set_password(self.new.data)
            user.commit()
            return True
        except ValueError as e:
            user.rollback()
            self.new.errors = [str(e)]
            return False


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
            if user.refresh_repos(delete=True):
                user.commit()
            flash(_("Repositories successfully updated"), level='success')
        except ValueError as e:
            user.rollback()
            flash(str(e), level='warning')


class PagePrefsGeneral(Controller):
    """
    Plugin to change user profile and password.
    """

    @cherrypy.expose
    @cherrypy.tools.ratelimit(methods=['POST'], logout=True)
    def default(self, **kwargs):
        # Process the parameters.
        profile_form = UserProfileForm(obj=self.app.currentuser)
        password_form = UserPasswordForm()
        refresh_form = RefreshForm()
        if profile_form.is_submitted():
            if profile_form.validate():
                profile_form.populate_obj(self.app.currentuser)
                flash(_("Profile updated successfully."), level='success')
                raise cherrypy.HTTPRedirect("")
            else:
                flash(profile_form.error_message, level='error')
        elif password_form.is_submitted():
            if password_form.validate():
                if password_form.populate_obj(self.app.currentuser):
                    flash(_("Password updated successfully."), level='success')
                    raise cherrypy.HTTPRedirect("")
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
