#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 rdiffweb contributors
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

# TODO
import unittest
class TemplatingTest(unittest.TestCase):
   
   def test_do_format_filesize(self):
      # Test simple values
      assert(jinja_env.do_format_filesize(1024) == "1 KB")
      assert(do_format_filesize(1024 * 1024 * 1024) == "1 GB")
      assert(do_format_filesize(1024 * 1024 * 1024 * 1024) == "1 TB")
      assert(do_format_filesize(0) == "0 bytes")
      assert(do_format_filesize(980) == "980 bytes")
      assert(do_format_filesize(1024 * 980) == "980 KB")
      assert(do_format_filesize(1024 * 1024 * 1024 * 1.2) == "1.2 GB")
      assert(do_format_filesize(1024 * 1024 * 1024 * 1.243) == "1.24 GB")  # Round to one decimal
      assert(do_format_filesize(1024 * 1024 * 1024 * 1024 * 120) == "120 TB")  # Round to one decimal
