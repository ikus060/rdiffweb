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

from urllib.parse import quote, unquote


# TODO: Move this into page_main
def quote_url(url, safe='/'):
    """
    Receive either str or bytes. Always return str.
    """
    # If URL is None, return None
    if not url:
        return ''
    # Convert everything to bytes
    if not isinstance(url, bytes):
        url = url.encode(encoding='latin1')
    if not isinstance(safe, bytes):
        safe = safe.encode(encoding='latin1')

    # URL encode
    val = quote(url, safe)
    if isinstance(val, bytes):
        val = val.decode(encoding='latin1')
    return val


# TODO: Move this into page_main
def unquote_url(url):
    """
    Receive either str or bytes. Always return bytes
    """
    if not url:
        return url
    # Convert everything to str
    if isinstance(url, bytes):
        url = url.decode(encoding='latin1')
    # Unquote
    val = unquote(url)
    # Make sure to return bytes.
    if isinstance(val, str):
        val = val.encode(encoding='latin1')
    return val
