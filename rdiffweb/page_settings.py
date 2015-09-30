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

from __future__ import unicode_literals

import cherrypy
import encodings
import logging

import librdiff
import page_main

from rdiffweb import rdw_helpers
from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_helpers import decode_s, unquote_url
from cherrypy._cperror import HTTPRedirect

# Define the logger
_logger = logging.getLogger(__name__)


class SettingsPage(page_main.MainPage):

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
    def index(self, path_b=b"", **kwargs):
        assert isinstance(path_b, str)

        _logger.debug("settings [%s]" % decode_s(path_b, 'replace'))

        # Check user permissions
        try:
            (repo_obj, path_obj) = self.validate_user_path(path_b)
        except librdiff.FileError as e:
            _logger.exception("invalid user path")
            return self._compile_error_template(unicode(e))

        # Check if any action to process.
        params = {}
        action = kwargs.get('action')
        if action:
            try:
                if action == "delete":
                    params.update(self._handle_delete(repo_obj, **kwargs))
                elif action == "set_encoding":
                    params.update(self._handle_set_encoding(repo_obj, **kwargs))
                else:
                    _logger.info("unknown action: %s", action)
                    raise cherrypy.NotFound("Unknown action")
            except ValueError as e:
                params['error'] = unicode(e)
            except HTTPRedirect as e:
                # Re-raise HTTPRedirect exception.
                raise e
            except Exception as e:
                _logger.warn("unknown error processing action", exc_info=True)
                params['error'] = _("Unknown error")

        # Get page data.
        try:
            params.update(self._get_parms_for_page(repo_obj))
        except librdiff.FileError:
            _logger.exception("can't create page params")
            return self._compile_error_template(unicode(e))

        # Generate page.
        return self._compile_template("settings.html", **params)

    def _get_parms_for_page(self, repo_obj):
        assert isinstance(repo_obj, librdiff.RdiffRepo)

        current_encoding = repo_obj.get_encoding() or rdw_helpers.system_charset
        current_encoding = encodings.normalize_encoding(current_encoding)

        return {
            'repo_name': repo_obj.display_name,
            'repo_path': repo_obj.path,
            'settings': True,
            'supported_encodings': self._get_encodings(),
            'current_encoding': current_encoding
        }

    def _get_encodings(self):
        """
        Return a complete list of valid encoding supported by current python.
        """
        return ["ascii", "big5", "big5hkscs", "cp037", "cp424", "cp437",
                "cp500", "cp720", "cp737", "cp775", "cp850", "cp852", "cp855",
                "cp856", "cp857", "cp858", "cp860", "cp861", "cp862", "cp863",
                "cp864", "cp865", "cp866", "cp869", "cp874", "cp875", "cp932",
                "cp949", "cp950", "cp1006", "cp1026", "cp1140", "cp1250",
                "cp1251", "cp1252", "cp1253", "cp1254", "cp1255", "cp1256",
                "cp1257", "cp1258", "euc_jp", "euc_jis_2004", "euc_jisx0213",
                "euc_kr", "gb2312", "gbk", "gb18030", "hz", "iso2022_jp",
                "iso2022_jp_1", "iso2022_jp_2", "iso2022_jp_2004",
                "iso2022_jp_3", "iso2022_jp_ext", "iso2022_kr", "latin_1",
                "iso8859_2", "iso8859_3", "iso8859_4", "iso8859_5",
                "iso8859_6", "iso8859_7", "iso8859_8", "iso8859_9",
                "iso8859_10", "iso8859_13", "iso8859_14", "iso8859_15",
                "iso8859_16", "johab", "koi8_r", "koi8_u", "mac_cyrillic",
                "mac_greek", "mac_iceland", "mac_latin2", "mac_roman",
                "mac_turkish", "ptcp154", "shift_jis", "shift_jis_2004",
                "shift_jisx0213", "utf_32", "utf_32_be", "utf_32_le",
                "utf_16", "utf_16_be", "utf_16_le", "utf_7", "utf_8",
                "utf_8_sig"]

    def _handle_delete(self, repo_obj, **kwargs):
        """
        Delete the repository.
        """
        # Validate the name
        confirm_name = kwargs.get('confirm_name')
        if confirm_name != repo_obj.display_name:
            raise ValueError(_("confirmation doesn't matches"))

        # Update the repository encoding
        _logger.info("deleting repository [%s]", repo_obj)
        repo_obj.delete()

        # Refresh repository list
        username = self.app.currentuser.username
        repos = self.app.userdb.get_repos(username)
        repos.remove(b"/" + repo_obj.path)
        self.app.userdb.set_repos(username, repos)

        raise HTTPRedirect("/")

    def _handle_set_encoding(self, repo_obj, **kwargs):
        """
        Change the encoding of the repository.
        """
        # Validate the encoding value
        new_encoding = kwargs.get('encoding')
        new_encoding = unicode(encodings.normalize_encoding(new_encoding)).lower()
        if new_encoding not in self._get_encodings():
            raise ValueError(_("invalid encoding value"))

        # Update the repository encoding
        _logger.info("updating repository [%s] encoding [%s]", repo_obj, new_encoding)
        repo_obj.set_encoding(new_encoding)

        return {'success': _("Repository updated successfully with new encoding.")}
