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
from cherrypy._cperror import HTTPRedirect, HTTPError
import logging
import os
import re

from rdiffweb import rdw_spider_repos
from rdiffweb.core import RdiffError
from rdiffweb.dispatch import poppath
from rdiffweb.i18n import ugettext as _
from rdiffweb.page_main import MainPage
from rdiffweb.rdw_plugin import IPreferencesPanelProvider, ITemplateFilterPlugin


_logger = logging.getLogger(__name__)


@poppath()
class DeleteRepoPage(MainPage):

    @cherrypy.expose
    def index(self, path=b"", **kwargs):
        """
        Delete the repository.
        """
        self.assertIsInstance(path, bytes)
        _logger.debug("repo delete [%r]", path)

        # Check user permissions
        repo_obj = self.validate_user_path(path)[0]

        # Validate the name
        confirm_name = kwargs.get('confirm_name', None)
        if confirm_name != repo_obj.display_name:
            _logger.info("bad confirmation %r != %r", confirm_name, repo_obj.display_name)
            raise HTTPError(400, "bad confirmation")

        # Update the repository encoding
        _logger.info("deleting repository [%s]", repo_obj)
        repo_obj.delete()

        # Refresh repository list
        repos = self.app.currentuser.repos
        r = self.app.currentuser.get_repo(repo_obj.path)
        repos.remove(r.name)
        self.app.currentuser.repos = repos
        raise HTTPRedirect("/")


class DeleteRepoPlugin(ITemplateFilterPlugin):

    def activate(self):
        # Register new handler to delete repository.
        self.app.root.delete = DeleteRepoPage(self.app)
        # Call original
        ITemplateFilterPlugin.activate(self)

    def filter_data(self, template_name, data):
        """
        Add panel to repository settings.
        """
        if template_name == 'settings.html':
            # Append our template
            template = self.app.templates.get_template("delete_repo.html")
            data["templates_content"].append(template)
