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
from collections import namedtuple

import cherrypy
from cherrypy_foundation.tools.i18n import gettext_lazy as _
from cherrypy_foundation.url import url_for

from rdiffweb.core.librdiff import RdiffTime

# Define the logger
logger = logging.getLogger(__name__)


class Page(
    namedtuple('Page', ['id', 'label', 'url_for', 'icon', 'in_menu', 'active_page'], defaults=[None, True, None])
):

    def __hash__(self):
        return self.id.__hash__()

    def __eq__(self, other):
        return self and other and isinstance(other, Page) and self.id == other.id


class PageRegistry(dict):
    """
    Page registry built manually.
    """

    def __getitem__(self, page_id):
        return super().__getitem__(page_id)

    def get(self, page_id, default=None):
        if page_id.endswith('.html'):
            page_id = page_id[:-5]
        return super().get(page_id, default)

    def get_repo_nav_pages(self, in_menu=True):
        repo_pages = ['browse', 'history', 'restore', 'insights', 'settings']
        return [
            page for page in self.values() if page.id in repo_pages and (in_menu is None or page.in_menu == in_menu)
        ]

    def get_insight_nav_pages(self, in_menu=True):
        return [
            page
            for page in self.values()
            if page.active_page == 'insights' and (in_menu is None or page.in_menu == in_menu)
        ]

    def get_admin_nav_pages(self, in_menu=True):
        return [
            page
            for page in self.values()
            if page.id.startswith('admin_') and (in_menu is None or page.in_menu == in_menu)
        ]

    def get_prefs_nav_pages(self, in_menu=True):
        return [
            page
            for page in self.values()
            if page.id.startswith('prefs_') and (in_menu is None or page.in_menu == in_menu)
        ]


_pages = [
    Page('home', _('Home'), 'home', 'bi-house-fill'),
    # Repo
    Page('browse', _('Files'), 'browse', 'bi-folder'),
    Page('history', _('History'), 'history', None, False, 'browse'),
    Page('restore', _('Restore'), 'restore', None, False, 'browse'),
    Page('insights', _('Insights'), 'graphs', 'bi-lightbulb'),
    Page('settings', _('Settings'), 'settings', 'bi-sliders'),
    # Insights
    Page('graphs', _('Statistics'), 'graphs', 'bi-bar-chart-line', True, 'insights'),
    Page('stats', _('File Changes'), 'stats', 'bi-clock-history', True, 'insights'),
    Page('logs', _('Engine Logs'), 'logs', 'bi-journal-text', True, 'insights'),
    Page('repo_activity', _('Audit logs'), 'activity', None, True, 'insights'),
    # Admin
    Page('admin', _('Administration'), None, None, False),
    Page('admin_users', _('Users'), 'admin/users', 'bi-people-fill'),
    Page('admin_user_edit', _('Edit User'), 'admin/users/edit', None, False, 'admin_users'),
    Page('admin_user_new', _('Add User'), 'admin/users/new', None, False, 'admin_users'),
    Page('admin_repos', _('Repositories'), 'admin/repos', 'bi-archive-fill'),
    Page('admin_session', _('User Sessions'), 'admin/session', 'bi-display'),
    Page('admin_activity', _('Activity'), 'admin/activity', 'bi-activity'),
    Page('admin_logs', _('System Logs'), 'admin/logs', 'bi-journal-text'),
    Page('admin_sysinfo', _('System Info'), 'admin/sysinfo', ' bi-info-circle'),
    # User Preferences
    Page('prefs', _('User Profile'), None, None, False),
    Page('prefs_general', _('Account Settings'), 'prefs/general'),
    Page('prefs_notification', _('Notifications & Report'), 'prefs/notification'),
    Page('prefs_sshkeys', _('SSH Keys'), 'prefs/sshkeys'),
    Page('prefs_tokens', _('Access Tokens'), 'prefs/tokens'),
    Page('prefs_mfa', _('Two-Factor Authentication'), 'prefs/mfa'),
    Page('prefs_session', _('Browser Sessions'), 'prefs/session'),
]

page_registry = PageRegistry({page.id: page for page in _pages})


def breadcrumb_page(page):
    # Resolve page_id, or page template name.
    page = page_registry.get(page if isinstance(page, str) else page._TemplateReference__context.name)
    if page.url_for:
        return [(url_for(page), page.label)]
    return [(None, page.label)]


def breadcrumb_repo(repo, page=None, path=None, extend=False):
    """
    Create breadcrumbs for path object.
    Return a list of tuple.
    """
    # Resolve page_id, or page template name.
    if page:
        page = page_registry.get(page if isinstance(page, str) else page._TemplateReference__context.name)

    if path is not None:
        # Path as bytes
        if path and extend:
            parts = path.split(b'/')
            return [(url_for(page, repo, b'/'.join(parts[: i + 1])), repo._decode(parts[i])) for i in range(len(parts))]
        elif path:
            return [(url_for(page, repo, path), page.label)]
        else:
            # When path is root.
            return []

    elif page is not None:
        # Page
        return [(url_for(page, repo), page.label)]

    # Repo
    currentuser = cherrypy.serving.request.currentuser
    if currentuser != repo.user:
        return [
            (url_for('home', repo.user.username), _("@%s") % repo.user.username),
            (url_for('browse', repo), repo.display_name),
        ]

    return [(url_for('/'), _("Home")), (url_for('browse', repo), repo.display_name)]


def validate_int(value, min=None, max=None):
    """Returns a converter function that validates integer ranges"""
    try:
        val = int(value)
    except (ValueError, TypeError):
        raise cherrypy.HTTPError(400, f"Invalid integer: {value}")

    if min is not None and val < min:
        raise cherrypy.HTTPError(400, f"Must be >= {min}")
    if max is not None and val > max:
        raise cherrypy.HTTPError(400, f"Must be <= {max}")

    return val


def validate_date(value, allow_none=False):
    """Returns a converter function that validates date"""

    if value is None and allow_none:
        return None
    try:
        return RdiffTime(int(value))
    except (ValueError, TypeError):
        pass
    try:
        return RdiffTime(value)
    except (ValueError, TypeError):
        pass
    raise cherrypy.HTTPError(400, f"Invalid date: {value}")
