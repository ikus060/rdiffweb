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

import argparse
import logging
import logging.config
import logging.handlers
import sys
import rdiffweb

import cherrypy

from rdiffweb import rdw_app
from rdiffweb.core.config import read_config
from rdiffweb.core.notification import NotificationPlugin
from rdiffweb.core.rdw_deamon import RemoveOlder

# Define logger for this module
logger = logging.getLogger(__name__)


def _setup_logging(log_file, log_access_file, level):
    """
    Called by `start()` to configure the logging system
    """
    assert isinstance(logging.getLevelName(level), int)

    def remove_cherrypy_date(record):
        """Remove the leading date for cherrypy error."""
        if record.name.startswith('cherrypy.error'):
            record.msg = record.msg[23:].strip()
        return True

    def add_ip(record):
        """Add request IP to record."""
        if hasattr(cherrypy, 'serving'):
            request = cherrypy.serving.request
            remote = request.remote
            record.ip = remote.name or remote.ip
            # If the request was forwarded by a reverse proxy
            if 'X-Forwarded-For' in request.headers:
                record.ip = request.headers['X-Forwarded-For']
        return True

    def add_username(record):
        """Add current username to record."""
        record.user = cherrypy.request and cherrypy.request.login or "anonymous"
        return True

    cherrypy.config.update({'log.screen': False, 'log.access_file': '', 'log.error_file': ''})
    cherrypy.engine.unsubscribe('graceful', cherrypy.log.reopen_files)

    # Configure root logger
    logger = logging.getLogger('')
    logger.level = logging.getLevelName(level)
    if log_file:
        print("continue logging to %s" % log_file)
        default_handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10485760, backupCount=20)
    else:
        default_handler = logging.StreamHandler(sys.stdout)
    default_handler.addFilter(remove_cherrypy_date)
    default_handler.addFilter(add_ip)
    default_handler.addFilter(add_username)
    default_handler.setFormatter(logging.Formatter("[%(asctime)s][%(levelname)-7s][%(ip)s][%(user)s][%(threadName)s][%(name)s] %(message)s"))
    logger.addHandler(default_handler)

    # Configure cherrypy access logger
    cherrypy_access = logging.getLogger('cherrypy.access')
    cherrypy_access.propagate = False
    if log_access_file:
        handler = logging.handlers.RotatingFileHandler(log_access_file, maxBytes=10485760, backupCount=20)
        cherrypy_access.addHandler(handler)

    # Configure cherrypy error logger
    cherrypy_error = logging.getLogger('cherrypy.error')
    cherrypy_error.propagate = False
    cherrypy_error.addHandler(default_handler)


def _parse_args(args):
    parser = argparse.ArgumentParser(prog='rdiffweb', description='Web interface to browse and restore rdiff-backup repositories')
    parser.add_argument('-d', '--debug', action='store_true', help='enable Rdiffweb debug mode - change the log level to DEBUG and print exception stack trace to the web interface')
    parser.add_argument('-f', '--config', help='location of Rdiffweb configuration file', default="/etc/rdiffweb/rdw.conf")
    parser.add_argument('--log-file', help='location of Rdiffweb log file. Print log to the console if not define in config file.')
    parser.add_argument('--log-access-file', help='location of Rdiffweb log access file.')
    parser.add_argument('--version', action='version', version='%(prog)s ' + rdiffweb.__version__)
    return parser.parse_args(args)


def main(args=None):
    """Start rdiffweb deamon."""
    # Parse arguments
    args = _parse_args(sys.argv[1:] if args is None else args)

    # Open config file before opening the apps.
    try:
        cfg = read_config(args.config)
    except FileNotFoundError:
        print('Fatal Error: configuration file %s not found' % args.config)
        sys.exit(1)

    log_file = args.log_file or cfg.get('logfile', None)
    log_access_file = args.log_access_file or cfg.get('logaccessfile', None)
    environment = 'development' if args.debug else cfg.get('environment', 'production')
    log_level = "DEBUG" if args.debug else cfg.get('loglevel', 'INFO')

    # Configure logging
    _setup_logging(log_file=log_file, log_access_file=log_access_file, level=log_level)

    try:
        # Create App.
        app = rdw_app.RdiffwebApp(cfg)

        # Get configuration
        serverhost = cfg.get("serverhost", "127.0.0.1")
        serverport = int(cfg.get("serverport", "8080"))
        # Get SSL configuration (if any)
        sslcertificate = cfg.get("sslcertificate")
        sslprivatekey = cfg.get("sslprivatekey")

        global_config = cherrypy._cpconfig.environments.get(environment, {})
        global_config.update({
            'server.socket_host': serverhost,
            'server.socket_port': serverport,
            'server.log_file': log_file,
            'server.ssl_certificate': sslcertificate,
            'server.ssl_private_key': sslprivatekey,
            # Set maximum POST size to 2MiB, for security.
            'server.max_request_body_size': 2097152,
            'server.environment': environment,
        })

        cherrypy.config.update(global_config)

        # Start deamons
        RemoveOlder(cherrypy.engine, app).subscribe()
        NotificationPlugin(cherrypy.engine, app).subscribe()

        # Start web server
        cherrypy.quickstart(app)
    except:
        logger.exception("FAIL")
    else:
        logger.info("STOP")


if __name__ == "__main__":
    main()
