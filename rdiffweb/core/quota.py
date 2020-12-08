# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

import os
import subprocess


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

    def __init__(self, app):
        self.app = app;

    def _exec(self, cmd, userobj, value=None):
        env = {
            "RDIFFWEB_USERID": userobj.userid,
            "RDIFFWEB_USERNAME": userobj.username,
            "RDIFFWEB_USERROOT": userobj.user_root,
            "RDIFFWEB_ROLE": userobj.role,
        }
        if value is not None:
            env["RDIFFWEB_QUOTA"] = value
        return subprocess.run(cmd, env=env, shell=True, check=True, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout

    def get_disk_usage(self, userobj):
        """
        Return the user disk space.
        """
        # Fall back to disk spaces.
        # Get the value from os and store in session.
        try:
            statvfs = os.statvfs(userobj.user_root)
            return {  # @UndefinedVariable
                'avail': statvfs.f_frsize * statvfs.f_bavail,
                'used': statvfs.f_frsize * (statvfs.f_blocks - statvfs.f_bavail),
                'size': statvfs.f_frsize * statvfs.f_blocks}
        except:
            return { 'avail': 0, 'used': 0, 'size': 0}

    def get_disk_quota(self, userobj):
        """
        Return the current user's quota.
        """
        return None

    def set_disk_quota(self, userobj, value):
        """
        Sets the user's quota.
        """
        raise QuotaUnsupported()
