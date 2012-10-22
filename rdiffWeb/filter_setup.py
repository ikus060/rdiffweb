import cherrypy
import rdw_config


def handle_setup():
   if not rdw_config.getConfigFile():
      print
      raise cherrypy.HTTPRedirect("/setup/")

cherrypy.tools.setup = cherrypy.Tool('before_handler', handle_setup)
