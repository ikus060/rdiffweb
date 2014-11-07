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

import logging
import time
import urllib

from jinja2 import Environment, PackageLoader

from . import rdw_helpers

# Load all the templates from ./templates directory
jinja_env = Environment(loader=PackageLoader(
    'rdiffweb', 'templates'), auto_reload=True, autoescape=True)

# Define the logger
logger = logging.getLogger(__name__)

def compileTemplate(templateName, **kwargs):
    """Very simple implementation to render template using jinja2.
        `templateName`
            The filename to be used as template.
        `kwargs`
            The arguments to be passed to the template.
    """
    logger.debug("compiling template [%s]" % templateName)
    template = jinja_env.get_template(templateName)
    data = template.render(kwargs)
    logger.debug("template [%s] compiled" % templateName)
    return data

def do_format_datetime(value, format='%Y-%m-%d %H:%M'):
    """Used to format an epoch into local time."""
    
    if isinstance(value, rdw_helpers.rdwTime):
        value = value.getSeconds()
    
    # TODO Try to figure out the timezone name (it's a )
    return time.strftime(format, time.localtime(value))

def do_format_filesize(value, binary=False):
    """Format the value like a 'human-readable' file size (i.e. 13 kB,
    4.1 MB, 102 Bytes, etc).  Per default decimal prefixes are used (Mega,
    Giga, etc.), if the second parameter is set to `True` the binary
    prefixes are used (Mebi, Gibi).
    """
    bytes = float(value)
    base = binary and 1024 or 1000
    prefixes = [
        (binary and 'KiB' or 'kB'),
        (binary and 'MiB' or 'MB'),
        (binary and 'GiB' or 'GB'),
        (binary and 'TiB' or 'TB'),
        (binary and 'PiB' or 'PB'),
        (binary and 'EiB' or 'EB'),
        (binary and 'ZiB' or 'ZB'),
        (binary and 'YiB' or 'YB')
    ]
    if bytes == 1:
        return '1 Byte'
    elif bytes < base:
        return '%d Bytes' % bytes
    else:
        for i, prefix in enumerate(prefixes):
            unit = base ** (i + 2)
            if bytes < unit:
                return '%.1f %s' % ((base * bytes / unit), prefix)
        return '%.1f %s' % ((base * bytes / unit), prefix)

def url_for(endpoint, **kwargs):
    """Generate an url for the given endpoint."""
    
    url = []
    url.append("/")
    url.append(endpoint)
    url.append("/")
    
    if kwargs:
        url.append("?")
        for key, value in kwargs.iteritems():
            assert key
            url.append(key if isinstance(key, unicode) else unicode(key))
            url.append("=")
            if isinstance(value, unicode):
                encoded_value = rdw_helpers.encode_url(value, u"/")
            elif value:
                encoded_value = rdw_helpers.encode_url(str(value), "/")
            else:
                encoded_value = ""
            url.append(encoded_value)
            url.append("&")
        # Remove the last "&"    
        url.pop()
    return ''.join(url)

def url_for_browse(repo, path="/", restore=False):
    if not restore:
        return url_for('browse', repo=repo, path=path)
    else:
        return url_for('browse', repo=repo, path=path, restore='T')

def url_for_restore(repo, path, date, usetar=False):
    if isinstance(date, rdw_helpers.rdwTime):
        date = date.getSeconds()
    if usetar:
        return url_for('restore', repo=repo, path=path, date=date, usetar='T')
    return url_for('restore', repo=repo, path=path, date=date)

# Register filters
jinja_env.filters['datetime'] = do_format_datetime
jinja_env.filters['filesize'] = do_format_filesize

# Register method
jinja_env.globals['url_for'] = url_for
jinja_env.globals['url_for_browse'] = url_for_browse
jinja_env.globals['url_for_restore'] = url_for_restore
