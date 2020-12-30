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

from collections import OrderedDict
import datetime
from io import StringIO
import logging

import humanfriendly
from jinja2 import Environment, PackageLoader
from jinja2.filters import do_mark_safe
from jinja2.loaders import ChoiceLoader

from rdiffweb.core import i18n
from rdiffweb.core import librdiff
from rdiffweb.core import rdw_helpers
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.store import RepoObject

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
    assert isinstance(value, librdiff.RdiffTime)
    return value.strftime(dateformat)


def do_format_lastupdated(value, now=None):
    """
    Used to format date as "Updated 10 minutes ago"
    """
    if not value:
        return ""
    assert isinstance(value, librdiff.RdiffTime)
    now = librdiff.RdiffTime(now)
    delta = now.epoch() - value.epoch()
    delta = datetime.timedelta(seconds=delta)
    if delta.days > 365:
        return _('%d years ago') % (delta.days / 365)
    if delta.days > 60:
        return _('%d months ago') % (delta.days / 30)
    if delta.days > 7:
        return _('%d weeks ago') % (delta.days / 7)
    elif delta.days > 1:
        return _('%d days ago') % delta.days
    elif delta.seconds > 3600:
        return _('%d hours ago') % (delta.seconds / 3600)
    elif delta.seconds > 60:
        return _('%d minutes ago') % (delta.seconds / 60)
    return _('%d seconds ago') % delta.seconds


def create_repo_tree(repos):
    """
    Organise the repositories into a tree.
    """
    repos = sorted(repos, key=lambda r:r.display_name)
    repo_tree = OrderedDict()
    for repo in repos:
        h = repo_tree
        key = repo.display_name.strip('/').split('/')
        for p in key[:-1]:
            if p in h and isinstance(h[p], RepoObject):
                h[p] = {'.': h[p]}
            h = h.setdefault(p, {})
        h[key[-1]] = repo
    return repo_tree


def url_for(endpoint, *args, **kwargs):
    """
    Generate a url for the given endpoint, path (*args) with parameters (**kwargs)
    """
    url = "/" + endpoint.strip("/")
    for chunk in args:
        if not chunk:
            continue
        if hasattr(chunk, 'owner') and hasattr(chunk, 'path'):
            # This is a RepoObject
            url += "/"
            url += chunk.owner
            url += "/"
            url += rdw_helpers.quote_url(chunk.path.strip(b"/"))
        elif hasattr(chunk, 'path'):
            # This is a DirEntry
            if chunk.path:
                url += "/"
                url += rdw_helpers.quote_url(chunk.path.strip(b"/"))
        elif chunk and isinstance(chunk, bytes):
            url += "/"
            url += rdw_helpers.quote_url(chunk.strip(b"/"))
        elif chunk and isinstance(chunk, str):
            url += "/"
            url += chunk.rstrip("/")
        else:
            raise ValueError('invalid positional arguments, url_for accept str, bytes or RepoPath: %r' % chunk)
    first_args = True
    # Sort the arguments to have predictable results.
    for key, value in sorted(kwargs.items()):
        url += "?" if first_args else "&"
        first_args = False
        if hasattr(value, 'epoch'):
            value = value.epoch()
        url += "%s=%s" % (key, value)
    return url


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
        self.jinja_env.filters['lastupdated'] = do_format_lastupdated
        self.jinja_env.filters['filesize'] = lambda x: humanfriendly.format_size(x, binary=True)

        # Register method
        self.jinja_env.globals['attrib'] = attrib
        self.jinja_env.globals['create_repo_tree'] = create_repo_tree
        self.jinja_env.globals['url_for'] = url_for

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
