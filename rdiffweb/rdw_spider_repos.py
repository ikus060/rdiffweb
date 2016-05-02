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

# Define the logger
logger = logging.getLogger(__name__)


RDIFF_BACKUP_DATA = "rdiff-backup-data"


def _find_repos(path, depth=3):
    # TODO Should be a configuration
    # Limit the depthness
    if depth <= 0:
        return
    if not os.path.isdir(path) or os.path.islink(path):
        return
    try:
        direntries = os.listdir(path)
    except:
        # Ignore error.
        return
    if RDIFF_BACKUP_DATA in direntries:
        yield path
    else:
        for entry in direntries:
            try:
                for x in _find_repos(os.path.join(path, entry), depth - 1):
                    yield x
            except UnicodeDecodeError:
                # Invalid encoding for root dir is not supported.
                logger.warning('skip invalid directory name %r/%r', path, entry)


def find_repos_for_user(user, userdb):
    logger.debug("find repos for [%s]", user)
    user_root = userdb.get_user(user).user_root
    repo_paths = list(_find_repos(user_root))

    def striproot(path):
        if not path[len(user_root):]:
            return "/"
        return path[len(user_root):]
    repo_paths = list(map(striproot, repo_paths))
    logger.debug("set user [%s] repos: %s ", user, repo_paths)
    userdb.get_user(user).repos = repo_paths
