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

import logging
from urllib.parse import quote, unquote_to_bytes

import cherrypy
from cherrypy.lib.static import mimetypes
from cherrypy_foundation.url import url_for

import rdiffweb.tools.errors  # noqa: cherrypy.tools.errors
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject
from rdiffweb.core.restore import ARCHIVERS

from . import validate_date

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
    return 'attachment; filename*=UTF-8\'\'%s' % quote(filename_utf8, safe='?')


def _content_type(filename):
    """
    Using filename, try to guess the content-type.
    """
    ext = ''
    i = filename.rfind('.')
    if i != -1:
        ext = filename[i:].lower()
    return mimetypes.types_map.get(ext, "application/octet-stream")


class _file_generator(object):
    """
    Yield the given input (a file object) in chunks (default 64k).
    """

    def __init__(self, input, chunkSize=65536):
        self.input = input
        self.chunkSize = chunkSize

    def __iter__(self):
        return self

    def __next__(self):
        chunk = self.input.read(self.chunkSize)
        if chunk:
            return chunk
        else:
            if hasattr(self.input, 'close'):
                self.input.close()
            raise StopIteration()

    next = __next__

    def close(self):
        if hasattr(self.input, 'close'):
            self.input.close()


class RestorePage:

    def _cp_dispatch(self, vpath):
        """
        Return the right handle if raw=1
        """
        func = self._raw if 'raw=1' in cherrypy.request.query_string else self.default
        cherrypy.serving.request.params = {
            'path': b"/".join([unquote_to_bytes(segment.encode('ISO-8859-1')) for segment in vpath])
        }
        vpath.clear()
        return func

    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            ValueError: 400,
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    @cherrypy.tools.jinja2(template="restore.html")
    def default(self, path=b"", date=None, kind=None, **kwargs):
        """
        Display a webpage to prepare download or trigger download of a file or folder.
        """
        validate_date(date)
        if kind is not None and kind not in ARCHIVERS:
            raise cherrypy.HTTPError(400, 'invalid kind: %s' % kind)
        repo, path = RepoObject.get_repo_path(path, refresh=False)
        params = {"repo": repo, "path": path}
        if repo.status[0] == 'ok':
            # If repo is healthy, return a download url
            params['download_url'] = url_for('restore', repo, path, date=date, kind=kind, raw=1)
        else:
            # Otherwise, return a HTTP error.
            # 400 might not be the best error code.
            cherrypy.response.status = 400
        return params

    @cherrypy.expose
    @cherrypy.tools.gzip(on=False)
    @cherrypy.tools.errors(
        error_table={
            ValueError: 400,
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    def _raw(self, path=b"", date=None, kind=None, **kwargs):
        """
        Restore a file or folder.
        """
        date = validate_date(date)
        if kind is not None and kind not in ARCHIVERS:
            raise cherrypy.HTTPError(400, 'invalid kind: %s' % kind)

        # Check user access to repo / path.
        repo, path = RepoObject.get_repo_path(path, refresh=False)

        # Restore file(s)
        filename, fileobj = repo.restore(path, int(date), kind=kind)

        # Define content-disposition.
        cherrypy.response.headers["Content-Disposition"] = _content_disposition(filename)

        # Set content-type based on filename extension
        content_type = _content_type(filename)
        cherrypy.response.headers['Content-Type'] = content_type

        # Set-Cookie: downloadStarted=1
        # To detect download in restore page.
        cherrypy.response.cookie['downloadStarted'] = 1

        # Log activity
        cherrypy.engine.publish('restore_path', repo=repo, path=path)
        repo.commit()

        # Stream the data.
        return _file_generator(fileobj)

    _raw._cp_config = {"response.stream": True}
