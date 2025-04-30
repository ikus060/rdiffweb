# udb, A web interface to manage IT network
# Copyright (C) 2023 IKUS Software inc.
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
