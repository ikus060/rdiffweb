# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 Patrik Dufresne Service Logiciel
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
"""
Default preference page to show general user information. It allows user
to change password ans refresh it's repository view.
"""

import logging
from rdiffweb.controller import Controller
from rdiffweb.core import RdiffError, RdiffWarning
from rdiffweb.core.i18n import ugettext as _
import re

import cherrypy

PATTERN_EMAIL = re.compile(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$')

# Define the logger
_logger = logging.getLogger(__name__)


class PrefsGeneralPanelProvider(Controller):
    """
    Plugin to change user profile and password.
    """

    panel_id = 'general'

    panel_name = _('Profile')

    def _handle_set_password(self, **kwargs):
        """
        Called when changing user password.
        """
        if 'current' not in kwargs or not kwargs['current']:
            raise RdiffWarning(_("Current password is missing."))
        if 'new' not in kwargs or not kwargs['new']:
            raise RdiffWarning(_("New password is missing."))
        if 'confirm' not in kwargs or not kwargs['confirm']:
            raise RdiffWarning(_("Confirmation password is missing."))

        # Check if confirmation is valid.
        if kwargs['new'] != kwargs['confirm']:
            return {'error': _("The new password and its confirmation do not match.")}

        # Update user password
        try:
            self.app.currentuser.set_password(kwargs['new'], old_password=kwargs['current'])
            return {'success': _("Password updated successfully.")}
        except ValueError as e:
            return {'warning': str(e)}

    def _handle_set_profile_info(self, **kwargs):
        """
        Called when changing user profile.
        """
        # Check data.
        if 'email' not in kwargs:
            raise RdiffWarning(_("Email is undefined."))

        # Parse the email value to extract a valid email. The following method
        # return an empty string if the email is not valid. This RFC also accept
        # local email address without '@'. So we add verification for '@'
        if not PATTERN_EMAIL.match(kwargs['email'].lower()):
            raise RdiffWarning(_("Invalid email."))

        # Update the user's email
        assert self.app.currentuser
        username = self.app.currentuser.username
        email = kwargs['email']
        _logger.info("updating user [%s] email [%s]", username, email)
        self.app.currentuser.email = kwargs['email']

        return {'success': _("Profile updated successfully.")}

    def _handle_update_repos(self):
        """
        Called to refresh the user repos.
        """
        self.app.currentuser.update_repos()
        return {'success': _("Repositories successfully updated.")}

    def render_prefs_panel(self, panelid, **kwargs):  # @UnusedVariable
        # Process the parameters.
        params = dict()
        action = kwargs.get('action')
        if action:
            try:
                if action == "set_profile_info":
                    params = self._handle_set_profile_info(**kwargs)
                elif action == "set_password":
                    params = self._handle_set_password(**kwargs)
                elif action == "update_repos":
                    params = self._handle_update_repos()
                else:
                    _logger.warning("unknown action: %s", action)
                    raise cherrypy.NotFound("Unknown action")
            except RdiffWarning as e:
                params['warning'] = str(e)
            except RdiffError as e:
                params['error'] = str(e)
            except Exception as e:
                _logger.warning("unknown error processing action", exc_info=True)
                params['error'] = _("Unknown error")

        params.update({
            'email': self.app.currentuser.email,
        })
        return "prefs_general.html", params
