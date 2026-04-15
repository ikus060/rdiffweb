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

from rdiffweb.core.rdw_templating import attrib


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
