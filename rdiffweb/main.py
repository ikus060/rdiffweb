#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

from __future__ import print_function
from __future__ import unicode_literals

import getopt
import logging
import logging.config
import logging.handlers
import sys
import tempfile
import threading
import traceback

import cherrypy
from future.builtins import str

from rdiffweb import rdw_app
from rdiffweb.core.config import read_config
from rdiffweb.core.notification import NotificationPlugin
from rdiffweb.core.rdw_deamon import RemoveOlder


PY2 = sys.version_info[0] == 2
nativestr = bytes if PY2 else str

# Define logger for this module
logger = logging.getLogger(__name__)


def debug_dump_mem():
    """
    Called when receiving a debug signal.
    Interrupt running process, and provide a python prompt for
    interactive debugging."""
    logger.warning("receive signal to dump memory")
    try:
        from meliae import scanner  # @UnresolvedImport
    except:
        logger.warning("can't dump memory, meliae is not available")
        return
    try:
        filename = tempfile.mktemp(suffix='.json', prefix='rdiff-dump-')
        logger.info("create memory dump: %s", filename)
        scanner.dump_all_objects(filename)
    except:
        logger.warning("fail to dump memory", exc_info=True)


def debug_dump_thread():
    """
    Called when receiving a debug signal.
    Dump all thread stack in stdout.
    """
    for th in threading.enumerate():
        print(th)
        traceback.print_stack(sys._current_frames()[th.ident])
        print()


def setup_logging(log_file, log_access_file, level):
    """
    Called by `start()` to configure the logging system
    """
    assert isinstance(logging.getLevelName(level), int)
    
    class ContextFilter(logging.Filter):
        """
        Filter the cherrypy record to remove the leading date. Also add more
        context information like ip address and username.
        """
        def filter(self, record):
            # Remove the leading date for cherrypy error.
            if record.msg.startswith('cherrypy.error'):
                record.msg = record.msg[23:]
            # Get the IP
            try:
                if hasattr(cherrypy, 'serving'):
                    request = cherrypy.serving.request
                    remote = request.remote
                    record.ip = remote.name or remote.ip
                    # If the request was forware by a reverse proxy
                    if 'X-Forwarded-For' in request.headers:
                        record.ip = request.headers['X-Forwarded-For']
            except:
                record.ip = "unknown"
            # Get the username
            try:
                record.user = cherrypy.session['user']  # @UndefinedVariable
            except:
                record.user = "anonymous"
            return True

    cherrypy.config.update({'log.screen': False,
                            'log.access_file': '',
                            'log.error_file': ''})
    cherrypy.engine.unsubscribe('graceful', cherrypy.log.reopen_files)

    # Create default formatter
    fmt = logging.Formatter("[%(asctime)s][%(levelname)-7s][%(ip)s][%(user)s][%(threadName)s][%(name)s] %(message)s")

    # Declare / create all logger
    logger = logging.getLogger('')
    logger.level = logging.getLevelName(level)
    cherrypy_access = logging.getLogger('cherrypy.access')
    cherrypy_access.propagate = False
    cherrypy_error = logging.getLogger('cherrypy.error')
    cherrypy_error.propagate = False
    
    # Configure default logger
    if log_file:
        print("continue logging to %s" % log_file)
        default_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10485760, backupCount=20)
    else:
        default_handler = logging.StreamHandler(sys.stdout)
    default_handler.addFilter(ContextFilter())
    default_handler.setFormatter(fmt)
    logger.addHandler(default_handler)
    
    # Configure cherrypy access logger
    if log_access_file:
        handler = logging.handlers.RotatingFileHandler(log_access_file, maxBytes=10485760, backupCount=20)
        cherrypy_access.addHandler(handler)
    
    # Configure cherrypy error logger
    if log_file:
        cherrypy_error.addHandler(default_handler)
    else:
        handler = logging.StreamHandler(sys.stdout)
        cherrypy_error.addHandler(handler)


def start():
    """Start rdiffweb deamon."""
    # Parse command line options
    args = {}
    opts = getopt.getopt(
        sys.argv[1:],
        'vdrf:', [
            'debug',
            'log-file=',
            'log-access-file=',
            'config=',
        ])[0]
    for option, value in opts:
        if option in ['-d', '--debug']:
            args['debug'] = True
        elif option in ['--log-file']:
            args['log_file'] = value
        elif option in ['--log-access-file']:
            args['log_access_file'] = value
        elif option in ['-f', '--config']:
            args['config'] = value

    # Open config file before opening the apps.
    configfile = args.get('config', '/etc/rdiffweb/rdw.conf')
    cfg = read_config(configfile)
    log_file = args.get('log_file', None) or cfg.get('logfile', False)
    log_access_file = args.get('log_access_file', None) or cfg.get('logaccessfile', None)
    if args.get('debug', False):
        environment = 'development'
        log_level = "DEBUG"
    else:
        environment = cfg.get('environment', 'production')
        log_level = cfg.get('loglevel', 'INFO')

    # Configure logging
    setup_logging(
        log_file=log_file,
        log_access_file=log_access_file,
        level=log_level)

    # Create App.
    app = rdw_app.RdiffwebApp(cfg)

    # Get configuration
    serverHost = nativestr(cfg.get("serverhost", "127.0.0.1"))
    serverPort = int(cfg.get("serverport", "8080"))
    # Get SSL configuration (if any)
    sslCertificate = cfg.get("sslcertificate")
    sslPrivateKey = cfg.get("sslprivatekey")

    global_config = cherrypy._cpconfig.environments.get(environment, {})
    global_config.update({
        'server.socket_host': serverHost,
        'server.socket_port': serverPort,
        'server.log_file': log_file,
        'server.ssl_certificate': sslCertificate,
        'server.ssl_private_key': sslPrivateKey,
        # Set maximum POST size to 2MiB, for security.
        'server.max_request_body_size': 2097152,
        'server.environment': environment,
    })

    cherrypy.config.update(global_config)

    # Add a custom signal handler
    cherrypy.engine.signal_handler.handlers['SIGUSR2'] = debug_dump_mem
    cherrypy.engine.signal_handler.handlers['SIGABRT'] = debug_dump_thread

    # Start deamons
    RemoveOlder(cherrypy.engine, app).subscribe()
    NotificationPlugin(cherrypy.engine, app).subscribe()

    # Start web server
    cherrypy.quickstart(app)

    # Log startup
    logger.info("STOP")


if __name__ == "__main__":
    start()
