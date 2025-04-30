# udb, A web interface to manage IT network
# Copyright (C) 2025 IKUS Software inc.
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

import sqlalchemy

# SQLAchemy before v1.4 doesn't provide regexp implementation.
# Let provide a simple implementation.
if sqlalchemy.__version__ < "1.4":

    import re

    from sqlalchemy import event, literal
    from sqlalchemy.engine import Engine
    from sqlalchemy.ext.compiler import compiles
    from sqlalchemy.sql import ColumnElement
    from sqlalchemy.sql.expression import BinaryExpression
    from sqlalchemy.types import Boolean

    class RegexpMatch(BinaryExpression):
        def __init__(self, left, right):
            if isinstance(right, str):
                right = literal(right)
            super().__init__(left, right, operator="REGEXP", type_=Boolean())

    def regexp_match(self, pattern):
        return RegexpMatch(self, pattern)

    ColumnElement.regexp_match = regexp_match

    @compiles(RegexpMatch, 'postgresql')
    def _compile_regexp_pg(element, compiler, **kw):
        """
        Regexp implementation for postgresql using "~" operator.
        """
        left = compiler.process(element.left, **kw)
        right = compiler.process(element.right, **kw)
        return f"{left} ~ {right}"

    def regexp(a, b):
        """
        Regexp implementation for SQLite.
        """
        return re.search(a, b) is not None

    @event.listens_for(Engine, "connect")
    def _register_sqlite_regexp_functions(dbapi_con, unused):
        """
        On SQLite engine, register regexp function .
        """
        if 'sqlite' in repr(dbapi_con):
            dbapi_con.create_function("regexp", 2, regexp)
