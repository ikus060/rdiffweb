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

import cherrypy
from sqlalchemy.exc import IntegrityError
from wtforms.validators import ValidationError

from rdiffweb.tools.i18n import gettext_lazy as _

from .form import CherryForm

logger = logging.getLogger(__name__)

Session = cherrypy.db.get_session()


class DbForm(CherryForm):
    """
    Special form to handle saving form to database.
    """

    def save_to_db(self, obj):

        form_errors = self.form_errors if hasattr(self, 'form_errors') else self.errors.setdefault(None, [])
        try:
            self.populate_obj(obj)
            Session.commit()
            return True
        except (ValueError, ValidationError) as e:
            Session.rollback()
            form_errors.append(str(e))
            return False
        except IntegrityError as e:
            Session.rollback()
            if e.constraint and e.constraint.info and 'error_message' in e.constraint.info:
                error_message = e.constraint.info['error_message']
                form_errors.append(error_message)
            else:
                form_errors.append(_("A database error occurred. Please check your input."))
                logger.error("database error occurred", exc_info=1)
            return False
        except Exception:
            Session.rollback()
            logger.exception("unexpected error occurred while saving data", exc_info=1)
            form_errors.append(_("An unexpected error occurred while saving your data."))
            return False
