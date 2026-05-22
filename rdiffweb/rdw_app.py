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
import functools
import importlib.resources
import json
import logging
import os
from datetime import datetime, timezone

import cherrypy
import cherrypy.lib.sessions
import cherrypy_foundation.plugins.db
import cherrypy_foundation.plugins.ldap
import cherrypy_foundation.plugins.oauth
import cherrypy_foundation.plugins.restapi
import cherrypy_foundation.plugins.scheduler
import cherrypy_foundation.plugins.smtp
import cherrypy_foundation.tools.auth
import cherrypy_foundation.tools.auth_mfa
import cherrypy_foundation.tools.datatables
import cherrypy_foundation.tools.i18n
import cherrypy_foundation.tools.jinja2
import cherrypy_foundation.tools.ratelimit
import cherrypy_foundation.tools.secure_headers
import cherrypy_foundation.tools.sessions_timeout
import humanfriendly
from cherrypy import Application
from cherrypy_foundation.db_sessions import DbSession
from cherrypy_foundation.error_page import error_page
from cherrypy_foundation.flash import get_flashed_messages
from cherrypy_foundation.tools.i18n import format_timedelta, get_translation
from cherrypy_foundation.url import url_for

import rdiffweb
import rdiffweb.controller.filter_authorization
import rdiffweb.core.activity
import rdiffweb.core.diskusage
import rdiffweb.core.notification
import rdiffweb.core.quota
import rdiffweb.core.remove_older
import rdiffweb.tools.enrich_session
import rdiffweb.tools.errors
import rdiffweb.tools.poppath
import rdiffweb.tools.required_scope
from rdiffweb.controller import breadcrumb_page, breadcrumb_repo, page_registry
from rdiffweb.controller.api import ApiPage
from rdiffweb.controller.dispatch import staticfile
from rdiffweb.controller.page_admin import AdminPage
from rdiffweb.controller.page_browse import BrowsePage
from rdiffweb.controller.page_delete import DeletePage
from rdiffweb.controller.page_graphs import GraphsPage
from rdiffweb.controller.page_history import HistoryPage
from rdiffweb.controller.page_home import HomePage
from rdiffweb.controller.page_login import LoginPage, LogoutPage
from rdiffweb.controller.page_logs import LogsPage
from rdiffweb.controller.page_mfa import MfaPage
from rdiffweb.controller.page_prefs import PreferencesPage
from rdiffweb.controller.page_repo_activity import RepoActivityPage
from rdiffweb.controller.page_restore import RestorePage
from rdiffweb.controller.page_settings import SettingsPage
from rdiffweb.controller.page_stats import StatsPage
from rdiffweb.controller.static import Static
from rdiffweb.core.config import parse_args
from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import SessionObject, UserObject

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


def _json_handler(*args, **kwargs):
    """
    Custom json handle to convert RdiffDate to string as isoformat and to use "json" instead of simplejson.
    """
    value = cherrypy.serving.request._json_inner_handler(*args, **kwargs)

    def default(o):
        if isinstance(o, RdiffTime):
            return str(o)
        elif isinstance(o, datetime):
            return str(RdiffTime(o))
        raise TypeError(repr(o) + " is not JSON serializable")

    encode = json.JSONEncoder(default=default, ensure_ascii=False).iterencode
    for chunk in encode(value):
        yield chunk.encode('utf-8')


def _template_processor():
    # TODO Move to cherrypy-foundation
    values = {
        'lang': str(get_translation().locale),
        'current_url': cherrypy.url(path=cherrypy.request.path_info),
    }
    if hasattr(cherrypy.serving.request, 'login'):
        values['login'] = cherrypy.serving.request.login
    if hasattr(cherrypy.serving.request, 'currentuser'):
        currentuser = cherrypy.serving.request.currentuser
        values['currentuser'] = currentuser
        # TODO Should should be replace within the template.
        values['fullname'] = currentuser.fullname
        values['is_admin'] = currentuser.is_admin
        values['is_maintainer'] = currentuser.is_maintainer
    return values


@cherrypy.tools.allow(methods=['GET'])
@cherrypy.tools.auth(
    session_user_key=SessionObject.SESSION_USER_KEY,
    user_lookup_func=UserObject.get_create_or_update_user,
    user_from_key_func=UserObject.get_user,
    checkpassword=[UserObject.authenticate, cherrypy.ldap.authenticate],
)
@cherrypy.tools.auth_mfa(
    mfa_enabled=lambda: getattr(cherrypy.serving.request, 'currentuser', False)
    and cherrypy.request.currentuser.mfa == UserObject.ENABLED_MFA
)
@cherrypy.tools.enrich_session()
@cherrypy.tools.i18n(
    lang=lambda: getattr(cherrypy.serving.request, 'currentuser', False) and cherrypy.request.currentuser.lang,
    tzinfo=lambda: getattr(cherrypy.serving.request, 'currentuser', False) and cherrypy.request.currentuser.timezone,
)
@cherrypy.tools.proxy(local=None, remote='X-Real-IP')
@cherrypy.tools.ratelimit(on=False)
@cherrypy.tools.secure_headers(
    csp={
        "default-src": "'self'",
        "style-src": ("'self'", "'unsafe-inline'"),
        "script-src": ("'self'", "'unsafe-inline'"),
        "img-src": ("'self'", "data:"),
    }
)
@cherrypy.tools.sessions()
@cherrypy.tools.sessions_timeout()
class Root:
    def __init__(self):
        self.home = HomePage()
        self.login = LoginPage()
        self.logout = LogoutPage()
        self.mfa = MfaPage()
        self.browse = BrowsePage()
        self.delete = DeletePage()
        self.restore = RestorePage()
        self.history = HistoryPage()
        self.stats = StatsPage()
        self.admin = AdminPage()
        self.prefs = PreferencesPage()
        self.settings = SettingsPage()
        self.api = ApiPage()
        self.graphs = GraphsPage()
        self.logs = LogsPage()
        self.activity = RepoActivityPage()
        self.static = Static()

        # Register robots.txt
        robots_txt = importlib.resources.files('rdiffweb') / 'static/robots.txt'
        self.robots_txt = staticfile(robots_txt, doc="robots.txt to disable search crawler")

    @cherrypy.expose
    def index(self):
        # Redirect user to home page.
        currentuser = cherrypy.serving.request.currentuser
        raise cherrypy.HTTPRedirect(url_for('home', currentuser.username))

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.auth(on=False)
    @cherrypy.tools.auth_mfa(on=False)
    @cherrypy.tools.caching(on=True)
    @cherrypy.tools.ratelimit(on=False)
    @cherrypy.tools.response_headers(headers=[('Content-Type', 'text/css')])
    @cherrypy.tools.sessions(on=False)
    @cherrypy.tools.secure_headers(on=False)
    @cherrypy.tools.jinja2(template='main.css')
    def main_css(self, **kwargs):
        """
        Return CSS file based on branding configuration
        """
        return {}


class RdiffwebApp(Application):
    """This class represent the application context."""

    @classmethod
    def parse_args(cls, args=None, config_file_contents=None):
        return parse_args(args, config_file_contents)

    def __init__(self, cfg):
        self.cfg = cfg

        # Configure Jinja2 environment.
        env = cherrypy.tools.jinja2.create_env(
            package_name='rdiffweb',
            globals={
                'footer_name': cfg.footer_name,
                'footer_url': cfg.footer_url,
                'get_flashed_messages': get_flashed_messages,
                'header_name': cfg.header_name,
                'url_for': url_for,
                'version': rdiffweb.__version__,
                'page_registry': page_registry,
                'breadcrumb_repo': breadcrumb_repo,
                'breadcrumb_page': breadcrumb_page,
                # Color branding
                'link_color': cfg.link_color,
                'btn_bg_color': cfg.btn_bg_color,
                'btn_fg_color': cfg.btn_fg_color,
                'navbar_color': cfg.navbar_color,
                'font_family': cfg.font_family,
            },
            filters={
                'lastupdated': lambda dt: format_timedelta(dt - datetime.now(timezone.utc), add_direction=True),
                'filesize': functools.partial(humanfriendly.format_size, binary=True),
            },
        )

        # Pick the right implementation for storage
        rate_limit_storage_class = cherrypy_foundation.tools.ratelimit.RamRateLimit
        if cfg.rate_limit_dir:
            rate_limit_storage_class = cherrypy_foundation.tools.ratelimit.FileRateLimit

        # Configure all the plugins.
        db_uri = self.cfg.database_uri if '://' in self.cfg.database_uri else "sqlite:///" + self.cfg.database_uri
        cherrypy.config.update(
            {
                'environment': 'development' if cfg.debug else cfg.environment,
                'tools.encode.on': True,
                'tools.encode.encoding': 'utf-8',
                'tools.gzip.on': True,
                # Define error page handler.
                'error_page.default': error_page,
                # Configure database plugins
                'db.uri': db_uri,
                'db.debug': cfg.debug,
                'db.autocreate': True,
                # Configure external_url
                'tools.proxy.base': cfg.external_url,
                # Configure session storage
                'tools.sessions.debug': cfg.debug,
                'tools.sessions.locking': 'explicit',
                'tools.sessions.storage_class': DbSession,
                'tools.sessions.model_class': SessionObject,
                'tools.sessions.httponly': True,
                'tools.sessions.timeout': cfg.session_idle_timeout,  # minutes
                'tools.sessions.persistent': False,
                'tools.sessions_timeout.persistent_timeout': cfg.session_persistent_timeout,  # minutes
                'tools.sessions_timeout.absolute_timeout': cfg.session_absolute_timeout,  # minutes
                # Configure Auth & MFA timeout
                'tools.auth.reauth_timeout': cfg.session_idle_timeout,  # minutes
                'tools.auth_mfa.trust_duration': cfg.session_persistent_timeout,  # minutes
                # Configure rate limit
                'tools.ratelimit.debug': cfg.debug,
                'tools.ratelimit.delay': 3600,
                'tools.ratelimit.limit': cfg.rate_limit,
                'tools.ratelimit.storage_class': rate_limit_storage_class,
                'tools.ratelimit.storage_path': cfg.rate_limit_dir,
                # Configure custom json_handler
                'tools.json_out.handler': _json_handler,
                # Configure jinja2 templating engine
                'tools.jinja2.env': env,
                'tools.jinja2.extra_processor': _template_processor,
                # Configure LDAP plugin
                'ldap.uri': cfg.ldap_uri,
                'ldap.base_dn': cfg.ldap_base_dn,
                'ldap.bind_dn': cfg.ldap_bind_dn,
                'ldap.bind_password': cfg.ldap_bind_password,
                'ldap.scope': cfg.ldap_scope,
                'ldap.tls': cfg.ldap_tls,
                'ldap.username_attribute': cfg.ldap_username_attribute,
                'ldap.user_filter': cfg.ldap_user_filter,
                'ldap.required_group': cfg.ldap_required_group,
                'ldap.group_filter': cfg.ldap_group_filter,
                'ldap.group_attribute': cfg.ldap_group_attribute,
                'ldap.group_attribute_is_dn': cfg.ldap_group_attribute_is_dn,
                'ldap.version': cfg.ldap_version,
                'ldap.network_timeout': cfg.ldap_network_timeout,
                'ldap.timeout': cfg.ldap_timeout,
                'ldap.encoding': cfg.ldap_encoding,
                'ldap.fullname_attribute': cfg.ldap_fullname_attribute,
                'ldap.firstname_attribute': cfg.ldap_firstname_attribute,
                'ldap.lastname_attribute': cfg.ldap_lastname_attribute,
                'ldap.email_attribute': cfg.ldap_email_attribute,
                # Configure OAuth
                'oauth.auth_url': cfg.oauth_auth_url,
                'oauth.client_id': cfg.oauth_client_id,
                'oauth.client_secret': cfg.oauth_client_secret,
                'oauth.email_claim': cfg.oauth_email_claim,
                'oauth.firstname_claim': cfg.oauth_firstname_claim,
                'oauth.fullname_claim': cfg.oauth_fullname_claim,
                'oauth.lastname_claim': cfg.oauth_lastname_claim,
                'oauth.scope': cfg.oauth_scope,
                'oauth.token_url': cfg.oauth_token_url,
                'oauth.userinfo_url': cfg.oauth_userinfo_url,
                'oauth.userkey_claim': cfg.oauth_userkey_claim,
                'oauth.required_claims': cfg.oauth_required_claims,
                # Configure SMTP plugin
                'smtp.server': cfg.email_host,
                'smtp.username': cfg.email_username,
                'smtp.password': cfg.email_password,
                'smtp.email_from': (cfg.header_name, cfg.email_sender) if cfg.email_sender else None,
                'smtp.encryption': cfg.email_encryption,
                # Configure remove_older plugin
                'remove_older.execution_time': self.cfg.remove_older_time,
                # Configure notification plugin
                'notification.execution_time': self.cfg.email_notification_time,
                'notification.send_changed': self.cfg.email_send_changed_notification,
                'notification.header_name': self.cfg.header_name,
                'notification.env': env,
                'notification.bcc': self.cfg.email_catch_all,
                # Configure latest lookup notification.
                'notification.current_version': self.version,
                'notification.latest_version_url': self.cfg.latest_version_url,
                # Configure quota plugin
                'quota.set_quota_cmd': self.cfg.quota_set_cmd,
                'quota.get_quota_cmd': self.cfg.quota_get_cmd,
                'quota.get_usage_cmd': self.cfg.quota_used_cmd,
                # Configure locales
                'tools.i18n.default': cfg.default_lang,
                'tools.i18n.default_timezone': cfg.default_timezone,
                'tools.i18n.mo_dir': importlib.resources.files('rdiffweb') / 'locales',
                'tools.i18n.domain': 'messages',
                'tools.i18n.cookie_name': 'locale',
            }
        )

        config = {
            '/': {
                # To work around the new behaviour in CherryPy >= 5.5.0, force usage of
                # ISO-8859-1 encoding for URL. This avoid any conversion of the
                # URL into UTF-8.
                'request.uri_encoding': 'ISO-8859-1',
            },
            '/api': {'request.dispatch': cherrypy_foundation.plugins.restapi.Dispatcher()},
        }

        # Initialize the application
        Application.__init__(self, root=Root(), config=config)

        # Register favicon.ico
        self.root.favicon_ico = staticfile(
            cfg.favicon if cfg.favicon else importlib.resources.files('rdiffweb') / 'static/favicon.ico',
            doc="Return favicon image file.",
        )

        # Register header_logo
        self.root.header_logo = staticfile(
            (cfg.header_logo if cfg.header_logo else importlib.resources.files('rdiffweb') / 'static/header-logo.png'),
            doc="Return static `header-logo` image file.",
        )

        # Register login-bg
        self.root.login_bg = staticfile(
            cfg.login_bg if cfg.login_bg else importlib.resources.files('rdiffweb') / 'static/login-bg.png',
            doc="Return static `login-bg` image file.",
        )

        # Define TEMP env
        if cfg.tempdir:
            os.environ["TMPDIR"] = cfg.tempdir

        # Register a late callback to create admin user when starting
        cherrypy.engine.subscribe('start', self.on_start, priority=250)

    def on_start(self):
        # Since we are not a real plugin, let unsubscribe to avoid interference if server get restarted.
        cherrypy.engine.unsubscribe('start', self.on_start)

        # Create admin user
        user = UserObject.create_admin_user(self.cfg.admin_user, self.cfg.admin_password)
        user.commit()

    @property
    def version(self):
        """
        Get the current running version (using package info).
        """
        return rdiffweb.__version__
