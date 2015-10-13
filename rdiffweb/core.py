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

from rdiffweb.i18n import ugettext as _


class RdiffError(Exception):
    """
    Standard exception raised by Rdiffweb.
    """

    def __init__(self, message):
        assert isinstance(message, unicode)
        super(RdiffError, self).__init__(message)
        self.message = message


class InvalidUserError(Exception):
    """
    Raised when calling a method with an invalid username.
    """

    def __init__(self, user):
        super(InvalidUserError, self).__init__(_("user %s doesn't exists" % (user,)))


class Component():

    def __init__(self, app):
        assert app
        self.app = app
