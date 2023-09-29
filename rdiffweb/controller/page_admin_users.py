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
import humanfriendly
from wtforms import validators, widgets
from wtforms.fields import Field, HiddenField, PasswordField, SelectField, StringField
from wtforms.validators import ValidationError

try:
    from wtforms.fields import EmailField  # wtform >=3
except ImportError:
    from wtforms.fields.html5 import EmailField  # wtform <3

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.model import UserObject
from rdiffweb.core.rdw_templating import url_for
from rdiffweb.tools.i18n import gettext_lazy as _

# Define the logger
logger = logging.getLogger(__name__)

# Max root directory path length
MAX_PATH = 260


class SizeField(Field):
    """
    A text field which stores a file size as GiB or GB format.
    """

    widget = widgets.TextInput()

    def __init__(self, label=None, validators=None, **kwargs):
        super(SizeField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and humanfriendly.format_size(self.data, binary=True) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            value_str = ''.join(valuelist)
            # parse_size doesn't handle locales.this mean we need to
            # replace ',' by '.' to get parse and prefix number with 0
            value_str = value_str.replace(',', '.').strip()
            # a value must start with a number.
            if value_str.startswith('.'):
                value_str = '0' + value_str
            try:
                self.data = humanfriendly.parse_size(value_str)
            except humanfriendly.InvalidSize:
                self.data = None
                raise ValidationError(self.gettext('Not a valid file size value'))


class UserForm(CherryForm):
    userid = HiddenField(_('UserID'))
    username = StringField(
        _('Username'),
        validators=[
            validators.data_required(),
            validators.length(max=256, message=_('Username too long.')),
            validators.length(min=3, message=_('Username too short.')),
            validators.regexp(UserObject.PATTERN_USERNAME, message=_('Must not contain any special characters.')),
        ],
    )
    fullname = StringField(
        _('Fullname'),
        validators=[
            validators.optional(),
            validators.length(max=256, message=_('Fullname too long.')),
            validators.regexp(UserObject.PATTERN_FULLNAME, message=_('Must not contain any special characters.')),
        ],
    )
    email = EmailField(
        _('Email'),
        validators=[
            validators.optional(),
            validators.length(max=256, message=_('Email too long.')),
            validators.regexp(UserObject.PATTERN_EMAIL, message=_('Must be a valid email address.')),
        ],
    )
    password = PasswordField(
        _('Password'),
        validators=[validators.optional()],
    )
    mfa = SelectField(
        _('Two-Factor Authentication (2FA)'),
        coerce=int,
        choices=[
            (UserObject.DISABLED_MFA, _("Disabled")),
            (UserObject.ENABLED_MFA, _("Enabled")),
        ],
        default=UserObject.DISABLED_MFA,
        description=_(
            "When Two-Factor Authentication (2FA) is enabled for a user, a verification code get sent by email when user login from a new location."
        ),
    )
    user_root = StringField(
        _('Root directory'),
        description=_("Absolute path defining the location of the repositories for this user."),
        validators=[
            validators.length(max=MAX_PATH, message=_('Root directory too long.')),
        ],
    )
    role = SelectField(
        _('User Role'),
        coerce=int,
        choices=[
            (UserObject.ADMIN_ROLE, _("Admin")),
            (UserObject.MAINTAINER_ROLE, _("Maintainer")),
            (UserObject.USER_ROLE, _("User")),
        ],
        default=UserObject.USER_ROLE,
        description=_(
            "Admin: may browse and delete everything. Maintainer: may browse and delete their own repo. User: may only browser their own repo."
        ),
    )
    report_time_range = SelectField(
        _('Send Backup report'),
        choices=[
            (0, _('Never')),
            (1, _('Daily')),
            (7, _('Weekly')),
            (30, _('Monthly')),
        ],
        coerce=int,
        default='0',
    )
    disk_quota = SizeField(
        _('Disk space'),
        validators=[validators.optional()],
        description=_("Users disk spaces (in bytes). Set to 0 to remove quota (unlimited)."),
    )
    disk_usage = SizeField(
        _('Quota Used'),
        validators=[validators.optional()],
        description=_("Disk spaces (in bytes) used by this user."),
        widget=widgets.HiddenInput(),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Make quota field readonly if quota is not enabled.
        self.quota_enabled = len(cherrypy.engine.listeners.get('set_disk_quota', [])) > 0
        if not self.quota_enabled:
            self.disk_quota.render_kw = {'readonly': True, 'disabled': True}
            self.disk_usage.render_kw = {'readonly': True, 'disabled': True}
        # Add help text for LDAP user
        cfg = cherrypy.request.app.cfg
        if cfg.ldap_uri:
            self.password.description = _('To create an LDAP user, you must leave the password empty.')

    def validate_role(self, field):
        # Don't allow the user to changes it's "role" state.
        currentuser = cherrypy.request.currentuser
        if self.username.data == currentuser.username and self.role.data != currentuser.role:
            raise ValidationError(_('Cannot edit your own role.'))

    def validate_mfa(self, field):
        # Don't allow the user to changes it's "mfa" state.
        currentuser = cherrypy.request.currentuser
        if self.username.data == currentuser.username and self.mfa.data != currentuser.mfa:
            raise ValidationError(_('Cannot change your own two-factor authentication settings.'))
        if not self.email.data and self.mfa.data:
            raise ValidationError(_('User email is required to enabled Two-Factor Authentication.'))

    def populate_obj(self, userobj):
        try:
            # Save password if defined
            if self.password.data:
                userobj.set_password(self.password.data)
            userobj.role = self.role.data
            userobj.fullname = self.fullname.data or ''
            userobj.email = self.email.data or ''
            userobj.user_root = self.user_root.data
            userobj.mfa = self.mfa.data
            userobj.report_time_range = self.report_time_range.data
            if userobj.user_root:
                if not userobj.valid_user_root():
                    flash(_("User's root directory %s is not accessible!") % userobj.user_root, level='error')
                    logger.warning("user's root directory %s is not accessible" % userobj.user_root)
                else:
                    userobj.refresh_repos(delete=True)
            userobj.commit()

        except Exception as e:
            userobj.rollback()
            flash(str(e), level='warning')
            return False

        # Try to update disk quota if the human readable value changed.
        # Report error using flash.
        if self.quota_enabled:
            new_quota = self.disk_quota.data or 0
            old_quota = humanfriendly.parse_size(
                humanfriendly.format_size(self.disk_quota.object_data or 0, binary=True)
            )
            if old_quota != new_quota:
                userobj.disk_quota = new_quota
                # Setting quota will silently fail. Check if quota was updated.
                if userobj.disk_quota != new_quota:
                    flash(_("Setting user's quota is not supported"), level='warning')
        return True


class EditUserForm(UserForm):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Make username field read-only
        self.username.render_kw = {'readonly': True, 'disabled': True}

        # When editing ourself.
        currentuser = cherrypy.request.currentuser
        if self.username.object_data == currentuser.username:
            # Disable MFA
            self.mfa.render_kw = {'readonly': True, 'disabled': True}
            # Disable Role
            self.role.render_kw = {'readonly': True, 'disabled': True}

    def validate_username(self, field):
        # Raise an error if username doesn't matches our user object
        if field.data != field.object_data:
            raise ValidationError(_('Cannot change username of and existing user.'))


class DeleteUserForm(CherryForm):
    username = StringField(_('Username'), validators=[validators.data_required()])


@cherrypy.tools.is_admin()
class AdminUsersPage(Controller):
    """
    Administration pages. Allow to manage users database.
    """

    @cherrypy.expose
    def index(self):
        # Build users page
        form = UserForm()
        return self._compile_template(
            "admin_users.html",
            form=form,
            users=UserObject.query.all(),
            ldap_enabled=self.app.cfg.ldap_uri,
        )

    @cherrypy.expose
    @cherrypy.tools.ratelimit(methods=['POST'])
    def new(self, **kwargs):
        form = UserForm()
        if form.is_submitted():
            if form.validate():
                try:
                    user = UserObject.add_user(form.username.data)
                except Exception as e:
                    flash(str(e), level='error')
                else:
                    if form.populate_obj(user):
                        flash(_("User added successfully."))
                        raise cherrypy.HTTPRedirect(url_for('admin', 'users'))
            else:
                flash(form.error_message, level='error')
        return self._compile_template("admin_user_new.html", form=form)

    @cherrypy.expose
    def edit(self, username_vpath, **kwargs):
        user = UserObject.get_user(username_vpath)
        if not user:
            raise cherrypy.HTTPError(400, _("User %s doesn't exists") % username_vpath)
        form = EditUserForm(obj=user)
        if form.is_submitted():
            if form.validate():
                if form.populate_obj(user):
                    flash(_("User information modified successfully."))
                    raise cherrypy.HTTPRedirect(url_for('admin', 'users'))
            else:
                flash(form.error_message, level='error')
        return self._compile_template("admin_user_edit.html", form=form)

    @cherrypy.expose
    def delete(self, username=None, **kwargs):
        # Validate form method.
        form = DeleteUserForm()
        if not form.is_submitted():
            raise cherrypy.HTTPError(405)
        # Get user
        user = UserObject.get_user(username)
        if not user:
            raise cherrypy.HTTPError(400, _("User %s doesn't exists") % username)
        if form.validate():
            if form.username.data == self.app.currentuser.username:
                raise cherrypy.HTTPError(400, _("You cannot remove your own account!"))
            try:
                user.delete()
                user.commit()
                flash(_("User account removed."))
            except Exception as e:
                user.rollback()
                flash(str(e), level='error')
        else:
            flash(form.error_message, level='error')
        raise cherrypy.HTTPRedirect(url_for('admin', 'users'))
