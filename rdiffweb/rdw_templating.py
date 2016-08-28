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

from __future__ import absolute_import
from __future__ import unicode_literals

from builtins import bytes
from builtins import object
from builtins import str
from io import StringIO
from jinja2 import Environment, PackageLoader
from jinja2.ext import _make_new_gettext, _make_new_ngettext
from jinja2.loaders import ChoiceLoader, FileSystemLoader
import logging
import time

from rdiffweb import i18n
from rdiffweb import rdw_helpers
from jinja2.filters import do_mark_safe


# Define the logger
logger = logging.getLogger(__name__)


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
        if not val:
            return
        if val is True:
            yield str(key)
            return
        if isinstance(val, list):
            val = ' '.join([_escape(v) for v in val if v])
        elif val:
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


def do_filter(sequence, attribute_name):
    """Filter sequence of objects."""
    return [x for x in sequence
            if (isinstance(x, dict) and
                attribute_name in x and
                x[attribute_name]) or
               (hasattr(x, attribute_name) and
                getattr(x, attribute_name))]


def do_format_datetime(value, dateformat='%Y-%m-%d %H:%M'):
    """Used to format an epoch into local time."""

    if not value:
        return ""

    if isinstance(value, rdw_helpers.rdwTime):
        value = value.getSeconds()

    # TODO Try to figure out the time zone name (it's a )
    return time.strftime(dateformat, time.localtime(value))


def do_format_filesize(value, binary=True):
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


def url_for_browse(repo, path=None, restore=False):
    """Generate an URL for browse controller."""
    # Make sure the URL end with a "/" otherwise cherrypy does an internal
    # redirection.
    assert isinstance(repo, bytes)
    assert isinstance(path, bytes) or not path
    if not path:
        path = b''
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
    assert isinstance(repo, bytes)
    url = []
    url.append("/history/")
    if repo:
        repo = repo.rstrip(b"/")
        url.append(rdw_helpers.quote_url(repo))
        url.append("/")
    return ''.join(url)


def url_for_restore(repo, path, date, kind=None):
    assert isinstance(repo, bytes)
    assert isinstance(path, bytes)
    assert isinstance(date, rdw_helpers.rdwTime)
    url = []
    url.append("/restore/")
    if repo:
        repo = repo.rstrip(b"/")
        url.append(rdw_helpers.quote_url(repo))
    if len(path) > 0:
        url.append("/")
        path = path.rstrip(b"/")
        url.append(rdw_helpers.quote_url(path))
    # Append date
    url.append("?date=")
    url.append(str(date.getSeconds()))
    if kind:
        url.append("&kind=%s" % kind)
    return ''.join(url)


def url_for_settings(repo):
    url = []
    url.append("/settings/")
    if repo:
        repo = repo.rstrip(b"/")
        url.append(rdw_helpers.quote_url(repo))
        url.append("/")
    return ''.join(url)


def url_for_status_entry(date, repo=None):
    assert isinstance(date, rdw_helpers.rdwTime)
    url = []
    url.append("/status/entry/")
    if repo:
        assert isinstance(repo, bytes)
        repo = repo.rstrip(b"/")
        url.append(rdw_helpers.quote_url(repo))
        url.append("/")
    if date:
        url.append("?date=")
        url.append(str(date.getSeconds()))
    return ''.join(url)


def _get_translation(domain):
    """
    Used in templates to load a different translation domain.
    """
    t = i18n.get_translation(domain)
    t.ugettext = _make_new_gettext(t.ugettext)
    t.ungettext = _make_new_ngettext(t.ungettext)
    return t


class TemplateManager(object):
    """
    Uses to generate HTML page from template using Jinja2 templating.
    """

    def __init__(self):

        loader = ChoiceLoader([
            PackageLoader('rdiffweb', 'templates')
        ])

        # Load all the templates from /templates directory
        self.jinja_env = Environment(
            loader=loader,
            auto_reload=True,
            autoescape=True,
            extensions=[
                'jinja2.ext.i18n',
                'jinja2.ext.with_',
                'jinja2.ext.autoescape',
            ])

        # Register filters
        self.jinja_env.filters['filter'] = do_filter
        self.jinja_env.filters['datetime'] = do_format_datetime
        self.jinja_env.filters['filesize'] = do_format_filesize

        # Register method
        self.jinja_env.globals['attrib'] = attrib
        self.jinja_env.globals['url_for_browse'] = url_for_browse
        self.jinja_env.globals['url_for_history'] = url_for_history
        self.jinja_env.globals['url_for_restore'] = url_for_restore
        self.jinja_env.globals['url_for_settings'] = url_for_settings
        self.jinja_env.globals['url_for_status_entry'] = url_for_status_entry
        self.jinja_env.globals['load_translation'] = _get_translation
        self.jinja_env.globals['get_translation'] = _get_translation

    def add_templatesdir(self, templates_dir):
        """
        Add a new templates directory.
        """
        # Add a new template location to the list of loaders.
        loaders = self.jinja_env.loader.loaders
        loaders.append(FileSystemLoader(templates_dir))

    def compile_template(self, template_name, **kwargs):
        """Very simple implementation to render template using jinja2.
            `templateName`
                The filename to be used as template.
            `kwargs`
                The arguments to be passed to the template.
        """
        logger.log(1, "compiling template [%s]", template_name)
        self.jinja_env.install_gettext_callables(
            i18n.ugettext, i18n.ungettext, newstyle=True)
        template = self.jinja_env.get_template(template_name)
        data = template.render(kwargs)
        logger.log(1, "template [%s] compiled", template_name)
        return data

    def get_template(self, template_name):
        """
        Return a reference to the given template identify by `template_name`.
        This method is commonly used by plugins. If the `template_name` is not
        found an error is raised.
        """
        # Simply use the jinja env to return reference to template.
        return self.jinja_env.get_template(template_name)
