# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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

import unittest

import cherrypy

from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import RepoObject, UserObject
from rdiffweb.core.rdw_templating import _ParentEntry, attrib, do_format_lastupdated, list_parents, url_for
from rdiffweb.test import WebCase


class TemplateManagerTest(unittest.TestCase):
    def test_attrib(self):
        # Single value
        self.assertEqual('id="row"', attrib(id='row'))
        # Single value with quote
        self.assertEqual('id="val&lt;ue&quot;with&quot;qu&gt;ot&amp;e"', attrib(id='val<ue"with"qu>ot&e'))
        # Multi attribute
        self.assertEqual('id="row" type="table"', attrib(type='table', id='row'))
        # Attribute with list
        self.assertEqual('type="table container"', attrib(type=['table', 'container']))
        # Attribute with class
        self.assertEqual('class="table container"', attrib(**{'class': ['table', 'container']}))
        # Boolean expressions
        self.assertEqual('id="active"', attrib(id=[False, 'active', False]))
        self.assertEqual('data="coucou" id="active"', attrib(type=False, id=[False, 'active', False], data='coucou'))
        active = True
        self.assertEqual('id="active"', attrib(id=[active and 'active']))
        active = False
        self.assertEqual('', attrib(id=[active and 'active']))

        # With True
        self.assertEqual('selected', attrib(selected=True))

        # Bytes
        self.assertEqual('selected="text"', attrib(selected=b'text'))

        # Newstr
        self.assertEqual('selected="text"', attrib(selected=str('text')))

        self.assertEqual('value="0"', attrib(value=0))

    def test_url_for(self):
        # Check backward compatibility
        self.assertEqual(cherrypy.server.base() + '/', url_for('/'))
        self.assertEqual(cherrypy.server.base() + '/browse', url_for('browse'))
        self.assertEqual(cherrypy.server.base() + '/browse/testcases', url_for('browse', b'testcases'))
        self.assertEqual(
            cherrypy.server.base() + '/browse/testcases/Revisions', url_for('browse', b'testcases', b'Revisions')
        )
        self.assertEqual(
            cherrypy.server.base() + '/restore/testcases/Revisions?date=1454448640',
            url_for('restore', b'testcases', b'Revisions', date=1454448640),
        )
        self.assertEqual(
            cherrypy.server.base() + '/restore/testcases/Revisions?date=1454448640&kind=tar.gz',
            url_for('restore', b'testcases', b'Revisions', date=1454448640, kind='tar.gz'),
        )
        self.assertEqual(
            cherrypy.server.base() + '/browse/testcases/R%C3%A9pertoire',
            url_for('browse', b'testcases', b'R\xc3\xa9pertoire'),
        )
        # Check if multi path is supported.
        self.assertEqual(cherrypy.server.base() + '/admin/logs', url_for('admin/logs'))
        self.assertEqual(cherrypy.server.base() + '/admin/logs/backup.log', url_for('admin/logs', 'backup.log'))

    def test_do_format_lastupdated(self):
        self.assertEqual('23 seconds ago', do_format_lastupdated(1591978823, now=1591978846))
        self.assertEqual('23 seconds ago', do_format_lastupdated(RdiffTime(value=1591978823), now=1591978846))
        self.assertEqual('8 minutes ago', do_format_lastupdated(RdiffTime(value=1591978324), now=1591978846))
        self.assertEqual('2 hours ago', do_format_lastupdated(RdiffTime(value=1591971646), now=1591978846))
        self.assertEqual('2 days ago', do_format_lastupdated(RdiffTime(value=1591805524), now=1591978846))
        self.assertEqual('4 weeks ago', do_format_lastupdated(RdiffTime(value=1589127124), now=1591978846))
        self.assertEqual('5 months ago', do_format_lastupdated(RdiffTime(value=1578672724), now=1591978846))
        self.assertEqual('4 years ago', do_format_lastupdated(RdiffTime(value=1452442324), now=1591978846))


class ListParentsTest(WebCase):
    def test_list_parents_with_root_dir(self):
        repo, path = RepoObject.get_repo_path(b'admin/testcases', as_user=UserObject.get_user('admin'))
        self.assertEqual(list_parents(repo, path), [_ParentEntry(path=b'', display_name='testcases')])

    def test_list_parents_with_root_subdir(self):
        repo, path = RepoObject.get_repo_path(b'admin/testcases/Revisions', as_user=UserObject.get_user('admin'))
        self.assertEqual(
            list_parents(repo, path),
            [
                _ParentEntry(path=b'', display_name='testcases'),
                _ParentEntry(path=b'Revisions', display_name='Revisions'),
            ],
        )


class UrlForTest(WebCase):
    @property
    def repo_obj(self):
        user = UserObject.get_user('admin')
        return RepoObject.query.filter(RepoObject.user == user, RepoObject.repopath == self.REPO).first()

    def test_url_for_absolute_path(self):
        self.assertEqual(cherrypy.server.base() + '/static/js/jquery.min.js', url_for('/static/js/jquery.min.js'))

    def test_url_for_browse(self):
        """Check creation of url"""
        self.assertEqual(cherrypy.server.base() + '/browse/admin/testcases', url_for('browse', self.repo_obj))
        self.assertEqual(
            cherrypy.server.base() + '/browse/admin/testcases/Revisions', url_for('browse', self.repo_obj, b'Revisions')
        )
        self.assertEqual(
            cherrypy.server.base() + '/browse/admin/testcases/Revisions?restore=True',
            url_for('browse', self.repo_obj, b'Revisions', restore=True),
        )
        self.assertEqual(
            cherrypy.server.base()
            + '/browse/admin/testcases/R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial',
            url_for(
                'browse',
                self.repo_obj,
                b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial',
            ),
        )

    def test_url_for_graphs(self):
        self.assertEqual(
            cherrypy.server.base() + '/graphs/files/admin/testcases', url_for('graphs', 'files', self.repo_obj)
        )

    def test_url_for_history(self):
        """Check creation of url"""
        self.assertEqual(cherrypy.server.base() + '/history/admin/testcases', url_for('history', self.repo_obj))

    def test_url_for_restore(self):
        self.assertEqual(
            cherrypy.server.base() + '/restore/admin/testcases?date=1414967021',
            url_for('restore', self.repo_obj, date=RdiffTime(1414967021)),
        )
        self.assertEqual(
            cherrypy.server.base() + '/restore/admin/testcases?date=1414967021',
            url_for('restore', self.repo_obj, b'', date=RdiffTime(1414967021)),
        )
        self.assertEqual(
            cherrypy.server.base() + '/restore/admin/testcases?date=1414967021&kind=tar.gz',
            url_for('restore', self.repo_obj, b'', date=RdiffTime(1414967021), kind='tar.gz'),
        )
        self.assertEqual(
            cherrypy.server.base() + '/restore/admin/testcases/Revisions?date=1414967021',
            url_for('restore', self.repo_obj, b'Revisions', date=RdiffTime(1414967021)),
        )
        self.assertEqual(
            cherrypy.server.base()
            + '/restore/admin/testcases/R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial?date=1414967021',
            url_for(
                'restore',
                self.repo_obj,
                b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial',
                date=RdiffTime(1414967021),
            ),
        )

    def test_url_for_status(self):
        self.assertEqual(
            cherrypy.server.base() + '/status?date=1414967021', url_for('status', date=RdiffTime(1414967021))
        )
        self.assertEqual(
            cherrypy.server.base() + '/status/admin/testcases?date=1414967021',
            url_for('status', self.repo_obj, date=RdiffTime(1414967021)),
        )

    def test_url_for_with_none(self):
        self.assertEqual(cherrypy.server.base() + '/logs', url_for('logs', date=None))
