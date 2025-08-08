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


def is_admin():
    # Validate the permissions.
    if not cherrypy.serving.request.currentuser or not cherrypy.serving.request.currentuser.is_admin:
        raise cherrypy.HTTPError(404)


def is_maintainer():
    # Validate the permissions.
    if not cherrypy.serving.request.currentuser or not cherrypy.serving.request.currentuser.is_maintainer:
        raise cherrypy.HTTPError(404)


# Make sure it's running after authentication (priority = 72)
cherrypy.tools.is_admin = cherrypy.Tool('before_handler', is_admin, priority=80)
cherrypy.tools.is_maintainer = cherrypy.Tool('before_handler', is_maintainer, priority=80)
