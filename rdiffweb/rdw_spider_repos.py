#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffweb contributors
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

import os
import db
import librdiff
import logging
import rdw_config
import threading

# Define the logger
logger = logging.getLogger(__name__)


# Returns pid of started process, or 0 if no process was started
def startRepoSpiderThread(killEvent):
    newThread = spiderReposThread(killEvent)
    newThread.start()


class spiderReposThread(threading.Thread):

    def __init__(self, killEvent):
        self.killEvent = killEvent
        threading.Thread.__init__(self)

    def run(self):
        spiderInterval = rdw_config.get_config("autoUpdateRepos")
        if spiderInterval:
            spiderInterval = int(spiderInterval)
            while True:
                findReposForAllUsers()
                self.killEvent.wait(60 * spiderInterval)
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


def findReposForAllUsers():
    userDBModule = db.userDB().getUserDBModule()
    if not userDBModule.is_modifiable():
        return

    users = userDBModule.list()
    for user in users:
        findReposForUser(user, userDBModule)
