#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 rdiffweb contributors
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

import logging
import time

from jinja2 import Environment, PackageLoader

import rdw_helpers
from i18n import ugettext, ungettext

# Load all the templates from /templates directory
jinja_env = Environment(loader=PackageLoader('rdiffweb', 'templates'),
                        auto_reload=True,
                        autoescape=True,
                        extensions=['jinja2.ext.i18n'])

# Define the logger
logger = logging.getLogger(__name__)


def compile_template(templateName, **kwargs):
    """Very simple implementation to render template using jinja2.
        `templateName`
            The filename to be used as template.
        `kwargs`
            The arguments to be passed to the template.
    """
    logger.debug("compiling template [%s]" % templateName)
    jinja_env.install_gettext_callables(ugettext, ungettext, newstyle=True)
    template = jinja_env.get_template(templateName)
    data = template.render(kwargs)
    logger.debug("template [%s] compiled" % templateName)
    return data


def do_filter(sequence, attribute_name):
    """Filter sequence of objects."""
    return filter(lambda x:
                  (isinstance(x, dict) and attribute_name in x
                   and x[attribute_name]) or
                  (hasattr(x, attribute_name) and getattr(x, attribute_name)),
                  sequence)


def do_format_datetime(value, dateformat='%Y-%m-%d %H:%M'):
    """Used to format an epoch into local time."""

    if not value:
        return ""

    if isinstance(value, rdw_helpers.rdwTime):
        value = value.getSeconds()

    # TODO Try to figure out the time zone name (it's a )
    return time.strftime(dateformat, time.localtime(value))


def do_format_filesize(value, binary=False):
    """Format the value like a 'human-readable' file size (i.e. 13 kB,
    4.1 MB, 102 Bytes, etc).  Per default decimal prefixes are used (Mega,
    Giga, etc.), if the second parameter is set to `True` the binary
    prefixes are used (Mebi, Gibi).
    """
    size = float(value)
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
    if size == 1:
        return '1 Byte'
    elif size < base:
        return '%d Bytes' % size
    else:
        for i, prefix in enumerate(prefixes):
            unit = base ** (i + 2)
            if size < unit:
                return '%.1f %s' % ((base * size / unit), prefix)
        return '%.1f %s' % ((base * size / unit), prefix)


def url_for_browse(repo, path=b"", restore=False):
    """Generate an URL for browse controller."""
    # Make sure the URL end with a "/" otherwise cherrypy does an internal
    # redirection.
    assert isinstance(repo, str)
    assert isinstance(path, str)
    url = []
    url.append("/browse/")
    if repo:
        repo = repo.rstrip(b"/")
        url.append(rdw_helpers.quote_url(repo))
        url.append("/")
    if len(path) > 0:
        path = path.rstrip(b"/")
        url.append(rdw_helpers.quote_url(path))
        url.append("/")
    if restore:
        url.append("?")
        url.append("restore=T")
    return ''.join(url)


def url_for_history(repo):
    url = []
    url.append("/history/")
    if repo:
        repo = repo.rstrip(b"/")
        url.append(rdw_helpers.quote_url(repo))
        url.append("/")
    return ''.join(url)


def url_for_restore(repo, path, date, usetar=False):
    assert isinstance(repo, str)
    assert isinstance(path, str)
    assert isinstance(date, rdw_helpers.rdwTime)
    url = []
    url.append("/restore/")
    if repo:
        repo = repo.rstrip(b"/")
        url.append(rdw_helpers.quote_url(repo))
        url.append("/")
    if len(path) > 0:
        path = path.rstrip(b"/")
        url.append(rdw_helpers.quote_url(path))
        url.append("/")
    # Append date
    url.append("?date=")
    url.append(str(date.getSeconds()))
    if usetar:
        url.append("&usetar=T")
    return ''.join(url)


def url_for_status_entry(date, repo=None):
    assert isinstance(date, rdw_helpers.rdwTime)
    url = []
    url.append("/status/entry/")
    if repo:
        assert isinstance(repo, str)
        repo = repo.rstrip(b"/")
        url.append(rdw_helpers.quote_url(repo))
        url.append("/")
    if date:
        url.append("?date=")
        url.append(str(date.getSeconds()))
    return ''.join(url)

# Register filters
jinja_env.filters['filter'] = do_filter
jinja_env.filters['datetime'] = do_format_datetime
jinja_env.filters['filesize'] = do_format_filesize

# Register method
jinja_env.globals['url_for_browse'] = url_for_browse
jinja_env.globals['url_for_history'] = url_for_history
jinja_env.globals['url_for_restore'] = url_for_restore
jinja_env.globals['url_for_status_entry'] = url_for_status_entry
