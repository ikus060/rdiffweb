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

from rdiffweb.controller import Controller
from rdiffweb.core.model import UserObject

logger = logging.getLogger(__name__)


def required_scope(scope):
    """
    Check the current authentication has the requried scope to access the resource.
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


@cherrypy.expose
@cherrypy.tools.required_scope(scope='all,read_user,write_user')
class ApiCurrentUser(Controller):
    @cherrypy.expose
    def get(self):

        u = self.app.currentuser
        if u.refresh_repos():
            u.commit()
        return {
            "email": u.email,
            "username": u.username,
            "disk_usage": u.disk_usage,
            "disk_quota": u.disk_quota,
            "repos": [
                {
                    # Database fields.
                    "name": repo_obj.name,
                    "maxage": repo_obj.maxage,
                    "keepdays": repo_obj.keepdays,
                    # Repository fields.
                    "display_name": repo_obj.display_name,
                    "last_backup_date": repo_obj.last_backup_date,
                    "status": repo_obj.status[0],
                    "encoding": repo_obj.encoding,
                }
                for repo_obj in u.repo_objs
            ],
        }


@cherrypy.expose
@cherrypy.tools.json_out(on=True)
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

    @cherrypy.expose
    def get(self):
        return {
            "version": self.app.version,
        }
