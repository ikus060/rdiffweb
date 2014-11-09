#!/usr/bin/python
# -*- coding: utf-8 -*-
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
import logging

import rdw_helpers
import rdw_config
import rdw_spider_repos
import email_notification
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

# Define logger for this module
logger = logging.getLogger(__name__)


def start():
    """Start rdiffweb deamon."""
    # Parse command line options
    debug = False
    autoReload = False
    pidFile = ""
    logFile = ""
    logAccessFile = ""

    opts, extraparams = getopt.getopt(sys.argv[1:],
                                      'vdr',
                                      ['debug',
                                       'log-file=',
                                       'log-access-file=',
                                       'pid-file=',
                                       'background',
                                       'autoreload'])
    for option, value in opts:
        if option in ['-d', '--debug']:
            debug = True
        if option in ['-r', '--autoreload']:
            autoReload = True
        elif option in ['--log-file']:
            logFile = value
        elif option in ['--log-access-file']:
            logAccessFile = value
        elif option in ['--pid-file']:
            pidFile = value
        elif option in ['--background']:
            rdw_helpers.daemonize()

    # Wait to write out to the pidfile until after we've (possibly) been
    # daemonized
    if pidFile:
        # Write our process id to specified file, so we can be killed later
        open(pidFile, 'a').write(str(os.getpid()) + "\n")

    # Configure logging
    logformat = '[%(asctime)s][%(levelname)-7s][%(name)s] %(message)s'
    level = logging.DEBUG if debug else logging.INFO
    if logFile:
        if not os.access(logFile, os.F_OK):
            print "log file %s not accessible" % logFile
            quit()
        logging.basicConfig(filename=logFile, level=level, format=logformat)
    else:
        logging.basicConfig(level=level, format=logformat)
    if logAccessFile:
        logging.root.handlers[0].addFilter(NotFilter("cherrypy.access"))
    logging.root.handlers[0].addFilter(ContextFilter())
    # Check if configuration file exists
    config_file = rdw_config.getConfigFile()
    if not os.access(config_file, os.F_OK):
        logger.error("configuration file is not accessible: %s" % config_file)
        quit()

    # Get configuration
    serverHost = rdw_config.get_config("ServerHost", default="localhost")
    try:
        serverPort = int(rdw_config.get_config("ServerPort", default="8080"))
    except ValueError:
        logger.error("ServerPort should be a port number")
        return
    sslCertificate = rdw_config.get_config("SslCertificate")
    sslPrivateKey = rdw_config.get_config("SslPrivateKey")

    environment = "development"
    if not debug:
        environment = "production"
    global_settings = {
        'tools.encode.on': True,
        'tools.encode.encoding': 'utf-8',
        'tools.gzip.on': True,
        'tools.sessions.on': True,
        'tools.authenticate.on': True,
        'autoreload.on': autoReload,
        'server.socket_host': serverHost,
        'server.socket_port': serverPort,
        'server.log_file': logFile,
        'server.ssl_certificate': sslCertificate,
        'server.ssl_private_key': sslPrivateKey,
        'log.screen': False,
        'log.access_file': logAccessFile,
        'server.environment': environment,
    }

    page_settings = {
        '/': {
            'tools.authenticate.checkAuth': page_locations.rdiffLocationsPage().checkAuthentication,
            'tools.authenticate.on': True,
            'tools.setup.on': True,
        },
        '/status/feed': {
            'tools.authenticate.authMethod': 'HTTP Header'
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
            'tools.staticdir.dir': "static",
            'tools.authenticate.on': False,
            'tools.setup.on': False,
        },
        '/setup': {
            'tools.setup.on': False,
            'tools.authenticate.on': False,
            'tools.sessions.on': False,
        }
    }

    if rdw_config.get_config("SessionStorage").lower() == "disk":
        sessionDir = rdw_config.get_config("SessionDir")
        if (os.path.exists(sessionDir)
                and os.path.isdir(sessionDir)
                and os.access(sessionDir, os.W_OK)):
            logger.info("Setting session mode to disk in directory %s" %
                        sessionDir)
            global_settings['tools.sessions.on'] = True
            global_settings['tools.sessions.storage_type'] = 'file'
            global_settings['tools.sessions.storage_path'] = sessionDir

    cherrypy.config.update(global_settings)
    root = page_locations.rdiffLocationsPage()
    root.setup = page_setup.rdiffSetupPage()
    root.browse = page_browse.rdiffBrowsePage()
    root.restore = page_restore.rdiffRestorePage()
    root.history = page_history.rdiffHistoryPage()
    root.status = page_status.rdiffStatusPage()
    root.admin = page_admin.rdiffAdminPage()
    root.prefs = page_prefs.rdiffPreferencesPage()

    # Start repo spider thread
    if not debug:
        killEvent = threading.Event()

        rdw_spider_repos.startRepoSpiderThread(killEvent)
        email_notification.startEmailNotificationThread(killEvent)
        if hasattr(cherrypy.engine, 'subscribe'):  # CherryPy >= 3.1
            cherrypy.engine.subscribe('stop', lambda: killEvent.set())
        else:
            cherrypy.engine.on_stop_engine_list.append(lambda: killEvent.set())

    # Start web server
    cherrypy.quickstart(root, config=page_settings)


class NotFilter(logging.Filter):

    """
    Negate logging filter
    """

    def __init__(self, name=''):
        self.name = name
        self.nlen = len(name)

    def filter(self, record):
        if self.nlen == 0:
            return 0
        elif self.name == record.name:
            return 0
        elif record.name.find(self.name, 0, self.nlen) != 0:
            return 1
        return not (record.name[self.nlen] == ".")


class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """

    def filter(self, record):
        try:
            if hasattr(cherrypy, 'serving'):
                request = cherrypy.serving.request
                remote = request.remote
                record.ip = remote.name or remote.ip
            if hasattr(cherrypy, 'session'):
                record.user = cherrypy.session['username']
        except:
            record.ip = "unknown"
            record.user = "unknown"
        return True
