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

import datetime
import logging
import os
from collections import namedtuple
from io import StringIO

from cherrypy_foundation.tools.i18n import ugettext as _
from jinja2.filters import do_mark_safe

from rdiffweb.core import librdiff

# Define the logger
logger = logging.getLogger(__name__)

_ParentEntry = namedtuple("_ParentEntry", 'path,display_name')

# TODO All function here should be move elsewhere.


def attrib(**kwargs):
    """Generate an attribute list from the keyword argument."""

    def _escape(text):
        if isinstance(text, bytes):
            text = text.decode('ascii', 'replace')
        text = str(text)
        if "&" in text:
            text = text.replace("&", "&amp;")
        if "<" in text:
            text = text.replace("<", "&lt;")
        if ">" in text:
            text = text.replace(">", "&gt;")
        if "\"" in text:
            text = text.replace("\"", "&quot;")
        return text

    def _format(key, val):
        # Don't write the attribute if value is False
        if val is False:
            return
        if val is True:
            yield str(key)
            return
        if isinstance(val, list):
            val = ' '.join([_escape(v) for v in val if v])
        else:
            val = _escape(val)
        if not val:
            return
        yield '%s="%s"' % (str(key), val)

    first = True
    buf = StringIO()
    for key, val in sorted(kwargs.items()):
        for t in _format(key, val):
            if not first:
                buf.write(' ')
            first = False
            buf.write(t)
    data = buf.getvalue()
    buf.close()
    return do_mark_safe(data)


def do_format_lastupdated(value, now=None):
    """
    Used to format date as "Updated 10 minutes ago".

    Value could be a RdiffTime or an epoch as int.
    """
    if not value:
        return ""
    now = librdiff.RdiffTime(now)
    if isinstance(value, librdiff.RdiffTime):
        delta = now.epoch - value.epoch
    elif isinstance(value, datetime.datetime):
        delta = now.epoch - value.timestamp()
    else:
        delta = now.epoch - value
    delta = datetime.timedelta(seconds=delta)
    if delta.days > 365:
        return _('%d years ago') % (delta.days / 365)
    if delta.days > 60:
        return _('%d months ago') % (delta.days / 30)
    if delta.days > 7:
        return _('%d weeks ago') % (delta.days / 7)
    elif delta.days > 0:
        return _('%d days ago') % delta.days
    elif delta.seconds > 3600:
        return _('%d hours ago') % (delta.seconds / 3600)
    elif delta.seconds > 60:
        return _('%d minutes ago') % (delta.seconds / 60)
    return _('%d seconds ago') % delta.seconds


def list_parents(repo, path):
    assert isinstance(path, bytes)
    # Build the parameters
    # Build "parent directories" links
    parents = [_ParentEntry(b'', repo.display_name)]
    parent_path_b = b''
    for part_b in path.split(b'/'):
        if part_b:
            parent_path_b = os.path.join(parent_path_b, part_b)
            display_name = repo._decode(librdiff.unquote(part_b))
            parents.append(_ParentEntry(parent_path_b, display_name))
    return parents
