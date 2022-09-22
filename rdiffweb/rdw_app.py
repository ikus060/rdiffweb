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
import os

import cherrypy
import cherrypy.lib.sessions
import pkg_resources
from cherrypy import Application

import rdiffweb
import rdiffweb.controller.filter_authorization
import rdiffweb.core.notification
import rdiffweb.core.quota
import rdiffweb.core.remove_older
import rdiffweb.plugins.ldap
import rdiffweb.plugins.scheduler
import rdiffweb.plugins.smtp
import rdiffweb.tools.auth_basic
import rdiffweb.tools.auth_form
import rdiffweb.tools.currentuser
import rdiffweb.tools.errors
import rdiffweb.tools.i18n
import rdiffweb.tools.proxy
import rdiffweb.tools.ratelimit
import rdiffweb.tools.real_ip
import rdiffweb.tools.secure_headers
from rdiffweb.controller import Controller
from rdiffweb.controller.api import ApiPage
from rdiffweb.controller.dispatch import static  # noqa
from rdiffweb.controller.page_admin import AdminPage
from rdiffweb.controller.page_browse import BrowsePage
from rdiffweb.controller.page_delete import DeletePage
from rdiffweb.controller.page_graphs import GraphsPage
from rdiffweb.controller.page_history import HistoryPage
from rdiffweb.controller.page_locations import LocationsPage
from rdiffweb.controller.page_login import LoginPage, LogoutPage
from rdiffweb.controller.page_logs import LogsPage
from rdiffweb.controller.page_prefs import PreferencesPage
from rdiffweb.controller.page_restore import RestorePage
from rdiffweb.controller.page_settings import SettingsPage
from rdiffweb.controller.page_status import StatusPage
from rdiffweb.core import rdw_templating
from rdiffweb.core.config import Option, parse_args
from rdiffweb.core.store import Store

# Define the logger
logger = logging.getLogger(__name__)

# Define cherrypy development environment
cherrypy.config.environments['development'] = {
    'engine.autoreload.on': True,
    'checker.on': False,
    'tools.log_headers.on': True,
    'request.show_tracebacks': True,
    'request.show_mismatched_params': True,
    'log.screen': False,
}


@cherrypy.tools.proxy(remote=None)
@cherrypy.tools.secure_headers()
@cherrypy.tools.real_ip()
class Root(LocationsPage):
    def __init__(self):
        self.login = LoginPage()
        self.logout = LogoutPage()
        self.browse = BrowsePage()
        self.delete = DeletePage()
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
        self.logs = LogsPage()

        # Register static dir.
        static_dir = pkg_resources.resource_filename('rdiffweb', 'static')  # @UndefinedVariable
        self.static = static(static_dir)

        # Register robots.txt
        robots_txt = pkg_resources.resource_filename('rdiffweb', 'static/robots.txt')  # @UndefinedVariable
        self.robots_txt = static(robots_txt)


class RdiffwebApp(Application):
    """This class represent the application context."""

    _favicon = Option('favicon')

    _header_logo = Option('header_logo')

    _tempdir = Option('tempdir')

    _session_dir = Option('session_dir')

    @classmethod
    def parse_args(cls, args=None, config_file_contents=None):
        return parse_args(args, config_file_contents)

    def __init__(self, cfg):
        self.cfg = cfg
        cherrypy.config.update(
            {
                'environment': 'development' if cfg.debug else cfg.environment,
                # Configure LDAP plugin
                'ldap.uri': cfg.ldap_uri,
                'ldap.base_dn': cfg.ldap_base_dn,
                'ldap.bind_dn': cfg.ldap_bind_dn,
                'ldap.bind_password': cfg.ldap_bind_password,
                'ldap.scope': cfg.ldap_scope,
                'ldap.tls': cfg.ldap_tls,
                'ldap.username_attribute': cfg.ldap_username_attribute,
                'ldap.required_group': cfg.ldap_required_group,
                'ldap.group_attribute': cfg.ldap_group_attribute,
                'ldap.group_attribute_is_dn': cfg.ldap_group_attribute_is_dn,
                'ldap.version': cfg.ldap_version,
                'ldap.network_timeout': cfg.ldap_network_timeout,
                'ldap.timeout': cfg.ldap_timeout,
                'ldap.encoding': cfg.ldap_encoding,
                # Configure SMTP plugin
                'smtp.server': cfg.email_host,
                'smtp.username': cfg.email_username,
                'smtp.password': cfg.email_password,
                'smtp.email_from': cfg.email_sender
                and '%s <%s>'
                % (
                    cfg.header_name,
                    cfg.email_sender,
                ),
                'smtp.encryption': cfg.email_encryption,
                # Configure remove_older plugin
                'remove_older.execution_time': self.cfg.remove_older_time,
                # Configure notification plugin
                'notification.execution_time': self.cfg.email_notification_time,
                'notification.send_changed': self.cfg.email_send_changed_notification,
                # Configure quota plugin
                'quota.set_quota_cmd': self.cfg.quota_set_cmd,
                'quota.get_quota_cmd': self.cfg.quota_get_cmd,
                'quota.get_usage_cmd': self.cfg.quota_used_cmd,
            }
        )

        # Initialise the template engine.
        self.templates = rdw_templating.TemplateManager()

        # Pick the right implementation for storage
        session_storage_class = cherrypy.lib.sessions.RamSession
        rate_limit_storage_class = rdiffweb.tools.ratelimit.RamRateLimit
        if self._session_dir:
            session_storage_class = cherrypy.lib.sessions.FileSession
            rate_limit_storage_class = rdiffweb.tools.ratelimit.FileRateLimit

        config = {
            '/': {
                # To work around the new behaviour in CherryPy >= 5.5.0, force usage of
                # ISO-8859-1 encoding for URL. This avoid any conversion of the
                # URL into UTF-8.
                'request.uri_encoding': 'ISO-8859-1',
                'tools.auth_basic.realm': 'rdiffweb',
                'tools.auth_basic.checkpassword': self._checkpassword,
                'tools.auth_form.on': True,
                'tools.currentuser.on': True,
                'tools.currentuser.userobj': lambda username: self.store.get_user(username),
                'tools.i18n.on': True,
                'tools.i18n.default': 'en_US',
                'tools.i18n.mo_dir': pkg_resources.resource_filename('rdiffweb', 'locales'),  # @UndefinedVariable
                'tools.i18n.domain': 'messages',
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.gzip.on': True,
                'error_page.default': self.error_page,
                'tools.sessions.on': True,
                'tools.sessions.debug': cfg.debug,
                'tools.sessions.storage_class': session_storage_class,
                'tools.sessions.storage_path': self._session_dir,
                'tools.sessions.httponly': True,
                'tools.ratelimit.debug': cfg.debug,
                'tools.ratelimit.delay': 60,
                'tools.ratelimit.anonymous_limit': cfg.rate_limit,
                'tools.ratelimit.storage_class': rate_limit_storage_class,
                'tools.ratelimit.storage_path': self._session_dir,
            },
        }

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
        self.store = Store(self)
        self.store.create_admin_user()

    @property
    def currentuser(self):
        """
        Proxy property to get current user from cherrypy request object.
        Return a UserObject when logged in or None.
        """
        return getattr(cherrypy.serving.request, 'currentuser', None)

    def _checkpassword(self, realm, username, password):
        """
        Check basic authentication.
        """
        return self.store.login(username, password) is not None

    def error_page(self, **kwargs):
        """
        Default error page shown to the user when an unexpected error occur.
        """
        # Log exception.
        logger.error(
            'error page: %s %s\n%s' % (kwargs.get('status', ''), kwargs.get('message', ''), kwargs.get('traceback', ''))
        )

        # Replace message by generic one for 404. Default implementation leak path info.
        if kwargs.get('status', '') == '404 Not Found':
            kwargs['message'] = 'Nothing matches the given URI'

        # Check expected response type.
        mtype = cherrypy.tools.accept.callable(['text/html', 'text/plain'])  # @UndefinedVariable
        if mtype == 'text/plain':
            return kwargs.get('message')

        # Try to build a nice error page.
        try:
            page = Controller()
            return page._compile_template('error_page_default.html', **kwargs)
        except Exception:
            # If failing, send the raw error message.
            return kwargs.get('message')

    @property
    def version(self):
        """
        Get the current running version (using package info).
        """
        return rdiffweb.__version__
