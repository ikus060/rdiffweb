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
from rdiffweb.controller import Controller, validate_isinstance, validate
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.i18n import ugettext as _

from builtins import bytes
import cherrypy

# Define the logger
_logger = logging.getLogger(__name__)


@poppath()
class SettingsPage(Controller):

    @cherrypy.expose
    def index(self, path=b""):
        validate_isinstance(path, bytes)
        repo_obj = self.app.currentuser.get_repo(path)
        # Get page data.
        params = {
            'repo_name': repo_obj.display_name,
            'repo_path': repo_obj.path,
            'current_encoding': repo_obj.encoding,
            'keepdays': repo_obj.keepdays,
        }
        # Generate page.
        return self._compile_template("settings.html", **params)
    
    
@poppath()
class SetEncodingPage(Controller):
    
    @cherrypy.expose()
    def index(self, path=b'', new_encoding=None):
        """
        Update repository encoding via Ajax.
        """
        validate_isinstance(path, bytes)
        validate(new_encoding)
        repo_obj = self.app.currentuser.get_repo(path)
        try:
            repo_obj.encoding = new_encoding
        except ValueError:
            raise cherrypy.HTTPError(400, _("invalid encoding value"))
        return _("Updated")
    
    
@poppath()
class RemoveOlderPage(Controller):

    @cherrypy.expose()
    def index(self, path=b"", keepdays=None):
        validate_isinstance(path, bytes)
        validate(keepdays)

        # Get repository object from user database.
        r = self.app.currentuser.get_repo(path)

        # Update the database.
        try:
            r.keepdays = keepdays
        except ValueError:
            _logger.warning("invalid keepdays value %r", keepdays)
            raise cherrypy.HTTPError(400, _("Invalid value"))            

        return _("Updated")

    
@poppath()
class DeleteRepoPage(Controller):

    @cherrypy.expose
    def index(self, path=b"", **kwargs):
        """
        Delete the repository.
        """
        validate_isinstance(path, bytes)

        # Check user permissions
        repo_obj = self.app.currentuser.get_repo(path)

        # Validate the name
        confirm_name = kwargs.get('confirm_name', None)
        if confirm_name != repo_obj.display_name:
            _logger.info("bad confirmation %r != %r", confirm_name, repo_obj.display_name)
            raise cherrypy.HTTPError(400)

        # Refresh repository list
        repo_obj.delete()

        raise cherrypy.HTTPRedirect("/")
