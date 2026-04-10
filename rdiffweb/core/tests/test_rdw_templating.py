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

import unittest

from rdiffweb.core.librdiff import RdiffTime
from rdiffweb.core.model import RepoObject, UserObject
from rdiffweb.core.rdw_templating import _ParentEntry, attrib, do_format_lastupdated, list_parents
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

    def test_do_format_lastupdated(self):
        self.assertEqual('23 seconds ago', do_format_lastupdated(1591978823, _now=1591978846))
        self.assertEqual('23 seconds ago', do_format_lastupdated(RdiffTime(1591978823), _now=1591978846))
        self.assertEqual('8 minutes ago', do_format_lastupdated(RdiffTime(1591978324), _now=1591978846))
        self.assertEqual('2 hours ago', do_format_lastupdated(RdiffTime(1591971646), _now=1591978846))
        self.assertEqual('2 days ago', do_format_lastupdated(RdiffTime(1591805524), _now=1591978846))
        self.assertEqual('4 weeks ago', do_format_lastupdated(RdiffTime(1589127124), _now=1591978846))
        self.assertEqual('5 months ago', do_format_lastupdated(RdiffTime(1578672724), _now=1591978846))
        self.assertEqual('4 years ago', do_format_lastupdated(RdiffTime(1452442324), _now=1591978846))
        self.assertEqual('1 days ago', do_format_lastupdated(RdiffTime(1676906974), _now=1676997934))


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
