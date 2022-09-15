# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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

import logging
import logging.config
import logging.handlers
import sys

import cherrypy

from rdiffweb.rdw_app import RdiffwebApp

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
    default_handler.setFormatter(
        logging.Formatter("[%(asctime)s][%(levelname)-7s][%(ip)s][%(user)s][%(threadName)s][%(name)s] %(message)s")
    )
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


def main(args=None, app_class=RdiffwebApp):
    """Start rdiffweb deamon."""
    # Parse arguments if config is not provided
    cfg = app_class.parse_args(args)

    # Configure logging
    log_level = "DEBUG" if cfg.debug else cfg.log_level
    _setup_logging(log_file=cfg.log_file, log_access_file=cfg.log_access_file, level=log_level)

    try:
        cherrypy.config.update(
            {
                'server.socket_host': cfg.server_host,
                'server.socket_port': cfg.server_port,
                'server.log_file': cfg.log_file,
                'server.ssl_certificate': cfg.ssl_certificate,
                'server.ssl_private_key': cfg.ssl_private_key,
                # Set maximum POST size to 2MiB, for security.
                'server.max_request_body_size': 2097152,
            }
        )
        # Start web server
        cherrypy.quickstart(app_class(cfg))
    except Exception:
        logger.exception("FAIL")
    else:
        logger.info("STOP")


if __name__ == "__main__":
    main()
