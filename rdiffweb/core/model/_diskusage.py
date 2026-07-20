# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2026 rdiffweb contributors
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

import cherrypy
import cherrypy_foundation.plugins.db  # noqa
from sqlalchemy import Column, ForeignKey, Index, Integer, LargeBinary
from sqlalchemy.orm import relationship, validates
from sqlalchemy.sql.functions import func

from ._timestamp import Timestamp

Base = cherrypy.db.base


class DiskUsage(Base):
    __tablename__ = 'diskusages'

    repoid = Column('RepoID', Integer, ForeignKey("repos.RepoID", ondelete="CASCADE"), nullable=False, primary_key=True)
    repo = relationship('RepoObject', lazy=True)
    parent_path = Column('ParentPath', LargeBinary, nullable=False, server_default=None, primary_key=True)
    child_name = Column('ChildName', LargeBinary, nullable=False, server_default=None, primary_key=True)
    mirror_size = Column('MirrorSize', Integer, nullable=True, server_default=None)
    increments_size = Column('IncrementsSize', Integer, nullable=True, server_default=None)
    last_updated = Column('LastUpdated', Timestamp, nullable=False, default=func.now(), onupdate=func.now())

    @validates('child_name')
    def _validate_child_name(self, key, value):
        if value and b'/' in value:
            raise ValueError("child_name must not contain '/'")
        return value

    @property
    def logical_path(self):
        if not self.parent_path:
            return self.child_name
        return self.parent_path + b'/' + self.child_name

    def __repr__(self):
        return f"DiskUsage({self.repoid!r}, {self.logical_path!r}, mirror_size={self.mirror_size!r}, increments_size={self.increments_size!r})"

    @classmethod
    def attach_disk_usage(cls, repo_objs):
        """
        Enrich a list of RepoObject with mirror_size/increments_size/total_size.
        """
        ids = [r.id for r in repo_objs]
        if not ids:
            return repo_objs

        usage_by_repoid = {
            repoid: (mirror_size or 0, increments_size or 0)
            for repoid, mirror_size, increments_size in (
                DiskUsage.query.with_entities(DiskUsage.repoid, DiskUsage.mirror_size, DiskUsage.increments_size)
                .filter(
                    DiskUsage.repoid.in_(ids),
                    DiskUsage.parent_path == b'',
                    DiskUsage.child_name == b'.',
                )
                .all()
            )
        }

        for repo in repo_objs:
            mirror_size, increments_size = usage_by_repoid.get(repo.id, (0, 0))
            repo.mirror_size = mirror_size
            repo.increments_size = increments_size
            if mirror_size or increments_size:
                repo.total_size = mirror_size + increments_size
            elif repo.session_statistics:
                repo.total_size = repo.session_statistics[-1].sourcefilesize
            else:
                repo.total_size = 0

        return repo_objs


diskusage_parentpath_index = Index(
    'diskusage_parentpath_index', DiskUsage.parent_path, DiskUsage.child_name, DiskUsage.repoid
)
