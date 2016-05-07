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
import logging
import os
import re

from rdiffweb import rdw_spider_repos, page_main
from rdiffweb.core import RdiffError
from rdiffweb.dispatch import poppath
from rdiffweb.i18n import ugettext as _
from rdiffweb.page_main import MainPage
from rdiffweb.rdw_plugin import IPreferencesPanelProvider, ITemplateFilterPlugin


_logger = logging.getLogger(__name__)


@poppath()
class RemoveOlderPage(page_main.MainPage):

    @cherrypy.expose()
    def index(self, path, keepdays):
        assert isinstance(path, bytes)
        assert keepdays
        _logger.debug("repo settings [%r]", path)

        # Get new value
        try:
            keepdays = int(keepdays)
        except:
            _logger.warning("invalid keepdays value %r", keepdays)
            raise cherrypy.HTTPError(400, _("Invalid value"))

        # Check user permissions
        repo_obj = self.validate_user_path(path)[0]

        # Get repository object from user database.
        r = self.app.currentuser.repo_dict[repo_obj.path]

        # Update the database.
        r.set_attr('keepdays', keepdays)

        return _("Updated")


class RemoveOlderPlugin(ITemplateFilterPlugin):

    def activate(self):
        # Add page
        self.app.root.remove_older = RemoveOlderPage(self.app)
        # Call original
        ITemplateFilterPlugin.activate(self)

    def filter_data(self, template_name, data):
        """
        Add panel to repository settings.
        """
        if template_name == 'settings.html':
            # Append our template
            template = self.app.templates.get_template("remove_older.html")
            data["templates_content"].append(template)
            # Query current data from database.
            r = self.app.currentuser.repo_dict[data['repo_path']]
            data["keepdays"] = int(r.get_attr('keepdays', default='-1'))
