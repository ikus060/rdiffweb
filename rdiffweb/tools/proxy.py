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
"""
Proxy tools copied from cherrypy
"""
import urllib

import cherrypy


def proxy(base=None, local='X-Forwarded-Host', remote='X-Forwarded-For', scheme='X-Forwarded-Proto', debug=False):
    """Change the base URL (scheme://host[:port][/path]).
    For running a CP server behind Apache, lighttpd, or other HTTP server.
    For Apache and lighttpd, you should leave the 'local' argument at the
    default value of 'X-Forwarded-Host'. For Squid, you probably want to set
    tools.proxy.local = 'Origin'.
    If you want the new request.base to include path info (not just the host),
    you must explicitly set base to the full base path, and ALSO set 'local'
    to '', so that the X-Forwarded-Host request header (which never includes
    path info) does not override it. Regardless, the value for 'base' MUST
    NOT end in a slash.
    cherrypy.request.remote.ip (the IP address of the client) will be
    rewritten if the header specified by the 'remote' arg is valid.
    By default, 'remote' is set to 'X-Forwarded-For'. If you do not
    want to rewrite remote.ip, set the 'remote' arg to an empty string.
    """

    request = cherrypy.serving.request

    if scheme:
        s = request.headers.get(scheme, None)
        if debug:
            cherrypy.log('Testing scheme %r:%r' % (scheme, s), 'TOOLS.PROXY')
        if s == 'on' and 'ssl' in scheme.lower():
            # This handles e.g. webfaction's 'X-Forwarded-Ssl: on' header
            scheme = 'https'
        else:
            # This is for lighttpd/pound/Mongrel's 'X-Forwarded-Proto: https'
            scheme = s
    if not scheme:
        scheme = request.base[: request.base.find('://')]

    if local:
        lbase = request.headers.get(local, None)
        if debug:
            cherrypy.log('Testing local %r:%r' % (local, lbase), 'TOOLS.PROXY')
        if lbase is not None:
            base = lbase.split(',')[0]
    if not base:
        default = urllib.parse.urlparse(request.base).netloc
        base = request.headers.get('Host', default)

    if base.find('://') == -1:
        # add http:// or https:// if needed
        base = scheme + '://' + base

    request.base = base

    if remote:
        xff = request.headers.get(remote)
        if debug:
            cherrypy.log('Testing remote %r:%r' % (remote, xff), 'TOOLS.PROXY')
        if xff:
            if remote == 'X-Forwarded-For':
                # Grab the first IP in a comma-separated list. Ref #1268.
                xff = next(ip.strip() for ip in xff.split(','))
            request.remote.ip = xff


# Patch cherrypy.tools.proxy only for version < 5 or > 10
# From version 5 to 10, a bug in cherrypy is breaking creation of base url.
if 5 <= int(cherrypy.__version__.split('.')[0]) <= 10:
    cherrypy.tools.proxy = cherrypy.Tool('before_request_body', proxy, priority=30)
