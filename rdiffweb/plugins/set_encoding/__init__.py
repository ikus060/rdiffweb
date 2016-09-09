#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 Patrik Dufresne Service Logiciel
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
Plugin to allow user to delete their own repository from repository settings.
"""
# Define the logger

from __future__ import unicode_literals

from builtins import str
import cherrypy
from cherrypy._cperror import HTTPRedirect
import datetime
import encodings
import logging
import os
import re

from rdiffweb import rdw_spider_repos, page_main, librdiff
from rdiffweb.dispatch import poppath
from rdiffweb.i18n import ugettext as _
from rdiffweb.page_main import MainPage
from rdiffweb.rdw_helpers import rdwTime
from rdiffweb.rdw_plugin import IPreferencesPanelProvider, ITemplateFilterPlugin, \
    IDeamonPlugin


_logger = logging.getLogger(__name__)

KEEPDAYS = 'keepdays'


@poppath()
class SetEncodingPage(page_main.MainPage):

    @cherrypy.expose()
    def index(self, path=b'', new_encoding=None):
        """
        Update repository encoding via Ajax.
        """
        self.assertIsInstance(path, bytes)
        self.assertTrue(new_encoding)

        _logger.debug("update repo [%r] settings [%r]", path, new_encoding)

        # Check user permissions
        repo_obj = self.validate_user_path(path)[0]

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


class SetEncodingPlugin(ITemplateFilterPlugin):

    def activate(self):
        # Add page
        self.app.root.ajax.set_encoding = SetEncodingPage(self.app)
        # Call original
        ITemplateFilterPlugin.activate(self)

    def filter_data(self, template_name, data):
        """
        Add panel to repository settings.
        """
        if template_name == 'settings.html':
            # Append our template
            template = self.app.templates.get_template("set_encoding.html")
            data["templates_content"].append(template)
            # Query current data from database.
            repo_obj = librdiff.RdiffRepo(self.app.currentuser.user_root, data['repo_path'])
            current_encoding = repo_obj.get_encoding()
            current_encoding = encodings.normalize_encoding(current_encoding)
            data['current_encoding'] = current_encoding
