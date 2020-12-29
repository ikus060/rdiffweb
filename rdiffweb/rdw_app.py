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

from collections import namedtuple
from distutils.version import LooseVersion
import logging
import os
import sys

from cherrypy import Application
import cherrypy
import pkg_resources

import rdiffweb
from rdiffweb.controller import Controller
from rdiffweb.controller import filter_authentication  # @UnusedImport
from rdiffweb.controller import filter_authorization  # @UnusedImport
from rdiffweb.controller.api import ApiPage
from rdiffweb.controller.dispatch import static, empty  # @UnusedImport
from rdiffweb.controller.page_admin import AdminPage
from rdiffweb.controller.page_browse import BrowsePage
from rdiffweb.controller.page_graphs import GraphsPage
from rdiffweb.controller.page_history import HistoryPage
from rdiffweb.controller.page_locations import LocationsPage
from rdiffweb.controller.page_prefs import PreferencesPage
from rdiffweb.controller.page_restore import RestorePage
from rdiffweb.controller.page_settings import SettingsPage
from rdiffweb.controller.page_status import StatusPage
from rdiffweb.core import i18n  # @UnusedImport
from rdiffweb.core import rdw_templating
from rdiffweb.core.config import Option
from rdiffweb.core.librdiff import DoesNotExistError, AccessDeniedError
from rdiffweb.core.quota import DefaultUserQuota
from rdiffweb.core.store import Store

# Define the logger
logger = logging.getLogger(__name__)

# Enabled tools.proxy only for version < 5 or > 10
# From version 5 to 10, a bug in cherrypy is breaking creation of base url.
cherrypy_version = cherrypy.__version__
if cherrypy_version == 'unknown':
    # From time to time the cheroot dependencies is broken on python3.5
    # So default to enabling proxy. https://www.illumos.org/issues/10508
    cp_tools_proxy_enabled = True
    cp_uri_encoding_enabled = True
else:
    cp_uri_encoding_enabled = LooseVersion(cherrypy.__version__) >= LooseVersion("5.5.0")
    cp_tools_proxy_enabled = not (5 <= int(cherrypy_version.split('.')[0]) <= 10)


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
        # Keep this for backward compatibility.
        self.api.set_encoding = self.settings
        self.api.remove_older = self.settings
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

    _user_quota = Option('UserQuota', default="default")

    def __init__(self, cfg={}):
        self.cfg = {k.lower(): v for k, v in cfg.items()}

        # Initialise the template engine.
        self.templates = rdw_templating.TemplateManager()

        # Get some config
        session_path = self.cfg.get("sessiondir", None)

        # Initialise the application
        config = {
            '/': {
                'tools.authform.on': True,
                'tools.i18n.on': True,
                'tools.i18n.default': 'en_US',
                'tools.i18n.mo_dir': pkg_resources.resource_filename('rdiffweb', 'locales'),  # @UndefinedVariable
                'tools.i18n.domain': 'messages',
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.gzip.on': True,
                'tools.sessions.on': True,
                'tools.proxy.on': cp_tools_proxy_enabled,
                'error_page.default': self.error_page,
                'request.error_response': self.error_response,
                'tools.sessions.storage_type': 'file' if session_path else 'ram',
                'tools.sessions.storage_path': session_path,
            },
        }

        # To work around the new behaviour in CherryPy >= 5.5.0, force usage of
        # ISO-8859-1 encoding for URL. This avoid any conversion of the
        # URL into UTF-8.
        if cp_uri_encoding_enabled:
            config['/']["request.uri_encoding"] = "ISO-8859-1"

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

        # Load UserQuota entry point
        self.quota = self._load_quota()

        # create user manager
        self.store = Store(self)
        self.store.create_admin_user()

    @property
    def currentuser(self):
        """
        Proxy property to get current user from cherrypy request object.
        Return a UserObject when logged in or None.
        """
        return getattr(cherrypy.serving.request, 'currentuser', None)

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
        if t == DoesNotExistError:
            code = 404
        elif t == AccessDeniedError:
            code = 403
        cherrypy.HTTPError(code).set_response()

    def _load_quota(self):
        """
        Load the right quota module
        """
        # If a custom module define a IUserQuota, let make use of it.
        entry_point = next(pkg_resources.iter_entry_points('rdiffweb.IUserQuota'), None)  # @UndefinedVariable
        if entry_point:
            try:
                cls = entry_point.load()
                return cls(self)
            except:
                logger.warning('IUserQuota [%s] fail to load, fall back to default quota', entry_point, exc_info=1)
                return DefaultUserQuota(self)
        # Otherwise, return default
        return DefaultUserQuota(self)

    @property
    def version(self):
        """
        Get the current running version (using package info).
        """
        return rdiffweb.__version__

    @property
    def plugins(self):
        """
        Return list of plugins.
        """
        RiffwebPlugin = namedtuple('RiffwebPlugin', ['name', 'version'])
        for group in ['rdiffweb.IUserQuota', 'rdiffweb.IUserChangeListener']:
            for e in pkg_resources.iter_entry_points(group):
                yield RiffwebPlugin(name=e.name, version=e.dist)
