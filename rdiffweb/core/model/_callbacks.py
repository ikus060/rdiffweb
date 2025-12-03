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
from sqlalchemy import event

Session = cherrypy.db.get_session()


def add_post_commit_tasks(session, *args):
    # Add task
    session.info.setdefault("_after_commit_tasks", []).append(args)


@event.listens_for(Session, 'after_rollback')
def reset_tasks(session):
    # Clear previous tasks.
    session.info.pop('_after_commit_tasks', None)


@event.listens_for(Session, 'after_transaction_end')
def run_tasks(session, transaction):
    if transaction.parent:
        return
    # Execute after commit tasks.
    if '_after_commit_tasks' in session.info:
        tasks = session.info.pop('_after_commit_tasks', None)
        for args in tasks:
            cherrypy.engine.publish(*args)
