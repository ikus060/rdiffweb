# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

import cherrypy

from rdiffweb.core.librdiff import RdiffTime

# Define the logger
logger = logging.getLogger(__name__)


# TODO Remove the following function.
def validate(value, message=None):
    """Raise HTTP error if value is not true."""
    if not value:
        raise cherrypy.HTTPError(400, message)


def validate_int(value, min=None, max=None):
    """Returns a converter function that validates integer ranges"""
    try:
        val = int(value)
    except (ValueError, TypeError):
        raise cherrypy.HTTPError(400, f"Invalid integer: {value}")

    if min is not None and val < min:
        raise cherrypy.HTTPError(400, f"Must be >= {min}")
    if max is not None and val > max:
        raise cherrypy.HTTPError(400, f"Must be <= {max}")

    return val


def validate_date(value, allow_none=False):
    """Returns a converter function that validates date"""

    if value is None and allow_none:
        return None
    try:
        return RdiffTime(int(value))
    except ValueError:
        pass
    try:
        return RdiffTime(value)
    except ValueError:
        pass
    raise cherrypy.HTTPError(400, f"Invalid date: {value}")
