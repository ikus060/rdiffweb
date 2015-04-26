#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

from __future__ import unicode_literals

import cherrypy
import getopt
import os
import sys
import threading
import logging
import inspect

import rdw_app
import rdw_spider_repos
import i18n  # @UnusedImport
import filter_authentication  # @UnusedImport
import filter_setup  # @UnusedImport

# Define logger for this module
logger = logging.getLogger(__name__)


def setup_favicon(app, page_settings):
    """
    Used to add an entry to the page setting if the FavIcon configuration is
    defined.
    """
    favicon_b = app.config.get_config_str("FavIcon")
    if not favicon_b:
        return

    # Append custom favicon
    if (not os.path.exists(favicon_b)
            or not os.path.isfile(favicon_b)
            or not os.access(favicon_b, os.R_OK)):
        logger.warn("""path define by FavIcon doesn't exists or is no
                    accessible: %s""", favicon_b)
    else:
        logger.info("use custom favicon: %s", favicon_b)
        basename_b = os.path.basename(favicon_b)
        app.favicon = b'/custom/%s' % (basename_b)
        page_settings.update({
            app.favicon: {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': favicon_b,
                'tools.authform.on': False,
                'tools.setup.on': False,
            }
        })


def setup_header_logo(app, page_settings):
    """
    Used to add an entry to the page setting if the FavIcon configuration is
    defined.
    """
    header_logo_b = app.config.get_config_str("HeaderLogo")
    if not header_logo_b:
        return
    # Append custom header logo
    if (not os.path.exists(header_logo_b)
            or not os.path.isfile(header_logo_b)
            or not os.access(header_logo_b, os.R_OK)):
        logger.warn("path define by HeaderLogo doesn't exists: %s",
                    header_logo_b)
    else:
        logger.info("use custom header logo: %s", header_logo_b)
        basename_b = os.path.basename(header_logo_b)
        app.header_logo = b'/custom/%s' % (basename_b)
        page_settings.update({
            app.header_logo: {
                'tools.staticfile.on': True,
                'tools.staticfile.filename': header_logo_b,
                'tools.authform.on': False,
                'tools.setup.on': False,
            }
        })


def setup_logging(log_file, log_access_file, debug):
    """
    Called by `start()` to configure the logging system
    """

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

    logformat = '[%(asctime)s][%(levelname)-7s][%(name)s] %(message)s'
    level = logging.DEBUG if debug else logging.INFO
    # Configure default log file.
    if log_file:
        assert isinstance(log_file, str)
        logging.basicConfig(filename=log_file, level=level, format=logformat)
    else:
        logging.basicConfig(level=level, format=logformat)

    # Configure access log file.
    if log_access_file:
        assert isinstance(log_access_file, str)
        logging.root.handlers[0].addFilter(NotFilter("cherrypy.access"))
    logging.root.handlers[0].addFilter(ContextFilter())


def start():
    """Start rdiffweb deamon."""
    # Parse command line options
    debug = False
    autoReload = False
    log_file = b""
    log_access_file = b""
    configfile = False

    opts, extraparams = getopt.getopt(sys.argv[1:],
                                      'vdrf:',
                                      ['debug',
                                       'log-file=',
                                       'log-access-file=',
                                       'config='
                                       'autoreload'])
    for option, value in opts:
        if option in ['-d', '--debug']:
            debug = True
        if option in ['-r', '--autoreload']:
            autoReload = True
        elif option in ['--log-file']:
            log_file = value
        elif option in ['--log-access-file']:
            log_access_file = value
        elif option in ['-f', '--config']:
            configfile = value

    # Configure logging
    setup_logging(
        log_file=log_file,
        log_access_file=log_access_file,
        debug=debug)

    # Create App.
    app = rdw_app.RdiffwebApp(configfile=configfile)

    # Get configuration
    serverHost = app.config.get_config_str("ServerHost", default="0.0.0.0")
    serverPort = app.config.get_config_int("ServerPort", default="8080")
    if not serverPort:
        logger.error("ServerPort should be a port number: %s" % (serverPort))
        sys.exit(1)
    # Get SSL configuration (if any)
    sslCertificate = app.config.get_config("SslCertificate")
    sslPrivateKey = app.config.get_config("SslPrivateKey")

    global_settings = {
        'tools.encode.on': True,
        'tools.encode.encoding': 'utf-8',
        'tools.gzip.on': True,
        'tools.sessions.on': True,
        'tools.authform.on': True,
        'autoreload.on': autoReload,
        'server.socket_host': serverHost,
        'server.socket_port': serverPort,
        'server.log_file': log_file,
        'server.ssl_certificate': sslCertificate,
        'server.ssl_private_key': sslPrivateKey,
        'log.screen': False,
        'log.access_file': log_access_file,
        'server.environment': "development" if debug else "production"
    }

    page_settings = {
        b'/': {
            'tools.authform.on': True,
            'tools.setup.on': True,
            'tools.i18n.on': True,
        },
        b'/login': {
            'tools.authform.on': False,
        },
        b'/status/feed': {
            'tools.authform.on': False,
            'tools.authbasic.on': True,
            'tools.authbasic.checkpassword': app.login.check_password
        },
        b'/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.root': os.path.abspath(os.path.dirname(__file__)),
            'tools.staticdir.dir': "static",
            'tools.authform.on': False,
            'tools.setup.on': False,
        },
        b'/setup': {
            'tools.setup.on': False,
            'tools.authform.on': False,
            'tools.sessions.on': False,
        }
    }

    # Setup the custom favicon.
    setup_favicon(app, page_settings)
    # Setup the custom header logo.
    setup_header_logo(app, page_settings)

    # Configure session storage.
    if app.config.get_config("SessionStorage").lower() == "disk":
        sessionDir = app.config.get_config("SessionDir")
        if (os.path.exists(sessionDir)
                and os.path.isdir(sessionDir)
                and os.access(sessionDir, os.W_OK)):
            logger.info("Setting session mode to disk in directory %s" %
                        sessionDir)
            global_settings['tools.sessions.on'] = True
            global_settings['tools.sessions.storage_type'] = 'file'
            global_settings['tools.sessions.storage_path'] = sessionDir

    cherrypy.config.update(global_settings)

    # Start daemon thread to refresh users repository
    kill_event = threading.Event()
    rdw_spider_repos.startRepoSpiderThread(kill_event, app)

    # Register kill_event
    if hasattr(cherrypy.engine, 'subscribe'):  # CherryPy >= 3.1
        cherrypy.engine.subscribe('stop', lambda: kill_event.set())
    else:
        cherrypy.engine.on_stop_engine_list.append(lambda: kill_event.set())  # @UndefinedVariable

    # Start web server
    cherrypy.quickstart(app, config=page_settings)
