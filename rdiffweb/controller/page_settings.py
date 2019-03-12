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

import encodings
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

        _logger.debug("repo settings [%r]", path)

        # Check user permissions
        repo_obj = self.app.currentuser.get_repo_path(path)[0]
        r = self.app.currentuser.get_repo(repo_obj.path)

        # Get page data.
        params = {
            'repo_name': repo_obj.display_name,
            'repo_path': repo_obj.path,
            'current_encoding': encodings.normalize_encoding(repo_obj.get_encoding()),
            'keepdays': r.keepdays,
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

        _logger.debug("update repo [%r] settings [%r]", path, new_encoding)

        # Check user permissions
        repo_obj = self.app.currentuser.get_repo_path(path)[0]

        # Validate the encoding value
        new_codec = encodings.search_function(new_encoding.lower())
        if not new_codec:
            raise cherrypy.HTTPError(400, _("invalid encoding value"))

        new_encoding = new_codec.name
        if not isinstance(new_encoding, str):
            # Python 2
            new_encoding = new_encoding.decode('ascii')

        # Update the repository encoding
        _logger.info("updating repository [%s] encoding [%s]", repo_obj, new_encoding)
        repo_obj.set_encoding(new_encoding)

        return _("Updated")
    
    
@poppath()
class RemoveOlderPage(Controller):

    @cherrypy.expose()
    def index(self, path=b"", keepdays=None):
        validate_isinstance(path, bytes)
        validate(keepdays)
        _logger.debug("repo settings [%r]", path)

        # Get new value
        try:
            keepdays = int(keepdays)
        except:
            _logger.warning("invalid keepdays value %r", keepdays)
            raise cherrypy.HTTPError(400, _("Invalid value"))

        # Check user permissions
        repo_obj = self.app.currentuser.get_repo_path(path)[0]

        # Get repository object from user database.
        r = self.app.currentuser.get_repo(repo_obj.path)

        # Update the database.
        r.keepdays = keepdays

        return _("Updated")

    
@poppath()
class DeleteRepoPage(Controller):

    @cherrypy.expose
    def index(self, path=b"", **kwargs):
        """
        Delete the repository.
        """
        validate_isinstance(path, bytes)
        _logger.debug("repo delete [%r]", path)

        # Check user permissions
        repo_obj = self.app.currentuser.get_repo_path(path)[0]

        # Validate the name
        confirm_name = kwargs.get('confirm_name', None)
        if confirm_name != repo_obj.display_name:
            _logger.info("bad confirmation %r != %r", confirm_name, repo_obj.display_name)
            raise cherrypy.HTTPError(400, "bad confirmation")

        # Update the repository encoding
        _logger.info("deleting repository [%s]", repo_obj)
        repo_obj.delete()

        # Refresh repository list
        repos = self.app.currentuser.repos
        r = self.app.currentuser.get_repo(repo_obj.path)
        repos.remove(r.name)
        self.app.currentuser.repos = repos
        raise cherrypy.HTTPRedirect("/")
