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

import re
from collections import OrderedDict

import rdiffweb.test


class CheckLinkTest(rdiffweb.test.WebCase):

    login = True

    def test_links(self):
        """
        Crawl all the pages to find broken links or relative links.
        """
        ignore = [
            '.*/logout',
            '.*/restore/admin/testcases/BrokenSymlink.*',
            '.*/browse/admin/testcases/BrokenSymlink.*',
            '.*/history/admin/testcases/BrokenSymlink.*',
            'https://www.ikus-soft.com/.*',
            'https://rdiffweb.org/.*',
            '.*js',
        ]
        done = set(['#'])
        todo = OrderedDict()
        todo["/"] = "/"
        self.getPage("/")
        # Store the original cookie since it get replace during execution.
        self.assertIsNotNone(self.cookies)
        cookies = self.cookies
        while todo:
            page, ref = todo.popitem(last=False)
            # Query page
            self.cookies = cookies
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
                    self.assertTrue(
                        newpage.startswith('http://'),
                        msg='url [%s] referenced in [%s] is not absolute' % (newpage, page),
                    )
