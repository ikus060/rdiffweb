import cherrypy
try:
   from cherrypy.filters.basefilter import BaseFilter
except:
   from cherrypy.lib.filter.basefilter import BaseFilter

class rdwHttpsFilter(BaseFilter):
    def onStartResource(self):
        cherrypy.request.scheme = 'https'

    def beforeRequestBody(self):
      if cherrypy.request.browserUrl.startswith("http://"):
         cherrypy.request.browserUrl = cherrypy.request.browserUrl.replace("http://", "https://")

