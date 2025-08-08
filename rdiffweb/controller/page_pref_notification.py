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

import cherrypy
from wtforms.fields import HiddenField, RadioField, SubmitField

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.formdb import DbForm
from rdiffweb.controller.page_settings import MaxAgeField
from rdiffweb.tools.i18n import gettext_lazy as _

logger = logging.getLogger(__name__)


class ReportForm(DbForm):
    action = HiddenField(default="set_report_info")
    report_time_range = RadioField(
        _('Send me a backup status report'),
        choices=[
            (0, _('Never')),
            (1, _('Daily')),
            (7, _('Weekly')),
            (30, _('Monthly')),
        ],
        coerce=int,
    )
    set_report_info = SubmitField(_('Save changes'), render_kw={"class": "pull-left mr-2"})
    send_report = SubmitField(_('Save and send report'), render_kw={"class": "btn-secondary pull-left"})

    def is_submitted(self):
        return super().is_submitted() and self.action.default in self.action.raw_data

    def populate_obj(self, userobj):
        userobj.report_time_range = self.report_time_range.data
        if self.send_report.data:
            if not userobj.report_time_range:
                raise ValueError(_('You must select a time range and save changes before sending a report.'))
            if not userobj.email:
                raise ValueError(_('Could not send report to user without configured email.'))
            cherrypy.notification.send_report(userobj, force=True)
            if hasattr(cherrypy.serving, 'session'):
                flash(_("Report sent successfully."), level='success')


class NotificationForm(DbForm):
    action = HiddenField(default="set_notification_info")

    @classmethod
    def create_form(cls, userobj):
        # Create dynamic list of fields
        data = {}
        extends = {}
        for repo in userobj.repo_objs:
            extends[repo.display_name] = MaxAgeField(label=repo.display_name)
            data[repo.display_name] = repo.maxage
        extends['submit'] = SubmitField(label=_('Save changes'))
        # Create class
        sub_form = type('SubForm', (cls,), extends)
        return sub_form(data=data)

    def is_submitted(self):
        return super().is_submitted() and self.action.default in self.action.raw_data

    def populate_obj(self, userobj):
        # Loop trough user repo and update max age.
        for repo in userobj.repo_objs:
            if repo.display_name in self:
                # Update the maxage
                repo.maxage = self[repo.display_name].data


class PagePrefNotification(Controller):
    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET', 'POST'])
    @cherrypy.tools.ratelimit(methods=['POST'])
    def default(self, **kwargs):
        """
        Show user notification settings
        """
        currentuser = cherrypy.serving.request.currentuser
        # Process the parameters.
        report_form = ReportForm(obj=currentuser)
        notification_form = NotificationForm.create_form(currentuser)
        if report_form.validate_on_submit():
            if report_form.save_to_db(currentuser):
                flash(_("Report settings updated successfully."), level='success')
                raise cherrypy.HTTPRedirect("")

        elif notification_form.validate_on_submit():
            if notification_form.save_to_db(currentuser):
                flash(_("Notification settings updated successfully."), level='success')
                raise cherrypy.HTTPRedirect("")
        if report_form.error_message:
            flash(report_form.error_message, level='error')
        if notification_form.error_message:
            flash(notification_form.error_message, level='error')
        params = {
            'email': currentuser.email,
            'report_form': report_form,
            'notification_form': notification_form,
        }
        return self._compile_template("prefs_notification.html", **params)
