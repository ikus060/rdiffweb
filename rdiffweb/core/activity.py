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
"""
Plugin used to send email to users when their repository is getting too old.
User can control the notification period.
"""
import logging
from datetime import datetime, timezone

import cherrypy
from cherrypy.process.plugins import SimplePlugin

from rdiffweb.core.librdiff import unquote
from rdiffweb.core.model import Message, UserObject
from rdiffweb.plugins.scheduler import clear_db_sessions
from rdiffweb.tools.i18n import ugettext as _

logger = logging.getLogger(__name__)


@clear_db_sessions
def _log_user_login(user_id, date, ip_address, user_agent):
    """Used to log user loging asynchronously."""
    user = UserObject.get_user(user_id)
    user.add_message(
        Message(
            body=_("User login to web application"),
            type=Message.TYPE_EVENT,
            date=date,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    )
    user.commit()


class ActivityPlugin(SimplePlugin):
    """
    Log application activities into database.
    """

    def start(self):
        self.bus.log('Start Activity plugin')
        self.bus.subscribe('restore_path', self.restore_path)
        self.bus.subscribe('delete_path', self.delete_path)
        self.bus.subscribe('user_login', self.user_login)

    def stop(self):
        self.bus.log('Stop Activity plugin')
        self.bus.unsubscribe('restore_path', self.restore_path)
        self.bus.unsubscribe('delete_path', self.delete_path)
        self.bus.unsubscribe('user_login', self.user_login)

    def graceful(self):
        """Reload of subscribers."""
        self.stop()
        self.start()

    def restore_path(self, repo, path):
        repo.add_message(Message(body=_("Restore file path %s") % path, type=Message.TYPE_EVENT))

    def delete_path(self, repo, path):
        display_name = repo._decode(unquote(path))
        repo.add_message(Message(body=_("Delete file path: %s") % display_name, type=Message.TYPE_EVENT))

    def user_login(self, userobj):
        # Log user_login in a different thread.
        if hasattr(userobj, 'add_message'):
            request = cherrypy.serving.request
            now = datetime.now(timezone.utc)
            self.bus.publish(
                'scheduler:add_job_now',
                _log_user_login,
                user_id=userobj.id,
                date=now,
                ip_address=request.remote.ip,
                user_agent=request.headers.get('User-Agent', ''),
            )


cherrypy.activity = ActivityPlugin(cherrypy.engine)
cherrypy.activity.subscribe()

cherrypy.config.namespaces['activity'] = lambda key, value: setattr(cherrypy.activity, key, value)
