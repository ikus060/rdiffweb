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

import time

import sqlalchemy
from sqlalchemy import select, text
from sqlalchemy.sql import ddl

# With SQLAlchemy<=1.4, the select() function signature is different
if sqlalchemy.__version__.startswith("1.3"):

    def select(*columns, orig_select=select):
        return orig_select(columns=columns)


"""
Collection of utility function to update database schema.
"""


def commit(conn):
    # SQLAlchmey 1.4 Commit current transaction and open a new one.
    if getattr(conn, '_transaction', None):
        conn._transaction.commit()


def is_sqlite(conn):
    """
    Check if connected to SQLite database
    """
    return 'SQLite' in conn.engine.dialect.__class__.__name__


def column_exists(conn, column):
    """
    Check if column exists.
    """
    table_name = column.table.fullname
    column_name = column.name
    if is_sqlite(conn):
        sql = 'SELECT %s FROM "%s"' % (column_name, table_name)
        try:
            conn.execute(text(sql)).first()
            return True
        except Exception:
            return False
    else:
        sql = "SELECT 1 FROM information_schema.columns WHERE table_name='%s' and column_name='%s'" % (
            table_name,
            column_name,
        )
        row = conn.execute(text(sql)).first()
        return row is not None


def column_add(conn, column):
    """
    Create column if missing.
    """
    table_name = column.table.fullname
    # Compile string representation of the column creation.
    conn.execute(text('ALTER TABLE "%s" ADD COLUMN %s' % (table_name, ddl.CreateColumn(column).compile(conn.engine))))
    return True


def recreate_table(conn, table, query):
    table_name = table.fullname
    temp_table = '%s_temp_%s' % (table_name, int(time.time()))
    # Create new table
    create_table_sql = str(ddl.CreateTable(table).compile(conn.engine)).replace(
        'CREATE TABLE %s' % table_name, 'CREATE TABLE %s' % temp_table
    )
    conn.execute(text(create_table_sql))
    if is_sqlite(conn):
        conn.execute(text("PRAGMA defer_foreign_keys = '1'"))
    # Copy data to new table using the provided query.
    conn.execute(
        text(
            'INSERT INTO %s (%s) %s'
            % (temp_table, ','.join([c.name for c in query.columns]), query.compile(conn.engine))
        )
    )
    # Drop previous table
    conn.execute(ddl.DropTable(table))
    # Rename table.
    conn.execute(text('ALTER TABLE %s RENAME TO %s' % (temp_table, table_name)))
    if is_sqlite(conn):
        conn.execute(text("PRAGMA defer_foreign_keys = '0'"))


def constraint_exists(conn, constraint):
    """
    Get detail information baout the table.
    """
    table_name = constraint.table.name
    constraint_name = constraint.name
    if is_sqlite(conn):
        try:
            row = conn.execute(
                text("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = '%s'" % table_name)
            ).first()
            return ('CONSTRAINT %s' % constraint_name) in row.sql
        except Exception:
            return False
    else:
        sql = "SELECT COUNT(*) FROM pg_catalog.pg_constraint WHERE conname='%s'" % (constraint_name)
        data = conn.execute(text(sql)).first()
        return data[0] >= 1


def constraint_add(conn, constraint):
    """
    Add given constraint to database schema.
    """
    if is_sqlite(conn):
        # On SQLite we need to recreate table.
        columns = [c for c in constraint.table.columns if not c.computed]
        recreate_table(conn, constraint.table, select(*columns))
    else:
        # On postgresql we use alter table.
        conn.execute(text(str(ddl.AddConstraint(constraint).compile(conn.engine))))


def index_exists(conn, index_name):
    """
    Check if the given index exists.
    """
    assert index_name
    if is_sqlite(conn):
        row = conn.execute(text("SELECT 1 FROM sqlite_master WHERE type='index' and name = '%s'" % index_name)).first()
    else:
        row = conn.execute(
            text(
                "SELECT 1 FROM pg_index, pg_class WHERE pg_class.oid = pg_index.indexrelid and relname = '%s'"
                % index_name
            )
        ).first()
    return row is not None


def index_drop(conn, index_name):
    """
    Drop given constraints.
    """
    assert index_name
    conn.execute(text("DROP INDEX %s" % index_name))


def table_exists(conn, table):
    """
    Check if given table exists.
    """
    assert table is not None and table.name
    if is_sqlite(conn):
        row = conn.execute(text("SELECT 1 FROM sqlite_master WHERE type='table' AND name = '%s'" % table.name)).first()
    else:
        row = conn.execute(text("SELECT 1 FROM information_schema.tables WHERE table_name = '%s'" % table.name)).first()
    return row is not None


def trigger_on_update(conn, name, before_or_after='AFTER', columns=[], sql=None):
    """
    Create a simple trigger.
    sql could be an sql statement or an array of sql statement.
    """
    assert ' ' not in name
    assert before_or_after in ['BEFORE', 'AFTER'], 'expect BEFORE or AFTER'
    assert columns, 'at least one column is required'
    table_name = columns[0].table.name
    column_names = ','.join([column.name for column in columns])
    update_condition = ' OR '.join(['new.%s <> old.%s' % (column.name, column.name) for column in columns])

    # Compile the statements
    if not isinstance(sql, list):
        sql = [sql]
    sql_body = ';\n'.join(str(stmt.compile(conn.engine, compile_kwargs={"literal_binds": True})) for stmt in sql)

    if is_sqlite(conn):
        # SQLite doesn't support multiple event type, so we need to create individual trigger with different name
        conn.execute(text(f"DROP TRIGGER IF EXISTS '{name}'"))
        conn.execute(
            text(
                f"CREATE TRIGGER '{name}' {before_or_after} UPDATE OF {column_names} ON '{table_name}' FOR EACH ROW WHEN {update_condition} BEGIN {sql_body}; END"
            )
        )
    else:
        # Postgresql required the creation of a function to be executed as a trigger.
        conn.execute(
            text(
                f'CREATE OR REPLACE FUNCTION {name}_func() RETURNS TRIGGER LANGUAGE PLPGSQL AS $$ BEGIN\n'
                f'IF {update_condition} THEN\n'
                f'{sql_body};\n'
                f'END IF;\n'
                f'RETURN NEW;\n'
                f'END $$'
            )
        )
        # Postgresql support multiple event. build the event string.
        conn.execute(text(f'DROP TRIGGER IF EXISTS "{name}" ON "{table_name}" CASCADE'))
        conn.execute(
            text(
                f'CREATE TRIGGER "{name}" {before_or_after} UPDATE OF {column_names} ON "{table_name}" FOR EACH ROW EXECUTE PROCEDURE {name}_func();'
            )
        )
