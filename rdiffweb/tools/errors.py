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
import sys

import cherrypy


def handle_exception(error_table):
    t = sys.exc_info()[0]
    code = error_table.get(t, 500)
    cherrypy.serving.request.error_response = cherrypy.HTTPError(code).set_response


cherrypy.tools.errors = cherrypy.Tool('before_error_response', handle_exception, priority=90)
