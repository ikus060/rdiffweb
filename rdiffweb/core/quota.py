# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2020 rdiffweb contributors
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

import psutil

from rdiffweb.core.config import Option
from rdiffweb.core.store import UserObject

logger = logging.getLogger(__name__)


class QuotaException(Exception):
    """
    Raised when error occur during setting quota.
    """
    pass


class QuotaUnsupported(Exception):
    """
    Raised when the quota is not supported.
    """
    pass


class IUserQuota():
    """
    Extension point to get user quotas
    """

    def get_disk_usage(self, userobj):
        """
        Return the user disk space or file system disk space.
        """

    def get_disk_quota(self, userobj, value):
        """
        Return the current user's quota. Return None if quota is not allow for
        this user or implementation. This is used to enable or disable display
        of user's quota in web interface.
        """

    def set_disk_quota(self, userobj, value):
        """
        Sets the user's quota. Raise QuotaUnsupported if this implementation
        doesn't support setting user's quota.
        """


class DefaultUserQuota():
    """
    Default implementation of IUserQuota for quota management.
    This implementation uses default disk usage.
    """

    _set_quota_cmd = Option('QuotaSetCmd')
    _get_quota_cmd = Option('QuotaGetCmd')
    _get_usage_cmd = Option('QuotaUsedCmd')

    def __init__(self, app):
        self.app = app;

    def _exec(self, cmd, userobj, quota=None):
        env = {
            "RDIFFWEB_USERID": str(userobj.userid),
            "RDIFFWEB_USERNAME": userobj.username,
            "RDIFFWEB_USERROOT": userobj.user_root,
            "RDIFFWEB_ROLE": str(userobj.role),
        }
        if quota is not None:
            env["RDIFFWEB_QUOTA"] = str(quota)
        return subprocess.run(cmd, env=env, shell=True, check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout

    def get_disk_usage(self, userobj):
        """
        Return the user disk space. Return 0 if unknown.
        """
        assert isinstance(userobj, UserObject)
        # Fall back to disk spaces.
        if not self._get_usage_cmd:
            try:
                return psutil.disk_usage(userobj.user_root).used
            except:
                logger.warn('fail to get disk usage [%s]', userobj.username, exc_info=1)
                return 0
        # Execute a command to get disk usage
        try:
            used = self._exec(self._get_usage_cmd, userobj)
            return int(used.strip())
        except Exception:
            logger.warn('fail to get user disk usage [%s]', userobj.username, exc_info=1)
            return 0

    def get_disk_quota(self, userobj):
        """
        Get's user's disk quota.
        """
        assert isinstance(userobj, UserObject)
        # Fall back to disk spaces.
        if not self._get_quota_cmd:
            try:
                return psutil.disk_usage(userobj.user_root).total
            except:
                logger.warn('fail to get disk size [%s]', userobj.username, exc_info=1)
                return 0
        # Execute a command to get disk usage
        try:
            self._exec(self._get_quota_cmd, userobj)
        except Exception:
            logger.warn('fail to get user quota [%s]', userobj.username, exc_info=1)
            return 0

    def set_disk_quota(self, userobj, quota):
        """
        Sets the user's quota.
        """
        assert isinstance(userobj, UserObject)
        assert isinstance(quota, int), "quota should be a number: " + quota
        # Return None if quota is not enabled
        if not self._set_quota_cmd:
            raise QuotaUnsupported()
        # Always update unless quota not define
        logger.info('set user [%s] quota [%s]', userobj.username, quota)
        try:
            self._exec(self._set_quota_cmd, userobj, quota=quota)
        except subprocess.CalledProcessError as e:
            raise QuotaException(e.output)
        except Exception as e:
            logger.warn('fail to set user quota [%s]', userobj.username, exc_info=1)
            raise QuotaException(str(e))

