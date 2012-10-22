
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
