#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffWeb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffWeb contributors
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

import time
from jinja2 import Environment, PackageLoader

# Load all the templates from ./templates directory
jinja_env = Environment(loader=PackageLoader('rdiffWeb', 'templates'), auto_reload=True, autoescape=True)

def compileTemplate(templateName, **kwargs):
   """Very simple implementation to render template using jinja2.
      `templateName`
         The filename to be used as template.
      `kwargs`
         The arguments to be passed to the template.
   """
   template = jinja_env.get_template(templateName)
   return template.render(kwargs)

def do_format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
   """Used to format date time"""
   return time.strftime(format, time.gmtime(value))

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

# Register filters
jinja_env.filters['datetime'] = do_format_datetime
jinja_env.filters['filesize'] = do_format_filesize
