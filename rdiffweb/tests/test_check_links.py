#!/usr/bin/env python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2018 Patrik Dufresne Service Logiciel
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
Created on Dec 30, 2015

@author: Patrik Dufresne
"""

from __future__ import print_function
from __future__ import unicode_literals

from collections import OrderedDict
import logging
import re
import unittest

from rdiffweb.test import WebCase


class CheckLinkTest(WebCase):

    login = True

    reset_app = True

    reset_testcases = True

    def test_links(self):
        """
        Crawl all the pages to find broken links.
        """
        ignore = ['/restore/testcases/BrokenSymlink.*', '/browse/testcases/BrokenSymlink.*']
        done = set(['#', '/logout/'])
        todo = OrderedDict()
        todo["/"] = "/"
        self.getPage("/")
        while todo:
            page, ref = todo.popitem(last=False)

            self.getPage(page)
            self.assertStatus('200 OK', "can't access page [%s] referenced by [%s]" % (page, ref))

            done.add(page)

            for newpage in re.findall("href=\"([^\"]+)\"", self.body.decode('utf8', 'replace')):
                newpage = newpage.replace("&amp;", "&")
                if newpage.startswith("?"):
                    newpage = re.sub("\\?.*", "", page) + newpage
                if newpage not in done and not any(re.match(i, newpage) for i in ignore):
                    todo[newpage] = page


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
