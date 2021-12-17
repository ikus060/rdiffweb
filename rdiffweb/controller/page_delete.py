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
'''
Created on Apr. 5, 2021

@author: Patrik Dufresne <patrik@ikus-soft.com>
'''
# Define the logger

import logging

import cherrypy
from rdiffweb.controller import Controller
from rdiffweb.controller.cherrypy_wtf import CherryForm
from rdiffweb.controller.dispatch import poppath
from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from wtforms import validators
from wtforms.fields.core import StringField

_logger = logging.getLogger(__name__)


class DeleteRepoForm(CherryForm):
    confirm = StringField(_('Confirmation'), validators=[validators.data_required()])
    redirect = StringField(default='/')


@poppath()
class DeletePage(Controller):

    @cherrypy.expose
    @cherrypy.tools.errors(error_table={
        DoesNotExistError: 404,
        AccessDeniedError: 403,
    })
    def default(self, path=b"", **kwargs):
        # Check permissions on path/repo
        unused, path_obj = self.app.store.get_repo_path(path)
        # Check user's permissions
        is_maintainer()

        # validate form
        form = DeleteRepoForm()
        if not form.validate():
            raise cherrypy.HTTPError(400, form.error_message)

        # Validate the name
        if form.confirm.data != path_obj.display_name:
            _logger.info("do not delete repo, bad confirmation %r != %r", form.confirm.data, path_obj.display_name)
            raise cherrypy.HTTPError(400, 'bad confirmation')

        # Delete repository
        self.app.scheduler.add_task(path_obj.delete, args=[])
        raise cherrypy.HTTPRedirect(form.redirect.data)
