# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import logging

import cherrypy
from cherrypy_foundation.logging import setup_logging

from rdiffweb.core.librdiff import find_rdiff_backup
from rdiffweb.rdw_app import RdiffwebApp

# Define logger for this module
logger = logging.getLogger(__name__)


def main(args=None, app_class=RdiffwebApp):
    """Start rdiffweb deamon."""
    # Parse arguments if config is not provided
    cfg = app_class.parse_args(args)

    # Configure logging
    log_level = "DEBUG" if cfg.debug else cfg.log_level
    setup_logging(log_file=cfg.log_file, log_access_file=cfg.log_access_file, level=log_level)

    try:
        # Prevent application from starting if rdiff-backup cannot be found.
        find_rdiff_backup()

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
