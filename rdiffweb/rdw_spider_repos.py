#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

from builtins import map
import logging
import os

from rdiffweb import librdiff


# Define the logger
logger = logging.getLogger(__name__)


def _find_repos(path, depth=3):
    # TODO Should be a configuration
    # Limit the depthness
    if depth <= 0:
        return
    try:
        direntries = os.listdir(path)
    except:
        # Ignore error.
        return
    if librdiff.RDIFF_BACKUP_DATA in direntries:
        yield path

    for entry in direntries:
        entryPath = os.path.join(path, entry)
        if os.path.isdir(entryPath) and not os.path.islink(entryPath):
            for x in _find_repos(entryPath, depth - 1):
                yield x


def find_repos_for_user(user, userdb):
    logger.debug("find repos for [%s]", user)
    user_root = userdb.get_user_root(user)
    repo_paths = list(_find_repos(user_root))

    def striproot(path):
        if not path[len(user_root):]:
            return "/"
        return path[len(user_root):]
    repo_paths = list(map(striproot, repo_paths))
    logger.debug("set user [%s] repos: %s ", user, repo_paths)
    userdb.set_repos(user, repo_paths)
