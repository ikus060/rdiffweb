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
from collections import namedtuple

import cherrypy
import humanfriendly
from cherrypy_foundation.flash import flash
from cherrypy_foundation.tools.i18n import get_timezone_name
from cherrypy_foundation.tools.i18n import gettext_lazy as _
from cherrypy_foundation.tools.i18n import list_available_locales, list_available_timezones
from cherrypy_foundation.url import url_for
from markupsafe import Markup
from sqlalchemy.orm import joinedload
from wtforms import validators, widgets
from wtforms.fields import BooleanField, Field, HiddenField, PasswordField, SelectField, StringField, TextAreaField
from wtforms.validators import ValidationError

from rdiffweb.controller.formdb import DbForm
from rdiffweb.controller.page_pref_sshkeys import DeleteSshForm, SshForm
from rdiffweb.controller.page_pref_tokens import DeleteTokenForm, TokenForm
from rdiffweb.core.model import Message, UserObject

try:
    from wtforms.fields import EmailField  # wtform >=3
except ImportError:
    from wtforms.fields.html5 import EmailField  # wtform <3


# Define the logger
logger = logging.getLogger(__name__)

# Max root directory path length
MAX_PATH = 260

UserActivityRow = namedtuple('UserActivityRow', ['id', 'author', 'date', 'type', 'body', 'changes'])


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


class NewUserForm(DbForm):
    fullname = StringField(
        _('Fullname'),
        validators=[
            validators.optional(),
            validators.length(max=256, message=_('Fullname too long.')),
            validators.regexp(UserObject.PATTERN_FULLNAME, message=_('Must not contain any special characters.')),
        ],
    )
    username = StringField(
        _('Username'),
        description=_('Username cannot be changed after creation.'),
        validators=[
            validators.data_required(),
            validators.length(max=256, message=_('Username too long.')),
            validators.length(min=3, message=_('Username too short.')),
            validators.regexp(
                UserObject.PATTERN_USERNAME,
                message=_(
                    'Must start with a letter and contain only letters, numbers, underscores (_), hyphens (-), or periods (.).'
                ),
            ),
        ],
    )
    password = PasswordField(_('Password'), validators=[validators.data_required(), validators.optional()])

    def populate_obj(self, userobj):
        # Update fullname
        userobj.fullname = self.fullname.data or ''


class EditUserForm(DbForm):
    id = HiddenField()
    username = StringField(
        _('Username'),
        description=_('Username cannot be changed.'),
        validators=[
            validators.data_required(),
            validators.length(max=256, message=_('Username too long.')),
            validators.length(min=3, message=_('Username too short.')),
            validators.regexp(
                UserObject.PATTERN_USERNAME,
                message=_(
                    'Must start with a letter and contain only letters, numbers, underscores (_), hyphens (-), or periods (.).'
                ),
            ),
        ],
        render_kw={'readonly': True, 'disabled': True},
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
        _('Password'), validators=[validators.optional()], render_kw={'placeholder': _('Leave blank to keep current')}
    )

    user_root = StringField(
        _('Root directory'),
        description=_("Absolute path defining the location of the repositories for this user."),
        validators=[
            validators.length(max=MAX_PATH, message=_('Root directory too long.')),
        ],
    )
    role = SelectField(
        _('Role'),
        # Support string and integer value.
        coerce=lambda v: UserObject.ROLES[v] if v in UserObject.ROLES else int(v),
        choices=[
            (UserObject.ADMIN_ROLE, _("Admin")),
            (UserObject.MAINTAINER_ROLE, _("Maintainer")),
            (UserObject.USER_ROLE, _("User")),
        ],
        default=UserObject.USER_ROLE,
        description=_(
            Markup(_("<b>Admin:</b> full access. <b>Maintainer:</b> own repos only. <b>User:</b> browse own repos."))
        ),
    )
    mfa = SelectField(
        _('Two-Factor Authentication (2FA)'),
        coerce=int,
        choices=[
            (UserObject.DISABLED_MFA, _("Disabled")),
            (UserObject.ENABLED_MFA, _("Enabled")),
        ],
        default=UserObject.DISABLED_MFA,
        description=_("When enabled, a verification code is sent by email on login from a new location."),
    )
    lang = SelectField(_('Preferred Language'), default='')
    timezone = SelectField(_('Preferred timezone'), default='')
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
        description=Markup(_("Disk space limit in bytes. Set to <code>0</code> for unlimited.")),
    )
    disk_usage = SizeField(
        _('Quota Used'),
        validators=[validators.optional()],
        description=_("Disk spaces (in bytes) used by this user."),
        widget=widgets.HiddenInput(),
    )
    disk_usage_threshold = SelectField(
        _('Disk Usage Threshold'),
        choices=[
            (0, _('Never - No storage alerts will be sent.')),
            (50, _('50% - Notify when storage is half full.')),
            (75, _('75% - Notify when storage is three-quarters full.')),
            (90, _('90% - Notify when storage is almost full.')),
            (95, _('95% - Notify when storage is critically full.')),
            (99, _('99% - Notify when storage is nearly exhausted.')),
        ],
        coerce=int,
        default='0',
    )
    notes = TextAreaField(
        _('Notes'),
        description=_('Internal notes visible to administrators only.'),
        default='',
        validators=[validators.length(max=256, message=_('Notes too long.'))],
        render_kw={"placeholder": _("Enter notes about this user.")},
    )
    disabled = BooleanField(
        _('Disabled'),
        description=_("Blocks the user from logging in without deleting their data."),
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # When editing ourself.
        currentuser = cherrypy.request.currentuser
        if self.username.object_data == currentuser.username:
            # Disable MFA
            self.mfa.render_kw = {'readonly': True, 'disabled': True}
            # Disable Role
            self.role.render_kw = {'readonly': True, 'disabled': True}
        # Make quota field readonly if quota is not enabled.
        self.quota_enabled = len(cherrypy.engine.listeners.get('set_disk_quota', [])) > 0
        if not self.quota_enabled:
            self.disk_quota.render_kw = {'readonly': True, 'disabled': True}
            self.disk_usage.render_kw = {'readonly': True, 'disabled': True}
        # Define selectable language
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
        # Add help text for LDAP user
        cfg = cherrypy.request.app.cfg
        if cfg.ldap_uri:
            self.password.description = _('To create an LDAP user, you must leave the password empty.')

    def validate_username(self, field):
        # Raise an error if username doesn't matches our user object
        if field.object_data is not None and field.data != field.object_data:
            raise ValidationError(_('Cannot change username of and existing user.'))

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
        # Save password if defined
        if self.password.data:
            userobj.set_password(self.password.data)
        userobj.role = self.role.data
        userobj.fullname = self.fullname.data or ''
        userobj.email = self.email.data or ''
        userobj.mfa = self.mfa.data
        userobj.lang = self.lang.data or ''
        userobj.report_time_range = self.report_time_range.data
        userobj.notes = self.notes.data
        userobj.disk_usage_threshold = self.disk_usage_threshold.data
        # Update user's status
        if self.disabled.data is True:
            userobj.status = UserObject.STATUS_DISABLED
        elif userobj.status == UserObject.STATUS_DISABLED:
            userobj.status = ""
        # Verify user's root directory and update repos.
        if self.user_root.data != userobj.user_root:
            userobj.user_root = self.user_root.data
            if not userobj.valid_user_root():
                if hasattr(cherrypy.serving, 'session'):
                    flash(_("User's root directory %s is not accessible!") % userobj.user_root, level='error')
            else:
                userobj.refresh_repos(delete=True)

    def save_to_db(self, obj, message_body=None):
        # Add Message to explain changes.
        if message_body:
            currentuser = cherrypy.request.currentuser
            message_obj = Message(body=message_body, author=currentuser)
            obj.add_message(message_obj)

        return_value = super().save_to_db(obj)

        # Try to update disk quota if the human readable value changed.
        # Report error using flash.
        if return_value and self.quota_enabled:
            new_quota = self.disk_quota.data or 0
            old_quota = humanfriendly.parse_size(
                humanfriendly.format_size(self.disk_quota.object_data or 0, binary=True)
            )
            if old_quota != new_quota:
                obj.disk_quota = new_quota
                # Setting quota may silently fail.
                # Align with the nearest block size.
                if abs(obj.disk_quota - new_quota) > 4096:
                    if hasattr(cherrypy.serving, 'session'):
                        flash(_("Setting user's quota is not supported"), level='warning')

        return return_value


class DeleteUserForm(DbForm):
    confirm = StringField(_('Confirmation'), validators=[validators.data_required()])
    username = HiddenField(_('Username'), validators=[validators.data_required()])
    delete_data = BooleanField(
        _("Delete user's data"),
        default=False,
        description=_("Also delete this user's backup data (all associated backups will be permanently removed)"),
    )

    def validate_confirm(self, field):
        if self.confirm.data != self.username.data:
            raise ValidationError(_('Invalid confirmation'))

    def validate_username(self, field):
        currentuser = cherrypy.request.currentuser
        if field.data == currentuser.username:
            raise ValidationError(_("You cannot remove your own account!"))

    def populate_obj(self, userobj):
        """
        Run the deletion process.
        """
        userobj.schedule_delete(delete_data=self.delete_data.data)


@cherrypy.tools.is_admin()
class AdminUsersPage:

    def _get_user(self, username_or_id):
        user = UserObject.get_user(username_or_id)
        if user is None:
            raise cherrypy.HTTPError(400, _("User %s doesn't exists") % username_or_id)
        return user

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    @cherrypy.tools.jinja2(template="admin_users.html")
    def index(self, **kwargs):
        """
        Show user list
        """
        # Build users page
        form = NewUserForm()
        if form.is_submitted():
            if form.validate():
                user = UserObject.add_user(form.username.data, password=form.password.data)
                if form.save_to_db(user):
                    flash(_("User added successfully."))
                    raise cherrypy.HTTPRedirect(url_for('admin', 'users', 'edit', user.id))
        # Form is invalid -> redirect to the form
        if form.error_message:
            flash(form.error_message, level='error')
        return {
            'form': form,
            'edit_form': EditUserForm(),
            'users': UserObject.query.options(
                joinedload(UserObject.repo_objs), joinedload(UserObject.authorizedkeys), joinedload(UserObject.tokens)
            ).all(),
        }

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    @cherrypy.tools.jinja2(template="admin_user_edit.html")
    def edit(self, username_or_id, **kwargs):
        """
        Show form to edit user
        """
        user = self._get_user(username_or_id)
        form = EditUserForm(obj=user)
        message_body = kwargs.get('body', False)
        if form.validate_on_submit() and form.save_to_db(user, message_body=message_body):
            flash(_("User information modified successfully."))
            raise cherrypy.HTTPRedirect(url_for('admin', 'users'))
        if form.error_message:
            flash(form.error_message, level='error')
        return {
            'form': form,
            'delete_form': DeleteUserForm(),
            'ssh_form': SshForm(),
            'token_form': TokenForm(),
            'user': user,
        }

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    def add_sshkey(self, username=None, **kwargs):
        """
        Add user ssh key.
        """
        cfg = cherrypy.tree.apps[''].cfg
        if cfg.disable_ssh_keys:
            raise cherrypy.HTTPError(400)
        userobj = self._get_user(username)
        # Validate form method.
        form = SshForm()
        if form.validate():
            if form.save_to_db(userobj):
                flash(_('SSH Key added.'))
        if form.error_message:
            flash(form.error_message, level='error')
        raise cherrypy.HTTPRedirect(url_for('admin', 'users', 'edit', username))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    def delete_sshkey(self, username=None, **kwargs):
        """
        Delete user ssh key.
        """
        cfg = cherrypy.tree.apps[''].cfg
        if cfg.disable_ssh_keys:
            raise cherrypy.HTTPError(400)
        userobj = self._get_user(username)
        # Validate form method.
        form = DeleteSshForm()
        if form.validate():
            # Get user
            if form.save_to_db(userobj):
                flash(_('SSH Key removed.'))
        if form.error_message:
            flash(form.error_message, level='error')
        raise cherrypy.HTTPRedirect(url_for('admin', 'users', 'edit', username))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    def add_token(self, username=None, **kwargs):
        """
        Add user token.
        """
        cfg = cherrypy.tree.apps[''].cfg
        if cfg.disable_ssh_keys:
            raise cherrypy.HTTPError(400)
        userobj = self._get_user(username)
        # Validate form method.
        form = TokenForm()
        if form.validate():
            if form.save_to_db(userobj):
                flash(_('Access token added.'))
        if form.error_message:
            flash(form.error_message, level='error')
        raise cherrypy.HTTPRedirect(url_for('admin', 'users', 'edit', username))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    def delete_token(self, username=None, **kwargs):
        """
        Delete user token.
        """
        cfg = cherrypy.tree.apps[''].cfg
        if cfg.disable_ssh_keys:
            raise cherrypy.HTTPError(400)
        userobj = self._get_user(username)
        # Validate form method.
        form = DeleteTokenForm()
        if form.validate():
            # Get user
            if form.save_to_db(userobj):
                flash(_('Access token revoked.'))
        if form.error_message:
            flash(form.error_message, level='error')
        raise cherrypy.HTTPRedirect(url_for('admin', 'users', 'edit', username))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    def delete(self, username=None, **kwargs):
        """
        Delete a user
        """
        userobj = self._get_user(username)
        # Validate form method.
        form = DeleteUserForm()
        if form.validate():
            if form.save_to_db(userobj):
                flash(_("User account removed."))
        if form.error_message:
            flash(form.error_message, level='error')
        raise cherrypy.HTTPRedirect(url_for('admin', 'users'))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out()
    @cherrypy.tools.datatables_out(search_columns=[Message.model_summary, Message.body, Message.changes])
    def messages(self, username_or_id, **kwargs):
        # Return Not found if user doesn't exists
        user = self._get_user(username_or_id)
        # Query Object Messages
        query = (
            Message.query.with_entities(
                Message.date,
                Message.author_username,
                Message.model_id,
                Message.model_name,
                Message.model_summary,
                Message.type,
                Message.body,
                Message.changes,
            )
            .order_by(Message.date.desc())
            .filter(Message.model_id == user.id, Message.model_name == user._get_message_model_name())
        )
        return query

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['POST'])
    def refresh_repos(self, username_or_id, **kwargs):
        user = UserObject.get_user(username_or_id)
        if user is None:
            raise cherrypy.HTTPError(400, _("User %s doesn't exists") % username_or_id)
        user.refresh_repos(delete=True)
        flash(_("Repositories successfully updated"))
        raise cherrypy.HTTPRedirect(url_for('admin', 'users', 'edit', username_or_id))


@cherrypy.expose
@cherrypy.tools.is_admin()
@cherrypy.tools.required_scope(scope='all,admin_read_users')
class AdminApiUsers:
    ROLES_MAP = {v: k for k, v in UserObject.ROLES.items()}

    def _to_json(self, user_obj, detailed=False):
        """User object as json."""
        data = {
            "id": user_obj.id,
            "username": user_obj.username,
            "fullname": user_obj.fullname,
            "email": user_obj.email,
            "lang": user_obj.lang,
            "mfa": user_obj.mfa,
            "role": self.ROLES_MAP.get(user_obj.role, None),
            "report_time_range": user_obj.report_time_range,
        }
        if detailed:
            data.update(
                {
                    "disk_usage": user_obj.disk_usage,
                    "disk_quota": user_obj.disk_quota,
                    "disk_usage_threshold": user_obj.disk_usage_threshold,
                    "repos": [
                        {
                            # database fields.
                            "name": repo_obj.name,
                            "maxage": repo_obj.maxage,
                            "keepdays": repo_obj.keepdays,
                            "ignore_weekday": repo_obj.ignore_weekday,
                            # repository fields.
                            "display_name": repo_obj.display_name,
                            "last_backup_date": repo_obj.last_backup_date,
                            "status": repo_obj.status[0],
                            "encoding": repo_obj.encoding,
                        }
                        for repo_obj in user_obj.repo_objs
                    ],
                }
            )
        return data

    def list(self):
        """
        List all users.

        Return a list of user information without repositories and disk quota.

        **Example Response**

        ```json
        [
            {
                "id": 1,
                "username": "admin",
                "fullname": "",
                "email": "",
                "lang": "",
                "mfa": 0,
                "role": "admin",
                "report_time_range": 0
            },
            {
                "id": 2,
                "username": "newuser",
                "fullname": "New User",
                "email": "test@example.com",
                "lang": "fr",
                "mfa": 1,
                "role": "user",
                "report_time_range": 0
            }
        ]
        ```

        **Fields in JSON Payload**

        - `id`: The title or name associated with the SSH key.
        - `email`: The email address of the user.
        - `username`: The username of the user.
        - `fullname`: The user full name.
        - `report_time_range`: The interval between email report sent to user in number of days.
        - `lang` : The user prefered language.
        - `mfa`: Multi-factor enabled (1) or disabled (0).
        - `role`: User's role.

        """
        return [self._to_json(user_obj) for user_obj in UserObject.query.all()]

    def get(self, username_or_id):
        """
        Return specific user information for the given id or username.

        Returns detailed information for the user identified by `<userid>` or `<username>`.

        **Example Response**

        ```json
        {
          "id": 2,
          "username": "newuser",
          "fullname": "New User",
          "email": "test@example.com",
          "lang": "fr",
          "mfa": 1,
          "role": "user",
          "report_time_range": 0,
          "repos":[],
          "disk_quota":0,
          "disk_usage":0
        }
        ```
        """
        user_obj = UserObject.get_user(username_or_id)
        if user_obj is None:
            raise cherrypy.NotFound()
        return self._to_json(user_obj, detailed=True)

    @cherrypy.tools.required_scope(scope='all,admin_write_users')
    def delete(self, username_or_id, **kwargs):
        """
        Delete the user identified by the given username or id.

        Returns status 200 OK on success.
        """
        user_obj = UserObject.get_user(username_or_id)
        if user_obj is None:
            raise cherrypy.NotFound()
        form = DeleteUserForm(obj=user_obj)
        # Don't validation confirmation in API.
        del form.confirm
        if form.validate() and form.save_to_db(user_obj):
            return {}
        if form.error_message:
            raise cherrypy.HTTPError(400, form.error_message)

    @cherrypy.tools.required_scope(scope='all,admin_write_users')
    def post(self, username_or_id=None, **kwargs):
        """
        Create new user or update existing user.

        To create a new user, the minimum is to provide a value for `username`.

        **Example Body**

        ```
        {
          "username": "newuser",
          "fullname": "New User",
          "email": "test@example.com",
          "lang": "fr",
          "mfa": 1,
          "role": "user",
          "report_time_range": 0,
          "disk_quota": 0,
          "disk_usage": 0
        }
        ```

        Returns status 200 OK on success with user object created as Json.
        """
        # Query existing object for update.
        user_obj = None
        if username_or_id is not None:
            user_obj = UserObject.get_user(username_or_id)
            if user_obj is None:
                raise cherrypy.NotFound()
        # Validate input data.
        form = EditUserForm(obj=user_obj, json=1)
        if form.strict_validate():
            # Create user if required.
            if user_obj is None:
                user_obj = UserObject.add_user(form.username.data)
            if form.save_to_db(user_obj):
                # Return Location and object as json.
                cherrypy.response.headers['Location'] = url_for(cherrypy.url(base=''), str(user_obj.id))
                return self._to_json(user_obj)
        raise cherrypy.HTTPError(400, form.error_message)
