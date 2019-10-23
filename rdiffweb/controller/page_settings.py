#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from rdiffweb.controller import Controller, validate, validate_int
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.i18n import ugettext as _

import cherrypy

# Define the logger
_logger = logging.getLogger(__name__)


@poppath()
class SettingsPage(Controller):

    @cherrypy.expose
    def default(self, path=b"", action=None, **kwargs):
        repo_obj = self.app.currentuser.get_repo(path)
        if action == 'delete':
            self._delete(repo_obj, **kwargs)
        if kwargs.get('keepdays'):
            return self._remove_older(repo_obj, **kwargs)
        elif kwargs.get('new_encoding'):
            return self._set_encoding(repo_obj, **kwargs)
        # Get page data.
        params = {
            'repo': repo_obj,
            'current_encoding': repo_obj.encoding,
            'keepdays': repo_obj.keepdays,
        }
        # Generate page.
        return self._compile_template("settings.html", **params)
    
    def _delete(self, repo_obj, **kwargs):
        """
        Delete the repository.
        """
        # Validate the name
        confirm = kwargs.get('confirm', None)
        if confirm != repo_obj.display_name:
            _logger.info("bad confirmation %r != %r", confirm, repo_obj.display_name)
            raise cherrypy.HTTPError(400)

        # Refresh repository list
        repo_obj.delete()

        raise cherrypy.HTTPRedirect("/")

    def _set_encoding(self, repo_obj, new_encoding=None):
        """
        Update repository encoding via Ajax.
        """
        validate(new_encoding)
        try:
            repo_obj.encoding = new_encoding
        except ValueError:
            raise cherrypy.HTTPError(400, _("invalid encoding value"))
        return _("Updated")

    def _remove_older(self, repo_obj, keepdays=None):
        validate_int(keepdays)
        # Update the database.
        try:
            repo_obj.keepdays = keepdays
        except ValueError:
            _logger.warning("invalid keepdays value %repo_obj", keepdays)
            raise cherrypy.HTTPError(400, _("Invalid value"))            

        return _("Updated")
