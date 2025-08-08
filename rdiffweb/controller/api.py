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

import cherrypy

from rdiffweb.controller import Controller
from rdiffweb.controller.api_currentuser import ApiCurrentUser
from rdiffweb.controller.api_openapi import OpenAPI
from rdiffweb.controller.page_admin_users import AdminApiUsers
from rdiffweb.core.model import UserObject

logger = logging.getLogger(__name__)


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
            cherrypy.tools.ratelimit.increase_hit()
            return False
    # Otherwise validate username password
    valid = cherrypy.tools.auth.login_with_credentials(username, password)
    if valid:
        # Store scope
        cherrypy.serving.request.scope = ['all']
        return True
    # When invalid, we need to increase the rate limit.
    cherrypy.tools.ratelimit.increase_hit()
    return False


@cherrypy.expose
@cherrypy.tools.allow(on=False)
@cherrypy.tools.json_out(on=True)
@cherrypy.tools.json_in(on=True, force=False)
@cherrypy.tools.auth_basic(realm='rdiffweb', checkpassword=_checkpassword, priority=70)
@cherrypy.tools.auth(on=True, redirect=False)
@cherrypy.tools.auth_mfa(on=False)
@cherrypy.tools.i18n(on=False)
@cherrypy.tools.ratelimit(scope='rdiffweb-api', hit=0, priority=69)
@cherrypy.tools.sessions(on=False)
class ApiPage(Controller):
    """
    This class provide a restful API to access some of the rdiffweb resources.
    """

    currentuser = ApiCurrentUser()
    openapi_json = OpenAPI()
    users = AdminApiUsers()

    def get(self):
        """
        Returns the current application version in JSON format.

        **Example Response**

        ```json
        {
            "version": "1.2.8"
        }
        ```

        """
        return {
            "version": self.app.version,
        }
