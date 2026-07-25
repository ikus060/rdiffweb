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

import cherrypy

import rdiffweb.test
from rdiffweb.core.model import DiskUsage, RepoObject, UserObject


class DiskUsageTest(rdiffweb.test.WebCase):
    default_config = {}

    def test_check_schedule(self):
        # Given the application is started
        # Then jobs should be schedule
        self.assertEqual(1, len([job for job in cherrypy.scheduler.get_jobs() if job.name.endswith('_disk_usage_job')]))

    def test_disk_usage_job(self):
        # Given a user with repos
        userobj = UserObject.get_user(self.USERNAME)
        self.assertTrue(userobj.repo_objs)
        self.assertEqual(0, DiskUsage.query.count())
        cherrypy.db.session.commit()
        # When starting disk usage job
        cherrypy.disk_usage._disk_usage_job()
        # Then disk usage table get populated
        self.assertGreater(DiskUsage.query.count(), 1)
        # Then listing folder return disk usage.
        repo = RepoObject.query.filter(RepoObject.repopath == self.REPO).first()
        entries = repo.listdir(b'/')
        self.assertEqual(
            {e.path: (e.mirror_size, e.increments_size) for e in entries if e.isdir},
            {
                b'Char ;059059090 to quote': (None, 8192),
                b'Char ;059090 to quote': (20480, 8192),
                b'Char ;090 to quote': (None, 8192),
                b'DIR\xef\xbf\xbd': (4096, 8192),
                b'Revisions': (4096, 12288),
                b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial': (
                    16384,
                    8192,
                ),
                b'R\xc3\xa9pertoire Existant': (0, 24576),
                b'R\xc3\xa9pertoire Supprim\xc3\xa9': (None, 20480),
                b'Subdirectory': (4096, 0),
                b'SymlinkToSubdirectory': (None, None),
                b'test\\test': (4096, 8192),
            },
        )

    def test_attach_disk_usage(self):
        # Given a user with repos
        userobj = UserObject.get_user(self.USERNAME)
        self.assertTrue(userobj.repo_objs)
        self.assertEqual(0, DiskUsage.query.count())
        cherrypy.db.session.commit()
        # Given disk usage get calculated
        cherrypy.disk_usage._disk_usage_job()
        # Query querying repo with diskusages.
        repo_objs = RepoObject.query.order_by(RepoObject.repopath).all()
        repo_objs = DiskUsage.attach_disk_usage(repo_objs)
        # Then disk usage get attached.
        self.assertEqual(57344, repo_objs[0].total_size)
        self.assertEqual(57344, repo_objs[0].mirror_size)
        self.assertEqual(0, repo_objs[0].increments_size)
        self.assertEqual(3854336, repo_objs[1].total_size)
        self.assertEqual(3702784, repo_objs[1].mirror_size)
        self.assertEqual(151552, repo_objs[1].increments_size)
