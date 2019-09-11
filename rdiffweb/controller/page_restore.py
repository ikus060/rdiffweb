#!/usr/bin/python
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

from __future__ import absolute_import
from __future__ import unicode_literals

import logging
from rdiffweb.controller import Controller, validate_isinstance, validate
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.archiver import ARCHIVERS
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.rdw_helpers import quote_url

from builtins import bytes
from builtins import str
import cherrypy
from cherrypy.lib.static import _serve_fileobj, mimetypes

# Define the logger
logger = logging.getLogger(__name__)


def _content_disposition(filename):
    """
    Try to generate the best content-disposition value to support most browser.
    """
    assert isinstance(filename, str)
    # Provide hint filename. Try to follow recommendation at
    # http://greenbytes.de/tech/tc2231/
    # I choose to only provide filename if the filename is a simple ascii
    # file without special character. Otherwise, we provide filename*

    # 1. Used quoted filename for ascii filename.
    try:
        filename.encode('ascii')
        # Some char are not decoded properly by user agent.
        if not any(c in filename for c in [';', '%', '\\']):
            return 'attachment; filename="%s"' % filename
    except:
        pass
    # 3. Define filename* as encoded UTF8 (replace invalid char)
    filename_utf8 = filename.encode('utf-8', 'replace')
    return 'attachment; filename*=UTF-8\'\'%s' % quote_url(filename_utf8, safe='?')


def _content_type(filename):
    """
    Using filename, try to guess the content-type.
    """
    ext = ''
    i = filename.rfind('.')
    if i != -1:
        ext = filename[i:].lower()
    return mimetypes.types_map.get(ext, "application/octet-stream")  # @UndefinedVariable


@poppath()
class RestorePage(Controller):
    _cp_config = {"response.stream": True, "response.timeout": 3000}

    @cherrypy.expose
    @cherrypy.tools.gzip(on=False)
    def default(self, path=b"", date=None, kind=None, usetar=None):
        validate_isinstance(path, bytes)
        validate_isinstance(date, str)
        validate(kind is None or kind in ARCHIVERS)
        validate(usetar is None or isinstance(usetar, str))

        logger.debug("restoring [%r][%s]", path, date)

        # Check user access to repo / path.
        path_obj = self.app.currentuser.get_repo_path(path)[1]

        # Get the restore date
        try:
            RdiffTime(int(date))
        except:
            logger.warning("invalid date %s", date)
            raise cherrypy.HTTPError(400, _("Invalid date."))

        # Get if backup in progress
        # status = repo_obj.status
        # if status[0] != 'ok':
        #    raise cherrypy.HTTPError(500, _(status[1] + ' ' + _("""Restores are disabled.""")))

        # Determine the kind.
        kind = kind or 'zip'
        if usetar is not None:
            kind = 'tar.gz'

        # Restore file(s)
        filename, fileobj = path_obj.restore(int(date), kind=kind)

        # Define content-disposition.
        cherrypy.response.headers["Content-Disposition"] = _content_disposition(filename)

        # Set content-type based on filename extension
        content_type = _content_type(filename)
        cherrypy.response.headers['Content-Type'] = content_type

        # Stream the data.
        # Make use of _serve_fileobj() because the fsstat() function on a pipe
        # return a size of 0 for Content-Length. This behavior brake all the flow.
        return _serve_fileobj(fileobj, content_type=content_type, content_length=None)
