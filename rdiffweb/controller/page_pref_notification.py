# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2026 rdiffweb contributors
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
from cherrypy_foundation.flash import flash
from cherrypy_foundation.tools.i18n import gettext_lazy as _
from wtforms.fields import RadioField, SubmitField

from rdiffweb.controller.formdb import DbForm
from rdiffweb.controller.widgets import SelectMultipleWidget

logger = logging.getLogger(__name__)


class NotificationForm(DbForm):
    report_time_range = RadioField(
        _('Send me a backup status report'),
        widget=SelectMultipleWidget(),
        choices=[
            (0, _('Never - No report emails will be sent.')),
            (1, _('Daily - Receive a report every day.')),
            (7, _('Weekly - Receive a report every Monday morning.')),
            (30, _('Monthly - Receive a report on the first day of each month.')),
        ],
        coerce=int,
    )

    send_report = SubmitField(_('Save and send report'))

    def populate_obj(self, user):
        user.report_time_range = self.report_time_range.data
        if self.send_report.data:
            if not user.report_time_range:
                raise ValueError(_('You must select a time range and save changes before sending a report.'))
            if not user.email:
                raise ValueError(_('Could not send report to user without configured email.'))
            try:
                cherrypy.notification.send_report(user, force=True)
                if hasattr(cherrypy.serving, 'session'):
                    flash(_("Report sent successfully."), level='success')
            except Exception:
                logger.exception("fail to send report", exc_info=1)
                flash(_("The report could not be sent. Check the server logs."), level='error')


class PagePrefNotification:

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    @cherrypy.tools.jinja2(template="prefs_notification.html")
    def default(self, **kwargs):
        """
        Show user notification settings
        """
        currentuser = cherrypy.serving.request.currentuser
        # Process the parameters.
        form = NotificationForm(obj=currentuser)
        if form.validate_on_submit():
            if form.save_to_db(currentuser):
                flash(_("Report settings updated successfully."), level='success')
                raise cherrypy.HTTPRedirect("")
        if form.error_message:
            flash(form.error_message, level='error')
        return {
            'email': currentuser.email,
            'form': form,
        }
