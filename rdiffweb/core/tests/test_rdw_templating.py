# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.rdw_templating import attrib, url_for, \
    do_format_lastupdated
from rdiffweb.test import AppTestCase


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
        self.assertEqual('/browse', url_for('browse'))
        self.assertEqual('/browse/testcases', url_for('browse', b'testcases'))
        self.assertEqual('/browse/testcases/Revisions', url_for('browse', b'testcases', b'Revisions'))
        self.assertEqual('/browse/testcases/Revisions?restore=1', url_for('browse', b'testcases', b'Revisions', restore=1))
        self.assertEqual('/browse/testcases/Revisions?restore=T', url_for('browse', b'testcases', b'Revisions', restore='T'))
        self.assertEqual('/browse/testcases/Revisions?restore=True', url_for('browse', b'testcases', b'Revisions', restore=True))
        self.assertEqual('/browse/testcases/R%C3%A9pertoire', url_for('browse', b'testcases', b'R\xc3\xa9pertoire'))
        # Check if multi path is supported.
        self.assertEqual('/admin/logs', url_for('admin/logs'))
        self.assertEqual('/admin/logs/backup.log', url_for('admin/logs', 'backup.log'))

    def test_do_format_lastupdated(self):
        self.assertEqual('23 seconds ago', do_format_lastupdated(RdiffTime(value=1591978823), now=1591978846))
        self.assertEqual('8 minutes ago', do_format_lastupdated(RdiffTime(value=1591978324), now=1591978846))
        self.assertEqual('2 hours ago', do_format_lastupdated(RdiffTime(value=1591971646), now=1591978846))
        self.assertEqual('2 days ago', do_format_lastupdated(RdiffTime(value=1591805524), now=1591978846))
        self.assertEqual('4 weeks ago', do_format_lastupdated(RdiffTime(value=1589127124), now=1591978846))
        self.assertEqual('5 months ago', do_format_lastupdated(RdiffTime(value=1578672724), now=1591978846))
        self.assertEqual('4 years ago', do_format_lastupdated(RdiffTime(value=1452442324), now=1591978846))


class UrlForTest(AppTestCase):

    reset_testcases = True

    USERNAME = 'admin'

    PASSWORD = 'password'

    def test_url_for_browse(self):
        """Check creation of url"""
        repo = self.app.store.get_user('admin').get_repo(self.REPO)
        self.assertEqual('/browse/admin/testcases', url_for('browse', repo))
        self.assertEqual('/browse/admin/testcases/Revisions', url_for('browse', repo, b'Revisions'))
        self.assertEqual('/browse/admin/testcases/Revisions?restore=True', url_for('browse', repo, b'Revisions', restore=True))
        self.assertEqual('/browse/admin/testcases/R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial',
                         url_for('browse', repo, b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial'))

    def test_url_for_graphs(self):
        repo = self.app.store.get_user('admin').get_repo(self.REPO)
        self.assertEqual('/graphs/files/admin/testcases', url_for('graphs', 'files', repo))

    def test_url_for_history(self):
        """Check creation of url"""
        repo = self.app.store.get_user('admin').get_repo(self.REPO)
        self.assertEqual('/history/admin/testcases', url_for('history', repo))

    def test_url_for_restore(self):
        repo = self.app.store.get_user('admin').get_repo(self.REPO)
        self.assertEqual('/restore/admin/testcases?date=1414967021', url_for('restore', repo, date=RdiffTime(1414967021)))
        self.assertEqual('/restore/admin/testcases?date=1414967021', url_for('restore', repo, b'', date=RdiffTime(1414967021)))
        self.assertEqual('/restore/admin/testcases?date=1414967021&kind=tar.gz', url_for('restore', repo, b'', date=RdiffTime(1414967021), kind='tar.gz'))
        self.assertEqual('/restore/admin/testcases/Revisions?date=1414967021', url_for('restore', repo, b'Revisions', date=RdiffTime(1414967021)))
        self.assertEqual('/restore/admin/testcases/R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial?date=1414967021',
                         url_for('restore', repo, b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial', date=RdiffTime(1414967021)))

    def test_url_for_status(self):
        repo = self.app.store.get_user('admin').get_repo(self.REPO)
        self.assertEqual('/status?date=1414967021', url_for('status', date=RdiffTime(1414967021)))
        self.assertEqual('/status/admin/testcases?date=1414967021', url_for('status', repo, date=RdiffTime(1414967021)))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
