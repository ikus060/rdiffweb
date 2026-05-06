# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2026 rdiffweb contributors
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

from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import Message, RepoObject, UserObject

logger = logging.getLogger(__name__)


@cherrypy.tools.poppath()
class RepoActivityPage:

    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.jinja2(template="repo_activity.html")
    @cherrypy.tools.poppath()
    def default(self, path, **kwargs):
        # Return Not found if user doesn't exists
        repo_obj = RepoObject.get_repo(path)
        if repo_obj is None:
            raise cherrypy.HTTPError(400)
        return {'repo': repo_obj}

    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out()
    @cherrypy.tools.datatables_out(search_columns=[Message.model_summary, Message.body, Message.changes])
    def data_json(self, path, **kwargs):
        """
        Return list of messages.
        """
        repo_obj = RepoObject.get_repo(path)
        if repo_obj is None:
            raise cherrypy.HTTPError(400)

        # Build queries
        return (
            Message.query.with_entities(
                Message.date,
                UserObject.username.label('author_username'),
                Message.model_id,
                Message.model_name,
                Message.model_summary,
                Message.type,
                Message.body,
                Message.changes,
            )
            .outerjoin(Message.author)
            .filter(Message.model_id == repo_obj.id, Message.model_name == repo_obj._get_message_model_name())
        )
