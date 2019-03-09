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

from distutils.version import LooseVersion
import logging
import os
from rdiffweb.controller import Controller
from rdiffweb.controller import filter_authentication  # @UnusedImport
from rdiffweb.controller.api import ApiPage
from rdiffweb.controller.dispatch import static, empty  # @UnusedImport
from rdiffweb.controller.page_admin import AdminPage
from rdiffweb.controller.page_browse import BrowsePage
from rdiffweb.controller.page_graphs import GraphsPage
from rdiffweb.controller.page_history import HistoryPage
from rdiffweb.controller.page_locations import LocationsPage
from rdiffweb.controller.page_prefs import PreferencesPage
from rdiffweb.controller.page_restore import RestorePage
from rdiffweb.controller.page_settings import SettingsPage, SetEncodingPage, RemoveOlderPage, \
    DeleteRepoPage
from rdiffweb.controller.page_status import StatusPage
from rdiffweb.core import i18n  # @UnusedImport
from rdiffweb.core import rdw_templating
from rdiffweb.core.config import Option
from rdiffweb.core.librdiff import DoesNotExistError, AccessDeniedError
from rdiffweb.core.user import UserManager
import sys

from cherrypy import Application
import cherrypy
from future.utils import native_str
import pkg_resources

# Define the logger
logger = logging.getLogger(__name__)

PY3 = sys.version_info[0] == 3


class Root(LocationsPage):

    def __init__(self):
        self.browse = BrowsePage()
        self.restore = RestorePage()
        self.history = HistoryPage()
        self.status = StatusPage()
        self.admin = AdminPage()
        self.prefs = PreferencesPage()
        self.settings = SettingsPage()
        self.api = ApiPage()
        self.api.set_encoding = SetEncodingPage()
        self.api.remove_older = RemoveOlderPage()
        self.delete = DeleteRepoPage()
        self.graphs = GraphsPage()

        # Register static dir.
        static_dir = pkg_resources.resource_filename('rdiffweb', 'static')  # @UndefinedVariable
        self.static = static(static_dir)

        # Register robots.txt
        robots_txt = pkg_resources.resource_filename('rdiffweb', 'static/robots.txt')  # @UndefinedVariable
        self.robots_txt = static(robots_txt)


class RdiffwebApp(Application):
    """This class represent the application context."""

    _favicon = Option('Favicon', default=pkg_resources.resource_filename('rdiffweb', 'static/favicon.ico'))  # @UndefinedVariable
    
    _header_logo = Option('HeaderLogo')
    
    _tempdir = Option('TempDir')

    def __init__(self, cfg={}):
        self.cfg = {k.lower(): v for k, v in cfg.items()}
        
        # Initialise the template engine.
        self.templates = rdw_templating.TemplateManager()

        # Get some config
        session_path = self.cfg.get("sessiondir", None)

        # Initialise the application
        config = {
            native_str('/'): {
                'tools.authform.on': True,
                'tools.i18n.on': True,
                'tools.i18n.default': 'en_US',
                'tools.i18n.mo_dir': pkg_resources.resource_filename('rdiffweb', 'locales'),  # @UndefinedVariable
                'tools.i18n.domain': 'messages',
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.gzip.on': True,
                'tools.sessions.on': True,
                'error_page.default': self.error_page,
                'request.error_response': self.error_response,
                'tools.sessions.storage_type': 'file' if session_path else 'ram',
                'tools.sessions.storage_path': session_path,
            },
        }

        # To work around the new behaviour in CherryPy >= 5.5.0, force usage of
        # ISO-8859-1 encoding for URL. This avoid any conversion of the
        # URL into UTF-8.
        if PY3 and LooseVersion(cherrypy.__version__) >= LooseVersion("5.5.0"):
            config[native_str('/')]["request.uri_encoding"] = "ISO-8859-1"

        # Initialize the application
        Application.__init__(self, root=Root(), config=config)
        
        # Register favicon.ico
        self.root.favicon_ico = static(self._favicon)
        
        # Register header_logo
        if self._header_logo:
            self.root.header_logo = static(self._header_logo)
        
        # Define TEMP env
        if self._tempdir:
            os.environ["TMPDIR"] = self._tempdir

        # create user manager
        self.userdb = UserManager(self)

    @property
    def currentuser(self):
        """
        Get the current user.
        """
        return cherrypy.serving.request.login

    def error_page(self, **kwargs):
        """
        Default error page shown to the user when an unexpected error occur.
        """
        # Log exception.
        logger.exception(kwargs.get('message', ''))

        # Check expected response type.
        mtype = cherrypy.tools.accept.callable(['text/html', 'text/plain'])  # @UndefinedVariable
        if mtype == 'text/plain':
            return kwargs.get('message')

        # Try to build a nice error page.
        try:
            page = Controller()
            return page._compile_template('error_page_default.html', **kwargs)
        except:
            pass
        # If failing, send the raw error message.
        return kwargs.get('message')

    def error_response(self):
        """
        Called when ever an exception reach cherrypy core. This implementation
        will convert the exception into the right HTTP Error.
        """
        code = 500
        t = sys.exc_info()[0]
        if t in [AccessDeniedError, DoesNotExistError]:
            code = 404
        cherrypy.HTTPError(code).set_response()

    def get_version(self):
        """
        Get the current running version (using package info).
        """
        # Get version.
        try:
            return pkg_resources.get_distribution("rdiffweb").version
        except:
            return "DEV"
