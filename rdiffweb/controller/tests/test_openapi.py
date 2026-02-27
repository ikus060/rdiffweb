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
from base64 import b64encode
from unittest.mock import ANY

import rdiffweb
import rdiffweb.test


class APITest(rdiffweb.test.WebCase):
    headers = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]
    maxDiff = None

    def test_get_openapi_json(self):
        data = self.getJson('/api/openapi.json', headers=self.headers)
        # Clear description
        for path, path_object in data['paths'].items():
            for method, method_object in path_object.items():
                method_object['description'] = ANY
        self.assertEqual(
            data,
            {
                'openapi': '3.0.0',
                'info': {
                    'title': 'rdiffweb',
                    'description': ANY,
                    'version': ANY,
                },
                'servers': [{'url': ANY}],
                'paths': {
                    '/api': {
                        'get': {
                            'summary': 'Returns the current application version in JSON format.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                        }
                    },
                    '/api/currentuser': {
                        'get': {
                            'summary': 'Returns information about the current user, including user settings and a list of repositories.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Update current user information: fullname, email, lang and report_time_range',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                            'requestBody': {'required': True, 'content': {'application/json': {}}},
                        },
                    },
                    '/api/currentuser/repos/{name_or_repoid}': {
                        'get': {
                            'summary': 'Return repository settings for the given id or name',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'name_or_repoid', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'post': {
                            'summary': 'Used to update repository settings.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'name_or_repoid', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                            'requestBody': {'required': True, 'content': {'application/json': {}}},
                        },
                    },
                    '/api/currentuser/repos': {
                        'get': {
                            'summary': 'Return current user repositories',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                        }
                    },
                    '/api/currentuser/sshkeys/{fingerprint}': {
                        'get': {
                            'summary': 'Return SSH key for given fingerprint',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'fingerprint', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'delete': {
                            'summary': 'Delete a SSH key',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'fingerprint', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                    },
                    '/api/currentuser/sshkeys': {
                        'post': {
                            'summary': 'Add a SSH key to current user',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                            'requestBody': {'required': True, 'content': {'application/json': {}}},
                        },
                        'get': {
                            'summary': 'List current user keys',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                        },
                    },
                    '/api/currentuser/tokens/{name}': {
                        'get': {
                            'summary': 'Return a specific access token info',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'name', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'delete': {
                            'summary': 'Delete a specific access token.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'name', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                    },
                    '/api/currentuser/tokens': {
                        'post': {
                            'summary': 'Create a new access token',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                            'requestBody': {'required': True, 'content': {'application/json': {}}},
                        },
                        'get': {
                            'summary': 'Return list of current user access token',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                        },
                    },
                    '/api/openapi_json': {
                        'get': {
                            'summary': 'Generate OpenAPI JSON for a given CherryPy root application.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                        }
                    },
                    '/api/users': {
                        'get': {
                            'description': ANY,
                            'parameters': [],
                            'responses': {'200': {'content': {'application/json': {}}, 'description': 'OK'}},
                            'summary': 'List all users.',
                        },
                        'post': {
                            'description': ANY,
                            'parameters': [
                                {
                                    'in': 'query',
                                    'name': 'username_or_id',
                                    'schema': {'default': 'None', 'type': 'string'},
                                }
                            ],
                            'requestBody': {'content': {'application/json': {}}, 'required': True},
                            'responses': {'200': {'content': {'application/json': {}}, 'description': 'OK'}},
                            'summary': 'Create new user or update existing user.',
                        },
                    },
                    '/api/users/{username_or_id}': {
                        'delete': {
                            'description': ANY,
                            'parameters': [
                                {'in': 'path', 'name': 'username_or_id', 'required': True, 'schema': {'type': 'string'}}
                            ],
                            'responses': {'200': {'content': {'application/json': {}}, 'description': 'OK'}},
                            'summary': 'Delete the user identified by the given username or id.',
                        },
                        'get': {
                            'description': ANY,
                            'parameters': [
                                {'in': 'path', 'name': 'username_or_id', 'required': True, 'schema': {'type': 'string'}}
                            ],
                            'responses': {'200': {'content': {'application/json': {}}, 'description': 'OK'}},
                            'summary': 'Return specific user information for the given id or username.',
                        },
                    },
                },
            },
        )
