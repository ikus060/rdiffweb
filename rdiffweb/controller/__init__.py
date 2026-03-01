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

from rdiffweb.core.librdiff import RdiffTime

# Define the logger
logger = logging.getLogger(__name__)

Page = namedtuple('Page', ['id', 'label', 'url_for', 'icon', 'active_page'], defaults=[None, None])
Page.__hash__ = lambda x: x.id.__hash__()
Page.__eq__ = lambda self, other: self and other and isinstance(other, Page) and self.id == other.id


class PageRegistry(dict):
    """
    Page registry built manually.
    """

    def __getitem__(self, id):
        return super().__getitem__(id)

    def get(self, id):
        if id.endswith('.html'):
            id = id[:-5]
        return super().get(id)

    def get_label(self, page_id):
        if page_id in self:
            return self[page_id].label
        return page_id

    def get_repo_nav_items(self):
        repo_pages = ['browse', 'settings', 'graphs', 'stats', 'logs']
        return {id: page for id, page in self.items() if id in repo_pages}

    def get_graphs_nav_items(self):
        return {id: page for id, page in self.items() if id.startswith('graphs_') and page.active_page is None}

    def get_admin_nav_items(self):
        return {id: page for id, page in self.items() if id.startswith('admin_') and page.active_page is None}

    def get_prefs_nav_items(self):
        return {id: page for id, page in self.items() if id.startswith('prefs_') and page.active_page is None}


# TODO Consider using function decorator to build the registry
_pages = [
    Page('home', _('Home'), '/', 'fa-home'),
    # Repo
    Page('browse', _('Files'), 'browse', 'fa-files-o'),
    Page('history', _('File History'), 'history', None, 'browse'),
    Page('restore', _('Restore'), 'restore', None, 'browse'),
    Page('settings', _('Settings'), 'settings', 'fa-sliders'),
    Page('graphs', _('Graphs'), 'graphs', 'fa-area-chart'),
    Page('stats', _('Snapshot Changes'), 'stats', 'fa-list-alt'),
    Page('logs', _('Logs'), 'logs', 'fa-file-text-o'),
    # Graphs
    Page('graphs_activities', _('Activities'), 'graphs/activities/'),
    Page('graphs_files', _('File count'), 'graphs/files/'),
    Page('graphs_sizes', _('Size'), 'graphs/sizes/'),
    Page('graphs_times', _('Elapsed Time'), 'graphs/times/'),
    Page('graphs_errors', _('Errors'), 'graphs/errors/'),
    # Admin
    Page('admin_users', _('Users'), 'admin/users', 'fa-users'),
    Page('admin_user_edit', _('Edit User'), 'admin/users/edit', None, 'admin_users'),
    Page('admin_user_new', _('Add User'), 'admin/users/new', None, 'admin_users'),
    Page('admin_repos', _('Repositories'), 'admin/repos', 'fa-th'),
    Page('admin_session', _('User Sessions'), 'admin/session', 'fa-id-badge'),
    Page('admin_activity', _('Activity'), 'admin/activity', 'fa-list-alt'),
    Page('admin_logs', _('System Logs'), 'admin/logs', 'fa-file-text-o'),
    Page('admin_sysinfo', _('System Info'), 'admin/sysinfo', 'fa-info-circle'),
    # User Preferences
    Page('prefs_general', _('Account Settings'), 'prefs/general'),
    Page('prefs_notification', _('Notifications & Report'), 'prefs/notification'),
    Page('prefs_sshkeys', _('SSH keys'), 'prefs/sshkeys'),
    Page('prefs_tokens', _('Access Token'), 'prefs/tokens'),
    Page('prefs_mfa', _('Two-Factor Authentication'), 'prefs/mfa'),
    Page('prefs_session', _('Active Sessions'), 'prefs/session', 'fa-id-badge'),
]

page_registry = PageRegistry({page.id: page for page in _pages})


# TODO Remove the following function.
def validate(value, message=None):
    """Raise HTTP error if value is not true."""
    if not value:
        raise cherrypy.HTTPError(400, message)


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
    except ValueError:
        pass
    try:
        return RdiffTime(value)
    except ValueError:
        pass
    raise cherrypy.HTTPError(400, f"Invalid date: {value}")
