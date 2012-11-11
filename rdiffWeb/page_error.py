# rdiffWeb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffWeb contributors
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

import rdw_helpers

class rdiffErrorPage:
   ''' Shows a very simple error message. Divorced 
       as much as possible from the rest of the system.'''
   def __init__(self, error):
      self.error = error
      
   def index(self):
      page = rdw_helpers.compileTemplate("page_start.html",
                                         title="rdiffWeb - Error",
                                         rssLink="",
                                         rssTitle="")
      page = page + self.error
      page = page + rdw_helpers.compileTemplate("page_end.html")
      return page
   index.exposed = True
