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

import cherrypy
from wtforms.fields import SelectField, StringField
from wtforms.validators import Length, Optional, Regexp

from rdiffweb.controller import Controller
from rdiffweb.controller.formdb import DbForm
from rdiffweb.controller.page_pref_sshkeys import ApiSshKeys
from rdiffweb.controller.page_pref_tokens import ApiTokens
from rdiffweb.controller.page_settings import ApiRepos
from rdiffweb.core.model import UserObject
from rdiffweb.tools.i18n import gettext_lazy as _
from rdiffweb.tools.i18n import list_available_locales

try:
    from wtforms.fields import EmailField  # wtform >=3
except ImportError:
    from wtforms.fields.html5 import EmailField  # wtform <3


class CurrentUserForm(DbForm):
    """
    Form used to validate input data for REST api request.
    """

    fullname = StringField(
        validators=[
            Optional(),
            Length(max=256, message=_('Fullname too long.')),
            Regexp(UserObject.PATTERN_FULLNAME, message=_('Must not contain any special characters.')),
        ],
    )
    email = EmailField(
        validators=[
            Optional(),
            Length(max=256, message=_("Email too long.")),
            Regexp(UserObject.PATTERN_EMAIL, message=_("Must be a valid email address.")),
        ],
    )
    lang = SelectField()
    report_time_range = SelectField(
        choices=[
            (0, _('Never')),
            (1, _('Daily')),
            (7, _('Weekly')),
            (30, _('Monthly')),
        ],
        coerce=int,
        default='0',
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        languages = [(locale.language, locale.display_name.capitalize()) for locale in list_available_locales()]
        languages = sorted(languages, key=lambda x: x[1])
        languages.insert(0, ('', _('(default)')))
        self.lang.choices = languages

    def populate_obj(self, user):
        user.fullname = self.fullname.data
        user.email = self.email.data
        user.lang = self.lang.data
        user.report_time_range = self.report_time_range.data


@cherrypy.expose
@cherrypy.tools.required_scope(scope='all,read_user,write_user')
class ApiCurrentUser(Controller):
    sshkeys = ApiSshKeys()
    tokens = ApiTokens()
    repos = ApiRepos()

    def get(self):
        """
        Returns information about the current user, including user settings and a list of repositories.

        **Example Response**

        ```json
        {
            "email": "user@example.com",
            "username": "admin",
            "fullname": "John Smith",
            "disk_usage": 6642954240,
            "disk_quota": 7904514048,
            "repos": [
                {
                "name": "backups/Desktop/C",
                "maxage": 0,
                "keepdays": -1,
                "last_backup_date": "2019-08-29T09:42:38-04:00",
                "status": "ok",
                "encoding": "utf-8"
                },
                // ... additional repository entries ...
            ]
        }
        ```

        **Fields in JSON Payload**

        - `email`: The email address of the user.
        - `username`: The username of the user.
        - `fullname`: The user full name.
        - `disk_usage`: The current disk space usage of the user.
        - `disk_quota`: The quota of disk space allocated to the user.
        - `report_time_range`: The interval between email report sent to user in number of days.
        - `repos`: An array of repositories associated with the user.
        - `name`: The name of the repository.
        - `maxage`: Maximum age for stored backups.
        - `keepdays`: Number of days to keep backups (-1 for indefinite).
        - `last_backup_date`: The date and time of the last backup.
        - `status`: Current status of the repository (e.g., "ok" or "in_progress").
        - `encoding`: The encoding used for the repository.

        """
        u = cherrypy.serving.request.currentuser
        if u.refresh_repos():
            u.commit()
        return {
            "id": u.id,
            "username": u.username,
            "fullname": u.fullname,
            "email": u.email,
            "disk_usage": u.disk_usage,
            "disk_quota": u.disk_quota,
            "lang": u.lang,
            "mfa": u.lang,
            "role": u.role,
            "report_time_range": u.report_time_range,
            "repos": [
                {
                    # Database fields.
                    "name": repo_obj.name,
                    "maxage": repo_obj.maxage,
                    "keepdays": repo_obj.keepdays,
                    "ignore_weekday": repo_obj.ignore_weekday,
                    # Repository fields.
                    "display_name": repo_obj.display_name,
                    "last_backup_date": repo_obj.last_backup_date,
                    "status": repo_obj.status[0],
                    "encoding": repo_obj.encoding,
                }
                for repo_obj in u.repo_objs
            ],
        }

    @cherrypy.tools.required_scope(scope='all,write_user')
    def post(self, **kwargs):
        """
        Update current user information: fullname, email, lang and report_time_range

        Updates some of the user's settings, such as fullname, email, lang, and report_time_range.

        Returns status 200 OK on success.
        """
        # Validate input data.
        userobj = cherrypy.serving.request.currentuser
        form = CurrentUserForm(obj=userobj, json=1)
        if not form.strict_validate():
            raise cherrypy.HTTPError(400, form.error_message)
        # Apply changes
        if form.save_to_db(userobj):
            return None
        raise cherrypy.HTTPError(400, form.error_message)
