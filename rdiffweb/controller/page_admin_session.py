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
from cherrypy_foundation.flash import flash
from cherrypy_foundation.tools.i18n import ugettext as _
from cherrypy_foundation.tools.sessions_timeout import SESSION_PERSISTENT, SESSION_START_TIME

from rdiffweb.controller.page_pref_session import RevokeSessionForm
from rdiffweb.core.model import SessionObject


@cherrypy.tools.is_admin()
class AdminSessionPage:

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    @cherrypy.tools.jinja2(template="admin_session.html")
    def index(self, **kwargs):
        """
        Show or remove user sessions
        """
        # Delete session on form submit
        form = RevokeSessionForm()
        if form.is_submitted():
            if form.validate():
                session = SessionObject.query.filter(SessionObject.number == form.number.data).first()
                if form.save_to_db(session):
                    flash(_('The session was successfully revoked.'), level='success')
            if form.error_message:
                flash(form.error_message, level='error')
            raise cherrypy.HTTPRedirect("")

        # Get list of current user's session
        obj_list = SessionObject.query.filter().order_by(SessionObject.access_time.desc()).all()
        active_sessions = [
            {
                'number': obj.number,
                'access_time': obj.data.get('access_time', None),
                'current': cherrypy.session.id == obj.session_id,
                'expiration_time': obj.expiration_time,
                'ip_address': obj.data.get('ip_address', None),
                'start_time': obj.data.get(SESSION_START_TIME, None),
                'user_agent': obj.data.get('user_agent', None),
                'login_persistent': obj.data.get(SESSION_PERSISTENT, None),
                'username': obj.username,
            }
            for obj in obj_list
        ]
        return {'active_sessions': active_sessions}
