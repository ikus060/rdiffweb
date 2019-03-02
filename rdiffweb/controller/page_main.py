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

from rdiffweb.controller import Controller

import cherrypy


class MainPage(Controller):

    def _is_submit(self):
        """
        Check if the cherrypy request is a POST.
        """
        return cherrypy.request.method == "POST"

    def _compile_template(self, template_name, **kwargs):
        """
        Used to generate a standard HTML page using the given template.
        This method should be used by subclasses to provide default template
        value.
        """
        loc = cherrypy.response.i18n.locale
        parms = {
            "lang": loc.language,
            "version": self.app.get_version(),
            "extra_head_templates": [],
        }
        if self.app.currentuser:
            parms.update({
                "is_login": False,
                'username': self.app.currentuser.username,
                'is_admin': self.app.currentuser.is_admin,
            })

        # Append custom branding
        if hasattr(self.app.root, "header_logo"):
            parms["header_logo"] = '/header_logo'
        header_name = self.app.cfg.get_config("HeaderName")
        if header_name:
            parms["header_name"] = header_name

        # Append template parameters.
        parms.update(kwargs)

        return self.app.templates.compile_template(template_name, **parms)
