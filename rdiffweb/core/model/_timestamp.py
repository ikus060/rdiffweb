# -*- coding: utf-8 -*-
# udb, A web interface to manage IT network
# Copyright (C) 2023 IKUS Software inc.
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
from datetime import datetime, timezone

from sqlalchemy import TypeDecorator
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql.functions import GenericFunction
from sqlalchemy.sql.sqltypes import DateTime


class epoch(GenericFunction):
    name = "epoch"
    inherit_cache = True


@compiles(epoch, "postgresql")
def _render_to_tsvector_of_pg(element, compiler, **kw):
    """
    On Postgresql, use extract(epoch FROM ...)
    """
    return "extract(epoch FROM %s)" % compiler.process(element.clauses, **kw)


@compiles(epoch, 'sqlite')
def _render_to_tsvector_of_sqlite(element, compiler, **kw):
    """
    On SQLite, use STRFTIME('%s', ...) function.
    """
    return "STRFTIME('%%s', %s)" % compiler.process(element.clauses, **kw)


class Timestamp(TypeDecorator):
    """
    Adjust datetime to store timezone info and restore timezone
    info whether or not the datetime object as it.
    """

    cache_ok = True
    impl = DateTime
    LOCAL_TIMEZONE = datetime.utcnow().astimezone().tzinfo

    def process_bind_param(self, value: datetime, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            value = value.astimezone(self.LOCAL_TIMEZONE)
        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
