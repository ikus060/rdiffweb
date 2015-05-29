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

import cherrypy
import logging
import os

from i18n import ugettext as _
from cherrypy.lib.static import serve_file

import librdiff
import page_main
import rdw_helpers

from rdw_helpers import decode_s, unquote_url

# Define the logger
logger = logging.getLogger(__name__)


def autodelete():
    """Register an handler to delete the restored files when the HTTP
    request is ending."""
    if not hasattr(cherrypy.request, "_autodelete_dir"):
        return
    autodelete_dir = cherrypy.request._autodelete_dir
    logger.info("deleting temporary folder [%s]" %
                decode_s(autodelete_dir, 'replace'))
    # Check if path exists
    if not os.access(autodelete_dir, os.F_OK):
        logger.info("temporary folder [%s] doesn't exists" %
                    decode_s(autodelete_dir, 'replace'))
        return
    if not os.path.isdir(autodelete_dir):
        autodelete_dir = os.path.dirname(autodelete_dir)
    rdw_helpers.remove_dir(autodelete_dir)

cherrypy.tools.autodelete = cherrypy.Tool('on_end_request', autodelete)


class rdiffRestorePage(page_main.rdiffPage):
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
            cherrypy.request.params['path_b'] = b"/".join(path)
            return self

        return vpath

    @cherrypy.expose
    @cherrypy.tools.autodelete()
    @cherrypy.tools.decode(default_encoding='Latin-1')
    def index(self, path_b=b"", date="", usetar=""):
        assert isinstance(path_b, str)
        assert isinstance(date, unicode)
        assert isinstance(usetar, unicode)

        logger.debug("restoring [%s][%s]" % (decode_s(path_b, 'replace'),
                                             date))

        # The path_b wont have leading and trailing "/".
        (path_b, file_b) = os.path.split(path_b)
        if not path_b:
            path_b = file_b
            file_b = b""

        # Check user access to repo / path.
        try:
            (repo_obj, path_obj) = self.validate_user_path(path_b)
        except librdiff.FileError as e:
            logger.exception("invalid user path")
            return self._writeErrorPage(unicode(e))

        # Get the restore date
        try:
            restore_date = rdw_helpers.rdwTime()
            restore_date.initFromInt(int(date))
        except:
            logger.warn("invalid date %s" % date)
            return self._writeErrorPage(_("Invalid date."))

        try:
            # Get if backup in progress
            if repo_obj.in_progress:
                return self._writeErrorPage(_("""A backup is currently in progress to this repository. Restores are disabled until this backup is complete."""))

            # Restore the file
            file_path_b = path_obj.restore(file_b, restore_date, usetar != "T")

        except librdiff.FileError as e:
            logger.exception("fail to restore")
            return self._writeErrorPage(unicode(e))
        except ValueError:
            logger.exception("fail to restore")
            return self._writeErrorPage(_("Fail to restore."))

        # The restored file path need to be deleted when the user is finish
        # downloading. The auto-delete tool, will do it if we give him a file
        # to delete.
        cherrypy.request._autodelete_dir = file_path_b

        # The file name return by rdiff-backup is in bytes. We do not process
        # it. Cherrypy seams to handle it any weird encoding from this point.
        logger.info("restored file [%s]" % decode_s(file_path_b, 'replace'))
        filename = os.path.basename(file_path_b)
        # Escape quotes in filename
        filename = filename.replace(b"\"", b"\\\"")
        return serve_file(file_path_b, None, disposition=b"attachment",
                          name=filename)
