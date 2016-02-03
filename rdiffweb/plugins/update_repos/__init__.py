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
When enabled, this plugin is responsible to periodically refresh
the users repositories. If a new repository is added to the home directory
of a user, it will be automatically added to his list of repository.
"""
# Define the logger

from __future__ import unicode_literals

import cherrypy
from datetime import date
import logging
import os

from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_plugin import IDeamonPlugin
from rdiffweb.rdw_spider_repos import find_repos_for_user


_logger = logging.getLogger(__name__)


class UpdateReposPlugin(IDeamonPlugin):
    """
    Plugin to refresh user repos.
    """

    @property
    def deamon_frequency(self):
        """
        Return the frequency to update user repo. Default to 15min.
        """
        value = self.app.cfg.get_config_bool("autoUpdateRepos", "15")
        if value <= 0:
            value = 15
        return value * 60

    def deamon_run(self):
        """
        Refresh the user repository
        """
        try:

            user_db = self.app.userdb
            if not user_db.supports('set_repos'):
                return

            users = user_db.list()
            for user in users:
                find_repos_for_user(user, user_db)

        except:
            _logger.exception("fail to update user repos")
