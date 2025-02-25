# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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
from base64 import b64encode
from unittest.mock import ANY

import rdiffweb
import rdiffweb.test


class APITest(rdiffweb.test.WebCase):
    headers = [("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))]

    def test_get_openapi_json(self):
        data = self.getJson('/api/openapi.json', headers=self.headers)
        self.assertEqual(
            data,
            {
                'openapi': '3.0.0',
                'info': {
                    'title': 'rdiffweb',
                    'description': 'Auto-generated OpenAPI documentation',
                    'version': rdiffweb.__version__,
                },
                'servers': [{'url': 'http://127.0.0.1:54583/'}],
                'paths': {
                    '/api': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                        }
                    },
                    '/favicon_ico': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/octet-stream': {}}}},
                            'parameters': [],
                        }
                    },
                    '/header_logo': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/octet-stream': {}}}},
                            'parameters': [],
                        }
                    },
                    '/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/logo': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/octet-stream': {}}}},
                            'parameters': [],
                        }
                    },
                    '/main_css': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/css': {}}}},
                            'parameters': [],
                        }
                    },
                    '/robots_txt': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/octet-stream': {}}}},
                            'parameters': [],
                        }
                    },
                    '/static/{filename}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {
                                '200': {'description': 'OK', 'content': {'text/html': {}}},
                                '404': {'description': 'File not found'},
                            },
                            'parameters': [
                                {
                                    'name': 'filename',
                                    'in': 'path',
                                    'required': True,
                                    'description': 'The name of the static file to retrieve.',
                                    'schema': {'type': 'string'},
                                }
                            ],
                        }
                    },
                    '/admin/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/logs/data.json': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '2000'}}
                            ],
                        }
                    },
                    '/admin/logs/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/repos/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/session/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/admin/sysinfo/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/users/delete': {
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'username', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}}
                            ],
                        }
                    },
                    '/admin/users/edit': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {
                                    'name': 'username_vpath',
                                    'in': 'query',
                                    'schema': {'type': 'string'},
                                    'required': True,
                                }
                            ],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {
                                    'name': 'username_vpath',
                                    'in': 'query',
                                    'schema': {'type': 'string'},
                                    'required': True,
                                }
                            ],
                        },
                    },
                    '/admin/users/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/users/new': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/api/currentuser': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                            'requestBody': {'required': True, 'content': {'application/json': {}}},
                        },
                    },
                    '/api/openapi_json': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                        }
                    },
                    '/api/currentuser/repos': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'name_or_id', 'in': 'query', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'name_or_id', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}}
                            ],
                            'requestBody': {'required': True, 'content': {'application/json': {}}},
                        },
                    },
                    '/api/currentuser/sshkeys': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'fingerprint', 'in': 'query', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'delete': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'fingerprint', 'in': 'query', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                            'requestBody': {'required': True, 'content': {'application/json': {}}},
                        },
                    },
                    '/api/currentuser/tokens': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'name', 'in': 'query', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'delete': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'name', 'in': 'query', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [],
                            'requestBody': {'required': True, 'content': {'application/json': {}}},
                        },
                    },
                    '/browse/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        }
                    },
                    '/delete/{path}': {
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        }
                    },
                    '/graphs/activities/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '30'}},
                            ],
                        }
                    },
                    '/graphs/errors/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '30'}},
                            ],
                        }
                    },
                    '/graphs/files/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '30'}},
                            ],
                        }
                    },
                    '/graphs/sizes/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '30'}},
                            ],
                        }
                    },
                    '/graphs/times/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '30'}},
                            ],
                        }
                    },
                    '/history/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                            ],
                        }
                    },
                    '/login/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/logout': {
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/logs/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                                {'name': 'date', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}},
                                {'name': 'file', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}},
                                {'name': 'raw', 'in': 'query', 'schema': {'type': 'string', 'default': '0'}},
                            ],
                        }
                    },
                    '/mfa/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'panelid', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}}
                            ],
                        }
                    },
                    '/prefs/general': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/mfa': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/notification': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/session': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/sshkeys': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/tokens': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/restore/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'date', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}},
                                {'name': 'kind', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}},
                                {'name': 'raw', 'in': 'query', 'schema': {'type': 'string', 'default': '0'}},
                            ],
                        }
                    },
                    '/settings/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'post': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                    },
                    '/stats/data.json/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                                {'name': 'date', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}},
                            ],
                        }
                    },
                    '/stats/{path}': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                                {'name': 'date', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}},
                            ],
                        }
                    },
                    '/status/activities.json': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'query', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'days', 'in': 'query', 'schema': {'type': 'string', 'default': '7'}},
                                {'name': 'count', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                                {'name': 'sort', 'in': 'query', 'schema': {'type': 'string', 'default': '1'}},
                            ],
                        }
                    },
                    '/status/age.json': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'query', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'count', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                            ],
                        }
                    },
                    '/status/disk_usage.json': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'query', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        }
                    },
                    '/status/elapsetime.json': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'query', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'days', 'in': 'query', 'schema': {'type': 'string', 'default': '7'}},
                                {'name': 'count', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                            ],
                        }
                    },
                    '/status/': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'query', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'days', 'in': 'query', 'schema': {'type': 'string', 'default': '7'}},
                                {'name': 'count', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                            ],
                        }
                    },
                    '/status/per_days.json': {
                        'get': {
                            'summary': ANY,
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'query', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'days', 'in': 'query', 'schema': {'type': 'string', 'default': '7'}},
                            ],
                        }
                    },
                },
            },
        )
