# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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


import encodings

import cherrypy
from markupsafe import Markup, escape
from wtforms.fields import SelectField, SelectMultipleField, SubmitField
from wtforms.widgets import html_params

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.dispatch import poppath
from rdiffweb.controller.filter_authorization import is_maintainer
from rdiffweb.controller.form import CherryForm
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject
from rdiffweb.tools.i18n import gettext_lazy as _


def normalize_encoding(value):
    codec = encodings.search_function(value.lower())
    if not codec:
        raise ValueError(_('invalid encoding %s') % value)
    return codec.name


class MaxAgeField(SelectField):
    def __init__(self, *args, **kwargs):
        super().__init__(
            *args,
            choices=[
                (0, _('Never')),
                (1, _('1 day')),
                (2, _('2 days')),
                (3, _('3 days')),
                (4, _('4 days')),
                (5, _('5 days')),
                (6, _('6 days')),
                (7, _('1 week')),
                (14, _('2 weeks')),
                (21, _('3 weeks')),
                (28, _('4 weeks')),
                (31, _('1 month')),
            ],
            coerce=int,
            **kwargs,
        )


class WeekdayField(SelectMultipleField):
    def __init__(self, label=None, **kwargs):
        choices = [
            (0, _('Monday')),
            (1, _('Tuesday')),
            (2, _('Wednesday')),
            (3, _('Thursday')),
            (4, _('Friday')),
            (5, _('Saturday')),
            (6, _('Sunday')),
        ]
        super().__init__(label, coerce=int, choices=choices, **kwargs)

    def widget(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        html = ['<div>']
        for val, label, selected in field.iter_choices():
            field_id = '%s_%s' % (field.id, val)
            html.append(
                '<input type="checkbox" %s /> <label for="%s">%s</label> '
                % (
                    html_params(
                        id=field_id,
                        name=field.name,
                        value=val,
                        checked=selected,
                    ),
                    field_id,
                    escape(label),
                )
            )
        html.append('</div>')
        return Markup(''.join(html))


class RepoSettingsForm(CherryForm):
    maxage = MaxAgeField(
        _('Inactivity Notification Period'),
        description=_(
            "The period refers to the duration of inactivity after which a notification is triggered and sent to the user. It determines the number of days of inactivity that must pass before the system generates a notification to inform the user about the lack of activity in the backup repository."
        ),
    )

    ignore_weekday = WeekdayField(
        _('Excluded Days of the Week'),
        description=_(
            'This field allows to select specific days of the week to exclude from considering as part of the inactivity period. By selecting the days to ignore, such as Saturday and Sunday, the system will not count the selected days when calculating the inactivity period for generating notifications.'
        ),
    )

    keepdays = SelectField(
        _('Data Retention Duration'),
        description=_(
            'The retention period determines how long the backup data will be stored in the repository before it is automatically deleted or purged. By adjusting this setting, you can specify the duration for which the backup data should be retained before being removed.'
        ),
        coerce=int,
        choices=[
            (-1, _("Forever")),
            (1, _("1 day")),
            (2, _("2 days")),
            (3, _("3 days")),
            (4, _("4 days")),
            (5, _("5 days")),
            (6, _("6 days")),
            (7, _("1 week")),
            (14, _("2 weeks")),
            (21, _("3 weeks")),
            (30, _("1 month")),
            (60, _("2 months")),
            (90, _("3 months")),
            (120, _("4 months")),
            (150, _("5 months")),
            (180, _("6 months")),
            (210, _("7 months")),
            (240, _("8 months")),
            (270, _("9 months")),
            (300, _("10 months")),
            (330, _("11 months")),
            (365, _("1 year")),
            (730, _("2 years")),
            (1095, _("3 years")),
            (1460, _("4 years")),
            (1825, _("5 years")),
        ],
    )
    encoding = SelectField(
        _('Display Encoding'),
        description=_(
            "This setting relates to the representation or format in which the backup repository is displayed. It may include considerations such as language or character encoding to match your specific locale. By adjusting this setting, you can ensure that the repository's content is displayed correctly and in a manner that is suitable for your locale."
        ),
        coerce=normalize_encoding,
        choices=[
            ('utf-8', 'UTF-8 (all languages)'),
            ('ascii', 'US-ASCII (English)'),
            ('cp037', 'IBM037, IBM039 (English)'),
            ('cp424', 'EBCDIC-CP-HE, IBM424 (Hebrew)'),
            ('cp437', 'IBM437 (English)'),
            ('cp500', 'IBM500 (Western Europe)'),
            ('cp737', 'CP737 (Greek)'),
            ('cp775', 'IBM775 (Baltic languages)'),
            ('cp850', 'IBM850 (Western Europe)'),
            ('cp852', 'IBM852 (Central and Eastern Europe)'),
            ('cp855', 'IBM855 (Russian)'),
            ('cp856', 'CP856 (Hebrew)'),
            ('cp857', 'IBM857 (Turkish)'),
            ('cp860', 'IBM860 (Portuguese)'),
            ('cp861', 'CP-IS, IBM861 (Icelandic)'),
            ('cp862', 'IBM862 (Hebrew)'),
            ('cp863', 'IBM863 (Canadian)'),
            ('cp864', 'IBM864 (Arabic)'),
            ('cp865', 'IBM865 (Danish, Norwegian)'),
            ('cp869', 'IBM869 (Greek)'),
            ('cp874', 'CP874 (Thai)'),
            ('cp875', 'CP875 (Greek)'),
            ('cp1006', 'CP1006 (Urdu)'),
            ('cp1026', 'IBM1026 (Turkish)'),
            ('cp1140', 'IBM1140 (Western Europe)'),
            ('cp1250', 'Windows-1250 (Central and Eastern Europe)'),
            ('cp1251', 'Windows-1251 (Russian)'),
            ('cp1252', 'Windows-1252 (Western Europe)'),
            ('cp1253', 'Windows-1253 (Greek)'),
            ('cp1254', 'Windows-1254 (Turkish)'),
            ('cp1255', 'Windows-1255 (Hebrew)'),
            ('cp1256', 'Windows-1256 (Arabic)'),
            ('cp1257', 'windows-1257 (Baltic languages)'),
            ('cp1258', 'Windows-1258 (Vietnamese)'),
            ('latin_1', 'ISO-8859-1, Latin1 (West Europe)'),
            ('iso8859_2', 'ISO-8859-2, Latin2 (Central and Eastern Europe)'),
            ('iso8859_3', 'ISO-8859-3, Latin3 (Esperanto, Maltese)'),
            ('iso8859_4', 'ISO-8859-4, Latin4 (Baltic languagues)'),
            ('iso8859_5', 'ISO-8859-5 (Russian)'),
            ('iso8859_6', 'ISO-8859-6 (Arabic)'),
            ('iso8859_7', 'ISO-8859-7 (Greek)'),
            ('iso8859_8', 'ISO-8859-8 (Hebrew)'),
            ('iso8859_9', 'ISO-8859-9, Latin5 (Turkish)'),
            ('iso8859_10', 'ISO-8859-10, Latin6 (Nordic languages)'),
            ('iso8859_13', 'ISO-8859-13 (Baltic languages)'),
            ('iso8859_14', 'ISO-8859-14, Latin8 (Celtic languages)'),
            ('iso8859_15', 'ISO-8859-15 (Western Europe)'),
            ('koi8_r', 'KOI8-r (Russian)'),
            ('koi8_u', 'KOI8-u (Ukrainian)'),
            ('mac_cyrillic', 'Mac-Cyrillic  (Russian)'),
            ('mac_greek', 'Mac-Greek (Greek)'),
            ('mac_iceland', 'Mac-Iceland (Icelandic)'),
            ('mac_latin2', 'Mac-Latin (Central and Eastern Europe)'),
            ('mac_roman', 'Mac-Roman (Western Europe)'),
            ('mac_turkish', 'Mac-Turkish (Turkish)'),
            ('utf_16', 'UTF16 (all languages)'),
            ('utf_16_be', 'UTF-16BE (all languages)'),
            ('utf_16_le', 'UTF-16LE (all languages)'),
            ('utf_7', 'UTF-7 (all languages)'),
        ],
    )
    submit = SubmitField(_('Save changes'))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Make keepdays readonly if not a maintainer
        if not cherrypy.serving.request.currentuser.is_maintainer:
            self.keepdays.render_kw['readonly'] = True
        # Disable choices validation for WTForms>=2.2
        self.encoding.validate_choice = False

    def populate_obj(self, repo_obj):
        # Only maintainer is allowed to change keepdays
        if self.keepdays.data != repo_obj.keepdays:
            is_maintainer()

        try:
            super().populate_obj(repo_obj)
            flash(_("Settings modified successfully."), level='success')
            return True
        except Exception as e:
            repo_obj.rollback()
            flash(str(e), level='warning')
            return False


@poppath()
class SettingsPage(Controller):
    @cherrypy.expose
    @cherrypy.tools.errors(
        error_table={
            DoesNotExistError: 404,
            AccessDeniedError: 403,
        }
    )
    def default(self, path=b"", **kwargs):
        repo_obj = RepoObject.get_repo(path)
        form = RepoSettingsForm(obj=repo_obj)
        if form.is_submitted():
            if form.validate():
                if form.populate_obj(repo_obj):
                    raise cherrypy.HTTPRedirect("")
            else:
                flash(form.error_message, level='error')
        return self._compile_template("settings.html", form=form, repo=repo_obj)
