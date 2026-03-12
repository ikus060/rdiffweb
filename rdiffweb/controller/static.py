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

from importlib.resources import files

import cherrypy
from cherrypy_foundation.components import StaticMiddleware


@cherrypy.tools.auth(on=False)
@cherrypy.tools.i18n(on=False)
@cherrypy.tools.ratelimit(on=False)
@cherrypy.tools.secure_headers(on=False)
@cherrypy.tools.sessions(on=False)
class Static:

    components = StaticMiddleware()

    @cherrypy.expose
    @cherrypy.tools.staticdir(
        section="", match=r".*(\.js|\.css|\.png|\.woff|\.woff2)$", dir=files('rdiffweb') / 'static'
    )
    def default(self, *args, **kwargs):
        """This entry point is used to serve content of /static/ folder."""
        raise cherrypy.HTTPError(400)
