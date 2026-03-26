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
from collections import namedtuple

import cherrypy
from cherrypy_foundation.tools.i18n import gettext_lazy as _
from sqlalchemy import desc, or_

from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import Message, RepoObject, UserObject

from . import validate_int

logger = logging.getLogger(__name__)


RepoActivityRow = namedtuple('RepoActivityRow', ['date', 'author_name', 'type', 'body', 'changes'])


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
    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def data_json(self, path, draw=None, start='0', length='10', **kwargs):
        """
        Return list of messages.
        """
        start = validate_int(start, min=0)
        length = validate_int(length, min=1, max=100)

        # Return Not found if user doesn't exists
        repo_obj = RepoObject.get_repo(path)
        if repo_obj is None:
            raise cherrypy.HTTPError(400)

        # Run the queries
        query = (
            Message.query.with_entities(
                Message.date,
                UserObject.username.label('author_name'),
                Message.type,
                Message.body,
                Message._changes.label('changes'),
            )
            .filter(Message.model_id == repo_obj.id, Message.model_name == repo_obj._get_message_model_name())
            .outerjoin(Message.author)
        )

        # Get total count before filtering
        total = query.count()

        # Apply sorting - default sort by date
        try:
            order_idx = validate_int(kwargs.get('order[0][column]', '4'), min=0, max=len(query.column_descriptions) - 1)
        except ValueError:
            raise cherrypy.HTTPError(400, 'Invalid column for sorting')
        order_dir = kwargs.get('order[0][dir]', 'desc')
        order_col = query.column_descriptions[int(order_idx)]['expr']
        if order_dir == 'desc':
            query = query.order_by(desc(order_col))
        else:
            query = query.order_by(order_col)

        # Apply filtering
        search = kwargs.get('search[value]', '')
        if search:
            query = query.filter(
                or_(
                    Message.model_summary.like(f"%{search}%"),
                    Message.body.like(f"%{search}%"),
                    Message._changes.like(f"%{search}%"),
                )
            )

        # Apply type filtering
        # With multiple selection, this is a regex pattern similar to (model1|model2|model3)
        search_type = kwargs.get('columns[2][search][value]', '')
        if search_type:
            types = search_type.strip('()').split('|')
            query = query.filter(Message.type.in_(types))

        # Count result.
        filtered = query.count()
        data = query.offset(start).limit(length).all()

        # Return data as Json
        return {
            'draw': draw,
            'recordsTotal': total,
            'recordsFiltered': filtered,
            'data': [
                RepoActivityRow(
                    date=row.date.isoformat(),
                    author_name=row.author_name or str(_('System')),
                    type=row.type,
                    body=row.body,
                    changes=Message.json_changes(row.changes),
                )
                for row in data
            ],
        }
