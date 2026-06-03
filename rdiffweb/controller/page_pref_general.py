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
from cherrypy_foundation.tools.i18n import get_timezone_name, list_available_timezones
from wtforms.fields import HiddenField, PasswordField, SelectField, StringField
from wtforms.validators import EqualTo, InputRequired, Length, Optional, Regexp, ValidationError

try:
    from wtforms.fields import EmailField  # wtform >=3
except ImportError:
    from wtforms.fields.html5 import EmailField  # wtform <3

import logging

from cherrypy_foundation.flash import flash
from cherrypy_foundation.tools.i18n import gettext_lazy as _
from cherrypy_foundation.tools.i18n import list_available_locales

from rdiffweb.controller.formdb import DbForm
from rdiffweb.core.model import UserObject

logger = logging.getLogger(__name__)


class UserProfileForm(DbForm):
    username = StringField(
        _('Username'), description=_('Your username cannot be changed.'), render_kw={'readonly': True}
    )
    fullname = StringField(
        _('Fullname'),
        validators=[
            Optional(),
            Length(max=256, message=_('Fullname too long.')),
            Regexp(UserObject.PATTERN_FULLNAME, message=_('Must not contain any special characters.')),
        ],
    )
    email = EmailField(
        _('Email address'),
        description=_('Used for backup reports and notifications.'),
        validators=[
            Optional(),
            Length(max=256, message=_("Email too long.")),
            Regexp(UserObject.PATTERN_EMAIL, message=_("Must be a valid email address.")),
        ],
    )
    lang = SelectField(_('Preferred Language'))
    timezone = SelectField(
        _('Preferred timezone'),
        description=_('Used to display backup times in your local time.'),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Load available languages
        languages = [(locale.language, locale.display_name.capitalize()) for locale in list_available_locales()]
        languages = sorted(languages, key=lambda x: x[1])
        languages.insert(0, ('', _('(default)')))
        self.lang.choices = languages
        # Load available timezone
        timezones = [
            (timezone, '%s (%s)' % (timezone, get_timezone_name(timezone))) for timezone in list_available_timezones()
        ]
        timezones.insert(0, ('', _('(default)')))
        self.timezone.choices = timezones

    def populate_obj(self, user):
        user.fullname = self.fullname.data
        user.email = self.email.data
        user.lang = self.lang.data
        user.timezone = self.timezone.data


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


class PagePrefsGeneral:
    """
    Plugin to change user profile and password.
    """

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'], logout=True)
    @cherrypy.tools.jinja2(template="prefs_general.html")
    def default(self, **kwargs):
        """
        Show user settings
        """
        currentuser = cherrypy.serving.request.currentuser
        # Process the parameters.
        form = UserProfileForm(obj=currentuser)
        password_form = UserPasswordForm()
        if password_form.is_submitted():
            # Check password first.
            if password_form.validate():
                if password_form.save_to_db(currentuser):
                    flash(_("Password updated successfully."), level='success')
                    raise cherrypy.HTTPRedirect("")
            if password_form.error_message:
                flash(password_form.error_message, level='error')
        elif form.is_submitted():
            if form.validate():
                # Fallback to profile form.
                if form.save_to_db(currentuser):
                    flash(_("Profile updated successfully."), level='success')
                    raise cherrypy.HTTPRedirect("")
            if form.error_message:
                flash(form.error_message, level='error')
        return {
            'form': form,
            'password_form': password_form,
        }
