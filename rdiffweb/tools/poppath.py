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

from rdiffweb.core.rdw_helpers import unquote_url


def convert_path():
    """
    A tool to convert vpath to path once the handler was found.

    Used to merge the segment of URI into a single parameter denoting the
    repository path.
    """
    handler = cherrypy.serving.request.handler
    if hasattr(handler, 'kwargs'):
        handler.kwargs = {'path': b"/".join([unquote_url(segment) for segment in handler.args])}
        handler.args = []


cherrypy.tools.poppath = cherrypy.Tool('on_start_resource', convert_path, priority=15)
