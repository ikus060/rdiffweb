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

from rdiffweb.core.model import Message


@cherrypy.tools.is_admin()
class AdminActivityPage:
    """
    Display server activities.
    """

    @cherrypy.expose
    @cherrypy.tools.jinja2(template="admin_activity.html")
    def index(self):
        return {}

    @cherrypy.expose()
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out()
    @cherrypy.tools.datatables_out(search_columns=[Message.model_summary, Message.body, Message.changes])
    def data_json(self, **kwargs):
        """
        Return list of all messages.
        """
        return Message.query.with_entities(
            Message.date,
            Message.author_username,
            Message.model_id,
            Message.model_name,
            Message.model_summary,
            Message.type,
            Message.body,
            Message.changes,
        ).outerjoin(Message.author)
