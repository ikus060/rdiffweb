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

import logging

import cherrypy
import rdiffweb.tools.errors  # noqa: cherrypy.tools.errors
from cherrypy.lib.static import _serve_fileobj, mimetypes
from rdiffweb.controller import (Controller, validate, validate_date,
                                 validate_isinstance)
from rdiffweb.controller.dispatch import poppath
from rdiffweb.core.librdiff import (AccessDeniedError, DoesNotExistError,
                                    SymLinkAccessDeniedError)
from rdiffweb.core.rdw_helpers import quote_url
from rdiffweb.core.restore import ARCHIVERS

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
    except Exception:
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
    @cherrypy.tools.errors(error_table={
        DoesNotExistError: 404,
        AccessDeniedError: 403,
        SymLinkAccessDeniedError: 403,
    })
    def default(self, path=b"", date=None, kind=None, usetar=None):
        validate_isinstance(path, bytes)
        validate(kind is None or kind in ARCHIVERS)
        validate(usetar is None or isinstance(usetar, str))
        date = validate_date(date)

        # Check user access to repo / path.
        path_obj = self.app.store.get_repo_path(path)[1]

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
