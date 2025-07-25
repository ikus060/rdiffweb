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

# Define the logger

import logging
import os

import cherrypy
from wtforms.fields import StringField
from wtforms.validators import DataRequired, ValidationError

from rdiffweb.controller import Controller
from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject
from rdiffweb.core.rdw_templating import url_for
from rdiffweb.tools.i18n import gettext_lazy as _

_logger = logging.getLogger(__name__)


def _delete_repo(repoid, path):
    repoobj = RepoObject.query.filter(RepoObject.repoid == repoid).one()
    repoobj.delete(path)
    repoobj.commit()


class DeleteRepoForm(CherryForm):
    confirm = StringField(_('Confirmation'), validators=[DataRequired()])

    def validate_confirm(self, field):
        if self.confirm.data != self.expected_confirm:
            raise ValidationError(_('Invalid value, must be: %s') % self.expected_confirm)


@cherrypy.tools.poppath()
class DeletePage(Controller):
    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    @cherrypy.tools.allow(methods=['POST'])
    def default(self, path, **kwargs):
        """
        Delete a repo, a file or folder history
        """
        # Check permissions on path/repo
        repo, path = RepoObject.get_repo_path(path)
        # Check if path exists with fstats
        path_obj = repo.fstat(path)
        # Check user's permissions
        is_maintainer()

        # validate form
        form = DeleteRepoForm()

        form.expected_confirm = repo.display_name if path_obj.isroot else path_obj.display_name
        if form.is_submitted():
            if form.validate():
                cherrypy.engine.publish('schedule_task', _delete_repo, repo.repoid, path)
                # Redirect to parent folder or to root if repo get deleted
                if path_obj.isroot:
                    raise cherrypy.HTTPRedirect(url_for('/'))
                else:
                    parent_path = repo.fstat(os.path.dirname(path_obj.path))
                    raise cherrypy.HTTPRedirect(url_for('browse', repo, parent_path))
            else:
                raise cherrypy.HTTPError(400, form.error_message)
