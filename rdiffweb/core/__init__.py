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


class RdiffError(Exception):
    """
    Standard exception raised by Rdiffweb. The error message is usually
    displayed to the web interface. Make sure the error message is translated.
    """

    def __init__(self, message):
        assert message
        if isinstance(message, bytes):
            message = message.decode('utf-8', 'replace')
        super(RdiffError, self).__init__(message)
        self.message = message


class RdiffWarning(RdiffError):
    """
    Generic exception to be used in rdiffweb to show warning message. Those
    exception are not expected to reach the default page handler. The page
    should handler this kind of exception and show a warning message to the
    user.
    """

    pass
