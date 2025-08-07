# Copyright (C) 2025 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.
from importlib.metadata import distribution

try:
    __version__ = distribution("minarca_server").version
except Exception:
    __version__ = 'DEV'
