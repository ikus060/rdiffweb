#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 Patrik Dufresne Service Logiciel
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
"""
Created on Dec 26, 2015

@author: Patrik Dufresne
"""

from __future__ import unicode_literals

from builtins import str
import datetime
import time
import unittest

from rdiffweb.rdw_helpers import quote_url, unquote_url, rdwTime


class Test(unittest.TestCase):

    def test_quote_url(self):
        self.assertEqual('this%20is%20some%20path', quote_url('this is some path'))
        self.assertEqual('this%20is%20some%20path', quote_url(b'this is some path'))
        self.assertEqual('R%C3%A9pertoire%20%28%40vec%29%20%7Bc%C3%A0ra%C3%A7t%23%C3%A8r%C3%AB%7D%20%24%C3%A9p%C3%AAcial',
                         quote_url(b'R\xc3\xa9pertoire (@vec) {c\xc3\xa0ra\xc3\xa7t#\xc3\xa8r\xc3\xab} $\xc3\xa9p\xc3\xaacial'))

    def test_unquote_url(self):
        self.assertEqual(b'this is some path', unquote_url('this%20is%20some%20path'))
        self.assertEqual(b'this is some path', unquote_url(b'this%20is%20some%20path'))


class RdwTimeTest(unittest.TestCase):

    def test_add(self):
        """Check if addition with timedelta is working as expected."""
        # Without timezone
        self.assertEqual(rdwTime('2014-11-08T21:04:30Z'),
                         rdwTime('2014-11-05T21:04:30Z') + datetime.timedelta(days=3))
        # With timezone
        self.assertEqual(rdwTime('2014-11-08T21:04:30-04:00'),
                         rdwTime('2014-11-05T21:04:30-04:00') + datetime.timedelta(days=3))

    def test_compare(self):
        """Check behaviour of comparison operator operator."""

        self.assertTrue(rdwTime('2014-11-07T21:04:30-04:00') < rdwTime('2014-11-08T21:04:30Z'))
        self.assertTrue(rdwTime('2014-11-08T21:04:30Z') < rdwTime('2014-11-08T21:50:30Z'))
        self.assertFalse(rdwTime('2014-11-08T22:04:30Z') < rdwTime('2014-11-08T21:50:30Z'))

        self.assertFalse(rdwTime('2014-11-07T21:04:30-04:00') > rdwTime('2014-11-08T21:04:30Z'))
        self.assertFalse(rdwTime('2014-11-08T21:04:30Z') > rdwTime('2014-11-08T21:50:30Z'))
        self.assertTrue(rdwTime('2014-11-08T22:04:30Z') > rdwTime('2014-11-08T21:50:30Z'))

    def test_init(self):
        """
        Check various constructor.
        """
        t0 = rdwTime()
        self.assertAlmostEqual(int(time.time()), t0.timeInSeconds, delta=5000)

        t1 = rdwTime(1415221470)
        self.assertEqual(1415221470, t1.timeInSeconds)

        t2 = rdwTime('2014-11-05T21:04:30Z')
        self.assertEqual(1415221470, t2.timeInSeconds)

    def test_int(self):
        """Check if int(rdwTime) return expected value."""
        self.assertEqual(1415221470, int(rdwTime(1415221470)))

    def test_str(self):
        """Check if __str__ is working."""
        self.assertEqual('2014-11-05 21:04:30', str(rdwTime(1415221470)))

    def test_sub(self):
        """Check if addition with timedelta is working as expected."""
        # Without timezone
        self.assertEqual(rdwTime('2014-11-02T21:04:30Z'),
                         rdwTime('2014-11-05T21:04:30Z') - datetime.timedelta(days=3))
        # With timezone
        self.assertEqual(rdwTime('2014-11-02T21:04:30-04:00'),
                         rdwTime('2014-11-05T21:04:30-04:00') - datetime.timedelta(days=3))

        # With datetime
        self.assertTrue((rdwTime('2014-11-02T21:04:30Z') - rdwTime()).days < 0)
        self.assertTrue((rdwTime() - rdwTime('2014-11-02T21:04:30Z')).days > 0)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
