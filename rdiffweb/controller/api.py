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
Created on Nov 16, 2017

@author: Patrik Dufresne
"""
# Define the logger


import logging

import cherrypy

from rdiffweb.controller import Controller
from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import UserObject

try:
    import simplejson as json
except ImportError:
    import json

logger = logging.getLogger(__name__)


def json_handler(*args, **kwargs):
    """Custom json handle to convert RdiffDate to str."""
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)

    def default(o):
        if isinstance(o, RdiffTime):
            return str(o)
        raise TypeError(repr(o) + " is not JSON serializable")

    encode = json.JSONEncoder(default=default, ensure_ascii=False).iterencode
    for chunk in encode(value):
        yield chunk.encode('utf-8')


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
            return True
        # Disable password authentication for MFA
        if userobj.mfa == UserObject.ENABLED_MFA:
            cherrypy.tools.ratelimit.hit()
            return False
    # Otherwise validate username password
    valid = any(cherrypy.engine.publish('login', username, password))
    if not valid:
        # When invalid, we need to increase the rate limit.
        cherrypy.tools.ratelimit.hit()
    return valid


class ApiCurrentUser(Controller):
    @cherrypy.expose
    def default(self):
        u = self.app.currentuser
        if u.refresh_repos():
            u.commit()
        return {
            "email": u.email,
            "username": u.username,
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


@cherrypy.tools.json_out(handler=json_handler)
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
    def index(self):
        return {
            "version": self.app.version,
        }
