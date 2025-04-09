# Copyright (C) 2025 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.
try:
    import pkg_resources

    __version__ = pkg_resources.get_distribution("minarca_server").version
except Exception:
    __version__ = "DEV"
