# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Plugin used to send email to users when their repository is getting too old.
User can control the notification period.
"""


import logging

import cherrypy
from wtforms.fields import HiddenField, RadioField, SubmitField

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.controller.page_settings import MaxAgeField
from rdiffweb.tools.i18n import gettext_lazy as _

logger = logging.getLogger(__name__)


class ReportForm(CherryForm):
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
        return self.action.data == 'set_report_info' and super().is_submitted()

    def populate_obj(self, userobj):
        # Simply push the time_range to user's data
        try:
            userobj.report_time_range = self.report_time_range.data
            userobj.commit()
            # Validate if a report could be sent
            if self.send_report.data:
                if not userobj.report_time_range:
                    raise ValueError(_('You must select a time range and save changes before sending a report.'))
                if not userobj.email:
                    raise ValueError(_('Could not send report to user without configured email.'))
                cherrypy.notification.send_report(userobj, force=True)
                flash(_("Report sent successfully."), level='success')
            else:
                flash(_("Report settings updated successfully."), level='success')
            return True
        except Exception as e:
            userobj.rollback()
            logger.warning('fail to save report settings', exc_info=1)
            flash(str(e), level='warning')
            return False


class NotificationForm(CherryForm):
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
        return self.action.data == 'set_notification_info' and super().is_submitted()

    def populate_obj(self, userobj):
        try:
            # Loop trough user repo and update max age.
            for repo in userobj.repo_objs:
                if repo.display_name in self:
                    # Update the maxage
                    repo.maxage = self[repo.display_name].data
            userobj.commit()
            flash(_("Notification settings updated successfully."), level='success')
            return True
        except Exception as e:
            userobj.rollback()
            flash(str(e), level='warning')
            return False


class PagePrefNotification(Controller):
    @cherrypy.expose
    @cherrypy.tools.ratelimit(methods=['POST'])
    def default(self, **kwargs):
        # Process the parameters.
        report_form = ReportForm(obj=self.app.currentuser)
        notification_form = NotificationForm.create_form(self.app.currentuser)
        if report_form.is_submitted():
            if report_form.validate():
                if report_form.populate_obj(self.app.currentuser):
                    raise cherrypy.HTTPRedirect("")
            else:
                flash(report_form.error_message, level='error')
        elif notification_form.is_submitted():
            if notification_form.validate():
                if notification_form.populate_obj(self.app.currentuser):
                    raise cherrypy.HTTPRedirect("")
            else:
                flash(notification_form.error_message, level='error')
        params = {
            'email': self.app.currentuser.email,
            'report_form': report_form,
            'notification_form': notification_form,
        }
        return self._compile_template("prefs_notification.html", **params)
