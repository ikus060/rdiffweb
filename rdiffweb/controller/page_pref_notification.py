# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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


import cherrypy
from wtforms.fields import HiddenField, SelectField, SubmitField

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.form import CherryForm
from rdiffweb.tools.i18n import ugettext as _


class MaxAgeField(SelectField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            choices=[
                (0, _('disabled')),
                (1, _('1 day')),
                (2, _('2 days')),
                (3, _('3 days')),
                (4, _('4 days')),
                (5, _('5 days')),
                (6, _('6 days')),
                (7, _('1 week')),
                (14, _('2 weeks')),
                (21, _('3 weeks')),
                (28, _('4 weeks')),
                (31, _('1 month')),
            ],
            coerce=int,
            **kwargs
        )


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
        except Exception as e:
            userobj.rollback()
            flash(str(e), level='warning')


class PagePrefNotification(Controller):
    @cherrypy.expose
    def default(self, action=None, **kwargs):
        # Process the parameters.
        form = NotificationForm.create_form(self.app.currentuser)
        if form.validate_on_submit():
            form.populate_obj(self.app.currentuser)
            flash(_('Notification settings updated successfully.'), level='success')

        params = {
            'email': self.app.currentuser.email,
            'form': form,
        }
        return self._compile_template("prefs_notification.html", **params)
