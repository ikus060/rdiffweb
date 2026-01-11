# Copyright (C) 2026 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.
"""
Created on Mar 12, 2025

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""
from base64 import b64encode
from unittest.mock import ANY

import minarca_server
import minarca_server.tests


class TestMinarcaOpenAPI(minarca_server.tests.AbstractMinarcaTest):
    headers = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]

    def test_get_openapi_json(self):
        # Check if the URL can be changed
        data = self.getJson("/api/openapi.json", headers=self.headers)
        self.assertEqual(
            data['paths']['/api/minarca'],
            {
                'get': {
                    'summary': ANY,
                    'description': ANY,
                    'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                    'parameters': [],
                }
            },
        )
