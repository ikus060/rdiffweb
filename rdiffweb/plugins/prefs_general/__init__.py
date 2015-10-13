#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 Patrik Dufresne Service Logiciel
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
import re

from rdiffweb.i18n import ugettext as _
from rdiffweb.rdw_plugin import IPreferencesPanelProvider
from rdiffweb.rdw_helpers import encode_s
from rdiffweb import rdw_spider_repos
from rdiffweb.core import RdiffError

"""
Created on May 16, 2015

@author: Patrik Dufresne
"""

PATTERN_EMAIL = re.compile(r'[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$')

# Define the logger
_logger = logging.getLogger(__name__)


class PrefsGeneralPanelProvider(IPreferencesPanelProvider):
    """
    Plugin to change user profile and password.
    """

    def get_prefs_panels(self):
        """
        Return a single page.
        """
        yield ('general', _('Profile'))

    def _handle_set_password(self, **kwargs):
        """
        Called when changing user password.
        """
        if 'current' not in kwargs:
            raise ValueError(_("current password is missing"))
        if 'new' not in kwargs:
            raise ValueError(_("new password is missing"))
        if 'confirm' not in kwargs:
            raise ValueError(_("confirmation password is missing"))

        # Check if confirmation is valid.
        if kwargs['new'] != kwargs['confirm']:
            return {'error': _("The new password and its confirmation does not matches.")}

        # Check if current database support it.
        user = self.app.currentuser.username
        store = self.app.userdb.find_user_store(user)
        if not store or not store.supports('set_password'):
            return {'error': _("Password changes is not supported.")}

        # Update user password
        _logger.info("updating user [%s] password", user)
        self.app.userdb.set_password(user, kwargs['new'], old_password=kwargs['current'])
        return {'success': _("Password updated successfully.")}

    def _handle_set_profile_info(self, **kwargs):
        """
        Called when changing user profile.
        """
        # Check data.
        if 'email' not in kwargs:
            raise ValueError(_("email is undefined"))

        # Check if email update is supported
        if not self.app.userdb.supports('set_email'):
            return {'error': _("Email update is not supported.")}

        # Parse the email value to extract a valid email. The following method
        # return an empty string if the email is not valid. This RFC also accept
        # local email address without '@'. So we add verification for '@'
        if not PATTERN_EMAIL.match(kwargs['email'].lower()):
            raise ValueError(_("invalid email"))

        # Update the user's email
        if not self.app.currentuser:
            raise RdiffError(_("invalid state"))

        username = self.app.currentuser.username
        email = kwargs['email']
        _logger.info("updating user [%s] email [%s]", username, email)
        self.app.userdb.set_email(username, kwargs['email'])

        return {'success': _("Profile updated successfully.")}

    def _handle_update_repos(self):
        """
        Called to refresh the user repos.
        """
        rdw_spider_repos.find_repos_for_user(self.app.currentuser.username, self.app.userdb)
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
                    _logger.info("unknown action: %s", action)
                    raise cherrypy.NotFound("Unknown action")
            except ValueError as e:
                params['error'] = unicode(e)
            except Exception as e:
                _logger.warn("unknown error processing action", exc_info=True)
                params['error'] = _("Unknown error")

        params.update({
            'email': self.app.currentuser.email,
            'supports_set_email': self.app.userdb.supports('set_email'),
            'supports_set_password': self.app.userdb.supports('set_password'),
        })
        return "prefs_general.html", params
