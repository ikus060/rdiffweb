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
"""
Created on Nov 16, 2017

@author: Patrik Dufresne
"""


import logging

import cherrypy
from wtforms.fields import SelectField, StringField
from wtforms.validators import Length, Optional, Regexp

from rdiffweb.controller import Controller
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.model import UserObject

try:
    from wtforms.fields import EmailField  # wtform >=3
except ImportError:
    from wtforms.fields.html5 import EmailField  # wtform <3

from rdiffweb.tools.i18n import gettext_lazy as _
from rdiffweb.tools.i18n import list_available_locales

logger = logging.getLogger(__name__)


def required_scope(scope):
    """
    Check the current authentication has the required scope to access the resource.
    """
    # Convert single scope or scope list to array.
    if isinstance(scope, str):
        scope = scope.split(',')
    # Get the current user scope
    current_scope = getattr(cherrypy.serving.request, 'scope', [])
    # Check if our current_scope match any of the required scope.
    if current_scope:
        for s in scope:
            if s in current_scope:
                return True
    raise cherrypy.HTTPError(403)


# Make sure it's running after authentication (priority = 72)
cherrypy.tools.required_scope = cherrypy.Tool('before_handler', required_scope, priority=75)


def _checkpassword(realm, username, password):
    """
    Check basic authentication.
    """
    # Validate username
    userobj = UserObject.get_user(username)
    if userobj is not None:
        # Verify if the password matches a token.
        access_token = userobj.validate_access_token(password)
        if access_token:
            access_token.accessed()
            access_token.commit()
            cherrypy.serving.request.scope = access_token.scope
            return True
        # Disable password authentication for MFA
        if userobj.mfa == UserObject.ENABLED_MFA:
            cherrypy.tools.ratelimit.hit()
            return False
    # Otherwise validate username password
    valid = any(cherrypy.engine.publish('login', username, password))
    if valid:
        # Store scope
        cherrypy.serving.request.scope = ['all']
        return True
    # When invalid, we need to increase the rate limit.
    cherrypy.tools.ratelimit.hit()
    return False


class CurrentUserForm(CherryForm):
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
        user.add()


@cherrypy.expose
@cherrypy.tools.required_scope(scope='all,read_user,write_user')
class ApiCurrentUser(Controller):
    def get(self):
        """
        Return current user information and settings.
        """
        u = self.app.currentuser
        if u.refresh_repos():
            u.commit()
        return {
            "userid": u.userid,
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
        # Validate input data.
        userobj = self.app.currentuser
        form = CurrentUserForm(obj=userobj, json=1)
        if not form.strict_validate():
            raise cherrypy.HTTPError(400, form.error_message)
        # Apply changes
        try:
            form.populate_obj(userobj)
            userobj.commit()
        except Exception as e:
            userobj.rollback()
            raise cherrypy.HTTPError(400, str(e))


@cherrypy.expose
@cherrypy.tools.json_out(on=True)
@cherrypy.tools.json_in(on=True, force=False)
@cherrypy.config(**{'error_page.default': False})
@cherrypy.tools.auth_basic(realm='rdiffweb', checkpassword=_checkpassword, priority=70)
@cherrypy.tools.auth_form(on=False)
@cherrypy.tools.auth_mfa(on=False)
@cherrypy.tools.i18n(on=False)
@cherrypy.tools.ratelimit(scope='rdiffweb-api', hit=0, priority=69)
@cherrypy.tools.sessions(on=False)
class ApiPage(Controller):
    """
    This class provide a restful API to access some of the rdiffweb resources.
    """

    currentuser = ApiCurrentUser()

    def get(self):
        return {
            "version": self.app.version,
        }
