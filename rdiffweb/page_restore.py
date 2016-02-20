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
from builtins import str
import cherrypy
from cherrypy.lib.static import _serve_fileobj
import logging
import os

from rdiffweb import librdiff
from rdiffweb import page_main
from rdiffweb import rdw_helpers
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_helpers import unquote_url, quote_url


# Define the logger
logger = logging.getLogger(__name__)


class RestorePage(page_main.MainPage):
    _cp_config = {"response.stream": True, "response.timeout": 3000}

    def _cp_dispatch(self, vpath):
        """Used to handle permalink URL.
        ref http://cherrypy.readthedocs.org/en/latest/advanced.html"""
        # Notice vpath contains bytes.
        if len(vpath) > 0:
            # /the/full/path/
            path = []
            while len(vpath) > 0:
                path.append(unquote_url(vpath.pop(0)))
            cherrypy.request.params['path'] = b"/".join(path)
            return self

        return vpath

    @cherrypy.expose
    @cherrypy.tools.gzip(on=False)
    def index(self, path=b"", date="", usetar=""):
        assert isinstance(path, bytes)
        assert isinstance(date, str)
        assert isinstance(usetar, str)

        logger.debug("restoring [%r][%s]", path, date)

        # The path wont have leading and trailing "/".
        (path, file_b) = os.path.split(path)
        if not path:
            path = file_b
            file_b = b""

        # Check user access to repo / path.
        try:
            (repo_obj, path_obj) = self.validate_user_path(path)
        except librdiff.FileError as e:
            logger.exception("invalid user path")
            return self._compile_error_template(str(e))

        # Get the restore date
        try:
            restore_date = rdw_helpers.rdwTime()
            restore_date.initFromInt(int(date))
        except:
            logger.warning("invalid date %s", date)
            return self._compile_error_template(_("Invalid date."))

        # Get if backup in progress
        if repo_obj.in_progress:
            return self._compile_error_template(_("""A backup is currently in progress to this repository. Restores are disabled until this backup is complete."""))

        # Determine the kind.
        kind = 'zip'
        if usetar:
            kind = 'tar.gz'

        # Restore file(s)
        try:
            filename, fileobj = path_obj.restore(file_b, int(date), kind=kind)
        except librdiff.FileError as e:
            logger.exception("fail to restore")
            return self._compile_error_template(str(e))
        except ValueError:
            logger.exception("fail to restore")
            return self._compile_error_template(_("Fail to restore."))

        # Provide hint filename. Try to follow recommendation at
        # http://greenbytes.de/tech/tc2231/
        try:
            # 1. Used quoted filename for ascii filename.
            filename.encode('ascii')
            cd = 'attachment; filename="%s"' % filename
        except:
            # 2. Define filename as ascii for fallback. Define filename* with
            filename_ascii = filename.encode('ascii', 'replace').decode('ascii')
            filename_utf8 = filename.encode('utf-8', 'replace')
            cd = 'attachment; filename="%s"; filename*=UTF-8\'\'%s' % (
                filename_ascii,
                quote_url(filename_utf8, safe='?'))
        cherrypy.response.headers["Content-Disposition"] = cd

        # Stream the data.
        return _serve_fileobj(fileobj, content_type=None, content_length=None, debug=True)
