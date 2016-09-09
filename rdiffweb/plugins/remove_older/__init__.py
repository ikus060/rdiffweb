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
import logging
import os
import re

from rdiffweb import rdw_spider_repos, page_main, librdiff
from rdiffweb.dispatch import poppath
from rdiffweb.i18n import ugettext as _
from rdiffweb.page_main import MainPage
from rdiffweb.rdw_helpers import rdwTime
from rdiffweb.rdw_plugin import IPreferencesPanelProvider, ITemplateFilterPlugin, \
    IDeamonPlugin, JobPlugin


_logger = logging.getLogger(__name__)

KEEPDAYS = 'keepdays'


@poppath()
class RemoveOlderPage(page_main.MainPage):

    @cherrypy.expose()
    def index(self, path=b"", keepdays=None):
        self.assertIsInstance(path, bytes)
        self.assertTrue(keepdays)
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
        r = self.app.currentuser.get_repo(repo_obj.path)

        # Update the database.
        r.set_attr(KEEPDAYS, keepdays)

        return _("Updated")


class RemoveOlderPlugin(ITemplateFilterPlugin, JobPlugin):

    def activate(self):
        # Add page
        self.app.root.ajax.remove_older = RemoveOlderPage(self.app)
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
            r = self.app.currentuser.get_repo(data['repo_path'])
            data["keepdays"] = int(r.get_attr(KEEPDAYS, default='-1'))

    @property
    def job_execution_time(self):
        return self.app.cfg.get_config('RemoveOlderTime', '23:00')

    def job_run(self):
        """
        Execute the job in background.
        """
        # Create a generator to loop on repositories.
        gen = (
            (user, repo, repo.get_attr(KEEPDAYS, default='-1'))
            for user in self.app.userdb.list()
            for repo in user.repo_list)
        # Filter them.
        gen = (
            (user, repo, keepdays)
            for user, repo, keepdays in gen
            if keepdays > 0)

        # Loop on each repos.
        for user, repo, keepdays in gen:
            try:
                self._remove_older(user, repo, keepdays)
            except:
                _logger.exception("fail to remove older for user [%r] repo [%r]", user, repo)

    def _remove_older(self, user, repo, keepdays):
        """
        Take action to remove older.
        """
        assert keepdays > 0
        # Get instance of the repo.
        r = librdiff.RdiffRepo(user.user_root, repo.name)
        # Check history date.
        if not r.last_backup_date:
            _logger.info("no backup dates for [%r]", r.repo_root)
            return
        d = rdwTime() - r.last_backup_date
        d = d.days + keepdays

        _logger.info("execute rdiff-backup --force --remove-older-than=%sD %r", d, r.repo_root)
        r.execute(b'--force',
                  b'--remove-older-than=' + str(d).encode(encoding='latin1') + b'D',
                  r.repo_root)
