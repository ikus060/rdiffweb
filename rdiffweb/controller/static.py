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

from importlib.resources import files

import cherrypy
from cherrypy_foundation.components import StaticMiddleware
from cherrypy_foundation.tools.i18n import gettext as _
from cherrypy_foundation.tools.i18n import preferred_lang


@cherrypy.tools.auth(on=False)
@cherrypy.tools.i18n(on=False)
@cherrypy.tools.ratelimit(on=False)
@cherrypy.tools.secure_headers(on=False)
@cherrypy.tools.sessions(on=False)
class Static:

    components = StaticMiddleware()

    @cherrypy.expose
    @cherrypy.tools.staticdir(
        section="", match=r".*(\.js|\.css|\.png|\.woff|\.woff2)$", dir=files('rdiffweb') / 'static'
    )
    def default(self, *args, **kwargs):
        """This entry point is used to serve content of /static/ folder."""
        raise cherrypy.HTTPError(400)

    @cherrypy.expose
    @cherrypy.tools.allow(methods=['GET'])
    @cherrypy.tools.json_out()
    def dt_language(self, lang, **kwargs):
        """Return datatable language file."""
        with preferred_lang(lang):
            return {
                "aria": {
                    "sortAscending": _('activate to sort column ascending'),
                    "sortDescending": _('activate to sort column descending'),
                },
                "info": _('Showing from _START_ to _END_ of _TOTAL_ total records'),
                "infoFiltered": _('(filtered from _MAX_ total records)'),
                "infoEmpty": _('No records available'),
                "processing": _('Loading...'),
                "rdiffweb": {
                    "null": _('undefined'),
                    "value": {
                        "mfa": {
                            "0": _('Disabled'),
                            "1": _('Enabled'),
                        },
                        "report_time_range": {
                            "0": _('Never'),
                            "1": _('Daily'),
                            "7": _('Weekly'),
                            "30": _('Monthly'),
                        },
                        "role": {
                            "0": _("Admin"),
                            "5": _("Maintainer"),
                            "10": _("User"),
                        },
                    },
                    "field": {
                        "_encoding_name": _('File Encoding'),
                        "_ignore_weekday": _('Excluded Days of the Week'),
                        "_keepdays": _('Retention Duration'),
                        "authorizedkeys": _('SSH Keys'),
                        "email": _('Email'),
                        "fullname": _('Fullname'),
                        "hash_password": _('Password'),
                        "lang": _('Preferred Language'),
                        "maxage": _('Inactivity Period'),
                        "mfa": _('Two-Factor Authentication'),
                        "notes": _('Description'),
                        "repo_objs": _('Repositories'),
                        "repopath": _('Display Name'),
                        "report_time_range": _('Send Backup report'),
                        "role": _('User Role'),
                        "tokens": _('Access Token'),
                        "user": _('Owner'),
                        "user_root": _('Root directory'),
                        "username": _('Username'),
                    },
                    "message_details": {
                        "user": {
                            "new": _('New user {model_summary} created by {author_username}'),
                            "deleted": _('User deleted by {author_username}'),
                            "dirty": _('Modified by {author_username}'),
                        },
                        "repo": {
                            "new": _('New repository {model_summary} created by {author_username}'),
                            "deleted": _('Repository deleted by {author_username}'),
                            "dirty": _('Modified by {author_username}'),
                        },
                    },
                },
                "search": _('Filter: '),
                "zeroRecords": _('List is empty'),
            }
