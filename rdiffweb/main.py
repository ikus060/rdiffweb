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
import sys
import threading
import logging
import tempfile

from rdiffweb import rdw_app
from rdiffweb import rdw_spider_repos
from rdiffweb import i18n  # @UnusedImport
from rdiffweb import filter_authentication  # @UnusedImport

# Define logger for this module
logger = logging.getLogger(__name__)


def debug_dump():
    """
    Called when receiving a debug signal.
    Interrupt running process, and provide a python prompt for
    interactive debugging."""
    logger.warn("receive signal to dump memory")
    try:
        from meliae import scanner  # @UnresolvedImport
    except:
        logger.warn("can't dump memory, meliae is not available")
        return
    try:
        filename = tempfile.mktemp(suffix='.json', prefix='rdiff-dump-')
        logger.info("create memory dump: %s" % (filename,))
        scanner.dump_all_objects(filename)
    except:
        logger.warn("fail to dump memory", exc_info=True)


def error_page(**kwargs):
    """
    Default error page.
    Try to fix a cherrypy error related to encoding.
    """
    # Template is a str, convert it to unicode.
    template = cherrypy._cperror._HTTPErrorTemplate.decode('ascii', 'replace')
    return template % dict([(key, value.decode('ascii', 'replace')) for key, value in kwargs.iteritems()])


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
                    # If the request was forware by a reverse proxy
                    if 'X-Forwarded-For' in request.headers:
                        record.ip = request.headers['X-Forwarded-For']
            except:
                record.ip = "none"
            try:
                record.user = cherrypy.session['username']  # @UndefinedVariable
            except:
                record.user = "none"
            return True

    logformat = '[%(asctime)s][%(levelname)-7s][%(ip)s][%(user)s][%(threadName)s][%(name)s] %(message)s'
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
    log_file = b""
    log_access_file = b""
    configfile = b'/etc/rdiffweb/rdw.conf'

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
            debug = True
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

    # Log startup
    logger.info("START")

    # Create App.
    app = rdw_app.RdiffwebApp(configfile)

    # Get configuration
    serverHost = app.cfg.get_config_str("ServerHost", default="0.0.0.0")
    serverPort = app.cfg.get_config_int("ServerPort", default="8080")
    if not serverPort:
        logger.error("ServerPort should be a port number: %s" % (serverPort))
        sys.exit(1)
    # Get SSL configuration (if any)
    sslCertificate = app.cfg.get_config("SslCertificate")
    sslPrivateKey = app.cfg.get_config("SslPrivateKey")

    global_config = {
        'server.socket_host': serverHost,
        'server.socket_port': serverPort,
        'server.log_file': log_file,
        'server.ssl_certificate': sslCertificate,
        'server.ssl_private_key': sslPrivateKey,
        # Set maximum POST size to 2MiB, for security.
        'server.max_request_body_size': 2097152,
        'log.screen': False,
        'log.access_file': log_access_file,
        'server.environment': "development" if debug else "production",
        'error_page.default': error_page,
    }

    cherrypy.config.update(global_config)

    # Add a custom signal handler
    cherrypy.engine.signal_handler.handlers['SIGUSR2'] = debug_dump

    # Start web server
    cherrypy.quickstart(app)

    # Log startup
    logger.info("STOP")


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    start()
