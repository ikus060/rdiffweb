#!/usr/bin/python
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffweb contributors
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

import cherrypy
import getopt
import os
import sys
import threading

import rdw_config
import rdw_spider_repos
import email_notification
import page_error
import filter_authentication
import filter_setup

import page_admin
import page_browse
import page_history
import page_locations
import page_restore
import page_setup
import page_status
import page_prefs

if __name__ == "__main__":
   # Parse command line options
   verbose = True
   debug = False
   autoReload = False
   pidFile = ""
   logFile = ""

   opts, extraparams = getopt.getopt(sys.argv[1:], 'vdr', ['debug', 'log-file=', 'pid-file=', 'background', 'autoreload'])
   for option, value in opts:
      if option in ['-d', '--debug']:
         debug = True
      if option in ['-r', '--autoreload']:
         autoReload = True
      elif option in ['--log-file']:
         logFile = value
      elif option in ['--pid-file']:
         pidFile = value
      elif option in ['--background']:
         import rdiffweb.rdw_helpers
         rdiffweb.rdw_helpers.daemonize()
         verbose = False

   # Wait to write out to the pidfile until after we've (possibly) been daemonized
   if pidFile:
      # Write our process id to specified file, so we can be killed later
      open(pidFile, 'a').write(str(os.getpid()) + "\n")

   serverPort = 8080
   if rdiffweb.rdw_config.getConfigSetting("ServerPort") != "":
      serverPort = int(rdiffweb.rdw_config.getConfigSetting("ServerPort"))
         
   environment = "development"
   if not debug:
      environment = "production"
   global_settings = {
      'tools.encode.on': True,
      'tools.encode.encoding': 'utf-8',
      'tools.gzip.on': True,
      'tools.sessions.on' : True,
      'tools.authenticate.on' : True,
      'autoreload.on' : autoReload,
      'server.socket_host' : rdiffweb.rdw_config.getConfigSetting("ServerHost"),
      'server.socket_port' : serverPort,
      'server.log_file' : logFile,
      'server.ssl_certificate': rdiffweb.rdw_config.getConfigSetting("SslCertificate"),
      'server.ssl_private_key': rdiffweb.rdw_config.getConfigSetting("SslPrivateKey"),
      'log.screen': True,
      'server.environment': environment,
   }
   
   page_settings = {
      '/': {
         'tools.authenticate.checkAuth' : rdiffweb.page_locations.rdiffLocationsPage().checkAuthentication,
         'tools.authenticate.on' : True,
         'tools.setup.on': True,
      },
      '/status/feed': {
         'tools.authenticate.authMethod' : 'HTTP Header'
      },
      '/static' : {
         'tools.staticdir.on' : True,
         'tools.staticdir.root': rdiffweb.rdw_helpers.getStaticRootPath(),
         'tools.staticdir.dir': "static",
         'tools.authenticate.on' : False,
         'tools.setup.on': False,
      },
      '/setup': {
         'tools.setup.on': False,
         'tools.authenticate.on' : False,
         'tools.sessions.on' : False,
      }
   }
   
   if rdiffweb.rdw_config.getConfigSetting("SessionStorage").lower() == "disk":
      sessionDir = rdiffweb.rdw_config.getConfigSetting("SessionDir")
      if os.path.exists(sessionDir) and os.path.isdir(sessionDir) and os.access(sessionDir, os.W_OK):
         cherrypy.log("Setting session mode to disk in directory %s" % sessionDir)
         global_settings['tools.sessions.on'] = True
         global_settings['tools.sessions.storage_type'] = 'file'
         global_settings['tools.sessions.storage_path'] = sessionDir

   cherrypy.config.update(global_settings)
   root = rdiffweb.page_locations.rdiffLocationsPage()
   root.setup = rdiffweb.page_setup.rdiffSetupPage()
   root.browse = rdiffweb.page_browse.rdiffBrowsePage()
   root.restore = rdiffweb.page_restore.rdiffRestorePage()
   root.history = rdiffweb.page_history.rdiffHistoryPage()
   root.status = rdiffweb.page_status.rdiffStatusPage()
   root.admin = rdiffweb.page_admin.rdiffAdminPage()
   root.prefs = rdiffweb.page_prefs.rdiffPreferencesPage()
   
   # Start repo spider thread
   if not debug:
      killEvent = threading.Event()
   
      rdiffweb.rdw_spider_repos.startRepoSpiderThread(killEvent)
      rdiffweb.email_notification.startEmailNotificationThread(killEvent)
      if hasattr(cherrypy.engine, 'subscribe'):  # CherryPy >= 3.1
          cherrypy.engine.subscribe('stop', lambda: killEvent.set())
      else:
          cherrypy.engine.on_stop_engine_list.append(lambda: killEvent.set())

   cherrypy.quickstart(root, config=page_settings)
