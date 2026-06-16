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

from sqlalchemy import event
from sqlalchemy.engine import Engine

from ._diskusage import DiskUsage  # noqa
from ._message import Message  # noqa
from ._repo import RepoObject  # noqa
from ._session import SessionObject  # noqa
from ._sshkey import SshKey, sshkey_fingerprint_index  # noqa
from ._token import Token  # noqa
from ._user import UserObject, user_username_index  # noqa


@event.listens_for(Engine, 'connect')
def _on_sqlite_connect(connection, connection_record):
    if 'sqlite3' in str(connection.__class__):
        # NORMAL skips fdatasync on every commit
        # Still safe - only risks losing the last transaction on power loss
        cursor = connection.cursor()
        cursor.execute('PRAGMA synchronous=NORMAL;')
        cursor.close()
