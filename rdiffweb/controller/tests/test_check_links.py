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

from collections import OrderedDict
import logging
import re
import unittest

from rdiffweb.test import WebCase


class CheckLinkTest(WebCase):

    login = True

    def test_links(self):
        """
        Crawl all the pages to find broken links or relative links.
        """
        ignore = ['.*/logout', '.*/restore/admin/testcases/BrokenSymlink.*', '.*/browse/admin/testcases/BrokenSymlink.*', '.*/history/admin/testcases/BrokenSymlink.*', 'https://www.ikus-soft.com/.*', 'https://rdiffweb.org/.*', '.*js']
        done = set(['#'])
        todo = OrderedDict()
        todo["/"] = "/"
        self.getPage("/")
        while todo:
            page, ref = todo.popitem(last=False)
            # Query page
            self.getPage(page)
            # Check status
            self.assertStatus('200 OK', "can't access page [%s] referenced by [%s]" % (page, ref))

            done.add(page)

            # Collect all link in the page.
            for unused, newpage in re.findall("(href|src)=\"([^\"]+)\"", self.body.decode('utf8', 'replace')):
                newpage = newpage.replace("&amp;", "&")
                if newpage.startswith("?"):
                    newpage = re.sub("\\?.*", "", page) + newpage
                if newpage not in done and not any(re.match(i, newpage) for i in ignore):
                    todo[newpage] = page
                    self.assertTrue(newpage.startswith('http://'), msg='url [%s] referenced in [%s] is not absolute' % (newpage, page))


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()
