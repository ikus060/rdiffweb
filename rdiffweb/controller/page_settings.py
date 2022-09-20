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


import cherrypy

from rdiffweb.controller import Controller, validate, validate_int
from rdiffweb.controller.dispatch import poppath
from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject
from rdiffweb.tools.i18n import ugettext as _


@poppath()
class SettingsPage(Controller):
    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    def default(self, path=b"", action=None, **kwargs):
        repo_obj = RepoObject.get_repo(path)
        if cherrypy.request.method == 'POST':
            if kwargs.get('keepdays'):
                return self._remove_older(repo_obj, **kwargs)
            elif kwargs.get('new_encoding'):
                return self._set_encoding(repo_obj, **kwargs)
            elif kwargs.get('maxage'):
                return self._set_maxage(repo_obj, **kwargs)
        # Get page data.
        params = {
            'repo': repo_obj,
            'keepdays': repo_obj.keepdays,
        }
        # Generate page.
        return self._compile_template("settings.html", **params)

    def _set_encoding(self, repo_obj, new_encoding=None, **kwargs):
        """
        Update repository encoding via Ajax.
        """
        validate(new_encoding)
        try:
            repo_obj.encoding = new_encoding
        except ValueError:
            raise cherrypy.HTTPError(400, _("invalid encoding value"))
        return _("Updated")

    def _set_maxage(self, repo_obj, maxage=None, **kwargs):
        """
        Update repository maxage via Ajax.
        """
        validate_int(maxage)
        repo_obj.maxage = maxage
        return _("Updated")

    def _remove_older(self, repo_obj, keepdays=None, **kwargs):
        is_maintainer()
        validate_int(keepdays)
        # Update the database.
        repo_obj.keepdays = keepdays
        return _("Updated")
