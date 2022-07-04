# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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
'''
Created on Sep. 29, 2020

@author: Patrik Dufresne
'''

import logging
import subprocess

import cherrypy
import psutil
from cherrypy.process.plugins import SimplePlugin

from rdiffweb.core.model import UserObject

logger = logging.getLogger(__name__)


class QuotaPlugin(SimplePlugin):
    """
    Default implementation of user quota for quota management.
    This implementation uses default disk usage.
    """

    set_quota_cmd = None
    get_quota_cmd = None
    get_usage_cmd = None

    def start(self):
        self.bus.log('Start Quota plugin')
        if self.set_quota_cmd:
            self.bus.subscribe("set_disk_quota", self.set_quota)
        self.bus.subscribe("get_disk_quota", self.get_quota)
        self.bus.subscribe("get_disk_usage", self.get_usage)

    def stop(self):
        self.bus.log('Stop Quota plugin')
        self.bus.unsubscribe("set_disk_quota", self.set_quota)
        self.bus.unsubscribe("get_disk_quota", self.get_quota)
        self.bus.unsubscribe("get_disk_usage", self.get_usage)

    def _exec(self, cmd, userobj, quota=None):
        env = {
            "RDIFFWEB_USERID": str(userobj.userid),
            "RDIFFWEB_USERNAME": userobj.username,
            "RDIFFWEB_USERROOT": userobj.user_root,
            "RDIFFWEB_ROLE": str(userobj.role),
        }
        if quota is not None:
            env["RDIFFWEB_QUOTA"] = str(quota)
        return subprocess.run(
            cmd,
            env=env,
            shell=True,
            check=True,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ).stdout

    def get_usage(self, userobj: UserObject):
        # Fall back to disk spaces.
        if not self.get_usage_cmd:
            try:
                return psutil.disk_usage(userobj.user_root).used
            except Exception:
                logger.warning('fail to get disk usage [%s]', userobj.username, exc_info=1)
                return 0
        # Execute a command to get disk usage
        try:
            used = self._exec(self.get_usage_cmd, userobj)
            return int(used.strip())
        except Exception:
            logger.warning('fail to get user disk usage [%s]', userobj.username, exc_info=1)
            return 0

    def get_quota(self, userobj: UserObject):
        # Fall back to disk spaces.
        if not self.get_quota_cmd:
            try:
                return psutil.disk_usage(userobj.user_root).total
            except Exception:
                logger.warning('fail to get disk size [%s]', userobj.username, exc_info=1)
                return 0
        # Execute a command to get disk usage
        try:
            total = self._exec(self.get_quota_cmd, userobj)
            return int(total.strip())
        except Exception:
            logger.warning('fail to get user quota [%s]', userobj.username, exc_info=1)
            return 0

    def set_quota(self, userobj: UserObject, quota: int):
        # Return False if quota is not enabled
        if not self.set_quota_cmd:
            return False
        # Always update unless quota not define
        logger.info('set user [%s] quota [%s]', userobj.username, quota)
        try:
            self._exec(self.set_quota_cmd, userobj, quota=quota)
            return quota
        except Exception:
            logger.warning('fail to set user quota [%s]', userobj.username, exc_info=1)
            return False


cherrypy.quota = QuotaPlugin(cherrypy.engine)
cherrypy.quota.subscribe()

cherrypy.config.namespaces['quota'] = lambda key, value: setattr(cherrypy.quota, key, value)
