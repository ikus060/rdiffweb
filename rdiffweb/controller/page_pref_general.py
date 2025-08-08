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
"""
Default preference page to show general user information. It allows user
to change password ans refresh it's repository view.
"""

import cherrypy
from wtforms.fields import HiddenField, PasswordField, SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, EqualTo, InputRequired, Length, Optional, Regexp, ValidationError

try:
    from wtforms.fields import EmailField  # wtform >=3
except ImportError:
    from wtforms.fields.html5 import EmailField  # wtform <3

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.formdb import DbForm
from rdiffweb.core.model import UserObject
from rdiffweb.tools.i18n import gettext_lazy as _
from rdiffweb.tools.i18n import list_available_locales


class UserProfileForm(DbForm):
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
    lang = SelectField(_('Preferred Language'))
    set_profile_info = SubmitField(_('Save changes'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        languages = [(locale.language, locale.display_name.capitalize()) for locale in list_available_locales()]
        languages = sorted(languages, key=lambda x: x[1])
        languages.insert(0, ('', _('(default)')))
        self.lang.choices = languages

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.action.default in self.action.raw_data

    def populate_obj(self, user):
        user.fullname = self.fullname.data
        user.email = self.email.data
        user.lang = self.lang.data


class UserPasswordForm(DbForm):
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
        return super().is_submitted() and self.action.default in self.action.raw_data

    def validate_new(self, field):
        """
        Make sure new password if not equals to old password.
        """
        if self.new.data and self.new.data == self.current.data:
            raise ValidationError(_('The new password must be different from the current password.'))

    def populate_obj(self, user):
        if not user.validate_password(self.current.data):
            raise ValueError(_("Wrong current password."))
        try:
            user.set_password(self.new.data)
        except ValueError as e:
            raise ValidationError(e)


class RefreshForm(DbForm):
    action = HiddenField(default='update_repos')
    update_repos = SubmitField(
        _('Refresh repositories'),
        description=_(
            "Refresh the list of repositories associated to your account. If you recently add a new repository and it doesn't show, you may try to refresh the list."
        ),
    )

    def is_submitted(self):
        # Validate only if action is set_profile_info
        return super().is_submitted() and self.action.default in self.action.raw_data

    def populate_obj(self, user):
        user.refresh_repos(delete=True)


class PagePrefsGeneral(Controller):
    """
    Plugin to change user profile and password.
    """

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'], logout=True)
    def default(self, **kwargs):
        """
        Show user settings
        """
        currentuser = cherrypy.serving.request.currentuser
        # Process the parameters.
        profile_form = UserProfileForm(obj=currentuser)
        password_form = UserPasswordForm()
        refresh_form = RefreshForm()
        if profile_form.validate_on_submit():
            if profile_form.save_to_db(currentuser):
                flash(_("Profile updated successfully."), level='success')
                raise cherrypy.HTTPRedirect("")
        elif password_form.validate_on_submit():
            if password_form.save_to_db(currentuser):
                flash(_("Password updated successfully."), level='success')
                raise cherrypy.HTTPRedirect("")
        elif refresh_form.validate_on_submit():
            if refresh_form.save_to_db(currentuser):
                flash(_("Repositories successfully updated"), level='success')
                raise cherrypy.HTTPRedirect("")
        if profile_form.error_message:
            flash(profile_form.error_message, level='error')
        if password_form.error_message:
            flash(password_form.error_message, level='error')
        if refresh_form.error_message:
            flash(refresh_form.error_message, level='error')
        params = {
            'profile_form': profile_form,
            'password_form': password_form,
            'refresh_form': refresh_form,
        }
        return self._compile_template("prefs_general.html", **params)
