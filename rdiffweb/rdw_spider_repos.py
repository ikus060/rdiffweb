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

from __future__ import unicode_literals

import os
import librdiff
import logging
import threading

# Define the logger
logger = logging.getLogger(__name__)


# Returns pid of started process, or 0 if no process was started
def startRepoSpiderThread(killEvent, app):
    # Get refresh interval from app config.
    spiderInterval = app.config.get_config_bool("autoUpdateRepos", "False")

    # Start the thread.
    newThread = SpiderReposThread(killEvent, app, spiderInterval)
    newThread.start()


class SpiderReposThread(threading.Thread):

    def __init__(self, killEvent, app, spiderInterval=False):
        """Create a new SpiderRepo to refresh the users repositories."""
        self.killEvent = killEvent
        self.app = app
        # Make sure it's an integer.
        if spiderInterval:
            assert isinstance(spiderInterval, int)
        self.spiderInterval = spiderInterval
        threading.Thread.__init__(self)

    def run(self):
        if self.spiderInterval:
            while True:
                findReposForAllUsers(self.app)
                self.killEvent.wait(60 * self.spiderInterval)
                if self.killEvent.isSet():
                    return


def _findRdiffRepos(dirToSearch, outRepoPaths, depth=0):
    # TODO Should be a configuration
    # Limit the depthness
    if depth >= 3:
        return

    dirEntries = os.listdir(dirToSearch)
    if librdiff.RDIFF_BACKUP_DATA in dirEntries:
        outRepoPaths.append(dirToSearch)
        return

    for entry in dirEntries:
        entryPath = os.path.join(dirToSearch, entry)
        if os.path.isdir(entryPath) and not os.path.islink(entryPath):
            _findRdiffRepos(entryPath, outRepoPaths, depth + 1)


def findReposForUser(user, userDBModule):
    logger.debug("find repos for [%s]" % user)
    userRoot = userDBModule.get_root_dir(user)
    repoPaths = []
    _findRdiffRepos(userRoot, repoPaths)

    def stripRoot(path):
        if not path[len(userRoot):]:
            return "/"
        return path[len(userRoot):]
    repoPaths = map(stripRoot, repoPaths)
    userDBModule.set_repos(user, repoPaths)


def findReposForAllUsers(app):
    """Refresh all users repositories using the given `app`."""
    user_db = app.userdb
    if not user_db.is_modifiable():
        return

    users = user_db.list()
    for user in users:
        findReposForUser(user, user_db)
