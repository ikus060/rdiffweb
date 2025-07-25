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
from wtforms import validators
from wtforms.fields import IntegerField, StringField

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.model import SessionObject
from rdiffweb.tools.i18n import ugettext as _


class RevokeSessionForm(CherryForm):
    action = StringField(validators=[validators.regexp('delete')])
    number = IntegerField(validators=[validators.data_required()])


class PagePrefSession(Controller):
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    def default(self, **kwargs):
        """
        Show user sessions
        """
        # Delete session on form submit
        form = RevokeSessionForm()
        if form.is_submitted():
            if form.validate():
                session = SessionObject.query.filter(
                    SessionObject.username == self.app.currentuser.username, SessionObject.number == form.number.data
                ).first()
                if not session:
                    flash(_('The given session cannot be removed because it cannot be found.'), level='warning')
                elif session.id == cherrypy.session.id:
                    flash(_('You cannot revoke your current session.'), level='warning')
                else:
                    session.delete()
                    session.commit()
                    flash(_('The session was successfully revoked.'), level='success')
            else:
                flash(form.error_message, level='error')
        # Get list of current user's session
        obj_list = SessionObject.query.filter(SessionObject.username == self.app.currentuser.username).all()
        active_sessions = [
            {
                'number': obj.number,
                'access_time': obj.data.get('access_time', None),
                'current': cherrypy.session.id == obj.id,
                'expiration_time': obj.expiration_time,
                'ip_address': obj.data.get('ip_address', None),
                'login_time': obj.data.get('login_time', None),
                'user_agent': obj.data.get('user_agent', None),
                'login_persistent': obj.data.get('login_persistent', None),
                'username': obj.username,
            }
            for obj in obj_list
        ]
        return self._compile_template("prefs_session.html", active_sessions=active_sessions)
