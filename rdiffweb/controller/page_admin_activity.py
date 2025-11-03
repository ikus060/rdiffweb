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

from collections import namedtuple

import cherrypy
from sqlalchemy import desc, or_

from rdiffweb.controller import Controller, validate_int
from rdiffweb.core.model import Message, UserObject
from rdiffweb.tools.i18n import gettext_lazy as _

ActivityRow = namedtuple(
    'ActivityRow', ['date', 'author_name', 'model_id', 'model_name', 'model_summary', 'type', 'body', 'changes']
)


@cherrypy.tools.is_admin()
class AdminActivityPage(Controller):
    """
    Display server activities.
    """

    @cherrypy.expose
    def index(self):
        """
        Show server activity.
        """
        return self._compile_template("admin_activity.html")

    @cherrypy.expose()
    @cherrypy.tools.json_out()
    def data_json(self, draw=None, start='0', length='10', **kwargs):
        """
        Return list of messages.
        """
        start = validate_int(start, min=0)
        length = validate_int(length, min=1, max=100)

        # Run the queries
        query = Message.query.with_entities(
            Message.date,
            UserObject.username.label('author_name'),
            Message.model_id,
            Message.model_name,
            Message.model_summary,
            Message.type,
            Message.body,
            Message._changes.label('changes'),
        ).outerjoin(Message.author)

        # Get total count before filtering
        total = query.count()

        # Apply sorting - default sort by date
        order_idx = validate_int(
            kwargs.get('order[0][column]', '4'),  # date
            min=0,
            max=len(query.column_descriptions) - 1,
            message=_('Invalid column for sorting'),
        )
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

        # Apply model_name filtering
        # With multiple selection, this is a regex pattern similar to (model1|model2|model3)
        search_model = kwargs.get('columns[3][search][value]', '')
        if search_model:
            model_names = search_model.strip('()').split('|')
            query = query.filter(Message.model_name.in_(model_names))

        # Count result.
        filtered = query.count()
        data = query.offset(start).limit(length).all()

        # Return data as Json
        return {
            'draw': draw,
            'recordsTotal': total,
            'recordsFiltered': filtered,
            'data': [
                ActivityRow(
                    date=row.date.isoformat(),
                    author_name=row.author_name or str(_('System')),
                    model_id=row.model_id,
                    model_name=row.model_name,
                    model_summary=row.model_summary,
                    type=row.type,
                    body=row.body,
                    changes=Message.json_changes(row.changes),
                )
                for row in data
            ],
        }
