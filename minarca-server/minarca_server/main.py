# Copyright (C) 2026 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.
import cherrypy

import rdiffweb.main


def main(args=None):
    from minarca_server.app import MinarcaApplication

    cherrypy.minarca.subscribe()
    rdiffweb.main.main(args, app_class=MinarcaApplication)
    cherrypy.minarca.unsubscribe()


if __name__ == "__main__":
    main()
