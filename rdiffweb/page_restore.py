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

from rdiffweb import page_main
from rdiffweb import rdw_helpers
import rdiffweb
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_helpers import quote_url
from rdiffweb.archiver import ARCHIVERS


# Define the logger
logger = logging.getLogger(__name__)


@rdiffweb.dispatch.poppath()
class RestorePage(page_main.MainPage):
    _cp_config = {"response.stream": True, "response.timeout": 3000}

    def _content_disposition(self, filename):
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

    @cherrypy.expose
    @cherrypy.tools.gzip(on=False)
    def default(self, path=b"", date=None, kind=None, usetar=None):
        self.assertIsInstance(path, bytes)
        self.assertIsInstance(date, str)
        self.assertTrue(kind is None or kind in ARCHIVERS)
        self.assertTrue(usetar is None or isinstance(usetar, str))

        logger.debug("restoring [%r][%s]", path, date)

        # The path wont have leading and trailing "/".
        (path, file_b) = os.path.split(path)
        if not path:
            path = file_b
            file_b = b""

        # Check user access to repo / path.
        (repo_obj, path_obj) = self.validate_user_path(path)

        # Get the restore date
        try:
            rdw_helpers.rdwTime(int(date))
        except:
            logger.warning("invalid date %s", date)
            raise cherrypy.HTTPError(400, _("Invalid date."))

        # Get if backup in progress
        if repo_obj.in_progress:
            raise cherrypy.HTTPError(500, _("""A backup is currently in progress to this repository. Restores are disabled until this backup is complete."""))

        # Determine the kind.
        kind = kind or 'zip'
        if usetar is not None:
            kind = 'tar.gz'

        # Restore file(s)
        filename, fileobj = path_obj.restore(file_b, int(date), kind=kind)

        # Define content-disposition.
        cherrypy.response.headers["Content-Disposition"] = self._content_disposition(filename)

        # Stream the data.
        return _serve_fileobj(fileobj, content_type=None, content_length=None)
