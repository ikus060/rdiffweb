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

import cherrypy
import humanfriendly
import jinja2
from jinja2 import Environment, PackageLoader
from jinja2.filters import do_mark_safe
from jinja2.loaders import ChoiceLoader

from rdiffweb.core import librdiff, rdw_helpers
from rdiffweb.tools import i18n
from rdiffweb.tools.i18n import ugettext as _

# Define the logger
logger = logging.getLogger(__name__)

_ParentEntry = namedtuple("_ParentEntry", 'path,display_name')


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
    return [
        x
        for x in sequence
        if (isinstance(x, dict) and attribute_name in x and x[attribute_name])
        or (hasattr(x, attribute_name) and getattr(x, attribute_name))
    ]


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


def url_for(*args, relative=None, **kwargs):
    """
    Generate a url for the given endpoint, path (*args) with parameters (**kwargs)

    This could be used to generate a path with userobject and repo object

    If `relative` is None or not provided, default to absolute
    path. If False, the output will be an absolute URL (including
    the scheme, host, vhost, and script_name). If True, the output
    will instead be a URL that is relative to the
    current request path, perhaps including '..' atoms. If relative is
    the string 'server', the output will instead be a URL that is
    relative to the server root; i.e., it will start with a slash.
    """
    path = ""
    for chunk in args:
        if chunk is None:
            continue
        if hasattr(chunk, 'owner') and hasattr(chunk, 'repopath'):
            # This is a RepoObject
            path += "/"
            path += chunk.owner
            path += "/"
            path += rdw_helpers.quote_url(chunk.repopath.strip("/"))
        elif hasattr(chunk, 'path'):
            # This is a DirEntry
            if chunk.path:
                path += "/"
                path += rdw_helpers.quote_url(chunk.path.strip(b"/"))
        elif isinstance(chunk, bytes):
            path += "/"
            path += rdw_helpers.quote_url(chunk.strip(b"/"))
        elif isinstance(chunk, str):
            if not chunk.startswith('.'):
                path += "/"
            path += chunk.lstrip("/")
        else:
            raise ValueError('invalid positional arguments, url_for accept str, bytes or RepoPath: %r' % chunk)
    # Sort the arguments to have predictable results.
    qs = [(k, v.epoch if hasattr(v, 'epoch') else v) for k, v in sorted(kwargs.items()) if v is not None]
    # Outside a request, use the external_url as base if defined
    base = None
    if not cherrypy.request.app and cherrypy.tree.apps:
        app = cherrypy.tree.apps['']
        base = app.cfg.external_url
    return cherrypy.url(path=path, qs=qs, relative=relative, base=base)


class TemplateManager(object):
    """
    Uses to generate HTML page from template using Jinja2 templating.
    """

    def __init__(self):
        # Load all the templates from /templates directory
        loader = ChoiceLoader([PackageLoader('rdiffweb', 'templates')])

        # With and autoescape are included by dfault in Jinja2>=3
        extensions = ['jinja2.ext.i18n']
        if jinja2.__version__[0] <= '2':
            extensions.extend(['jinja2.ext.with_', 'jinja2.ext.autoescape'])
        self.jinja_env = Environment(
            loader=loader,
            auto_reload=True,
            autoescape=True,
            extensions=extensions,
        )

        # Register filters
        self.jinja_env.filters['filter'] = do_filter
        self.jinja_env.filters['lastupdated'] = do_format_lastupdated
        self.jinja_env.filters['filesize'] = lambda x: humanfriendly.format_size(x, binary=True)
        self.jinja_env.filters['timespan'] = lambda x: humanfriendly.format_timespan(x, max_units=1)
        self.jinja_env.filters['format_datetime'] = i18n.format_datetime
        self.jinja_env.filters['format_date'] = i18n.format_date

        # Register method
        self.jinja_env.globals['attrib'] = attrib
        self.jinja_env.globals['list_parents'] = list_parents
        self.jinja_env.globals['url_for'] = url_for

    def compile_template(self, template_name, **kwargs):
        """Very simple implementation to render template using jinja2.
        `templateName`
            The filename to be used as template.
        `kwargs`
            The arguments to be passed to the template.
        """
        logger.log(1, "compiling template [%s]", template_name)
        self.jinja_env.install_gettext_callables(i18n.ugettext, i18n.ungettext, newstyle=True)
        template = self.jinja_env.get_template(template_name)
        data = template.render(kwargs)
        logger.log(1, "template [%s] compiled", template_name)
        return data
