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
                    '/admin/': {
                        'get': {
                            'summary': 'Admin dashboard',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/activity/data.json': {
                        'get': {
                            'summary': 'Return list of messages.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'draw', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}},
                                {'name': 'start', 'in': 'query', 'schema': {'type': 'string', 'default': '0'}},
                                {'name': 'length', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                            ],
                        }
                    },
                    '/admin/activity/': {
                        'get': {
                            'summary': 'Show server activity.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/logs/raw': {
                        'get': {
                            'summary': 'Download full server logs.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/plain': {}}}},
                            'parameters': [
                                {
                                    'name': 'name',
                                    'in': 'query',
                                    'schema': {'type': 'string', 'default': 'None'},
                                }
                            ],
                        }
                    },
                    '/admin/logs/': {
                        'get': {
                            'summary': 'Show server logs.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'name', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '2000'}},
                            ],
                        }
                    },
                    '/admin/repos/': {
                        'get': {
                            'summary': 'Show all user repositories',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/session/': {
                        'get': {
                            'summary': 'Show or remove user sessions',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Show or remove user sessions',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/admin/sysinfo/': {
                        'get': {
                            'summary': 'Show system information and application config',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/users/delete': {
                        'post': {
                            'summary': 'Delete a user',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/users/edit/{username_or_id}': {
                        'get': {
                            'summary': 'Show form to edit user',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'username_or_id', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'post': {
                            'summary': 'Show form to edit user',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'username_or_id', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                    },
                    '/admin/users/': {
                        'get': {
                            'summary': 'Show user list',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/admin/users/messages/{username_or_id}': {
                        'get': {
                            'description': ANY,
                            'parameters': [
                                {'in': 'path', 'name': 'username_or_id', 'required': True, 'schema': {'type': 'string'}}
                            ],
                            'responses': {'200': {'content': {'application/json': {}}, 'description': 'OK'}},
                            'summary': 'No description available',
                        }
                    },
                    '/admin/users/new': {
                        'get': {
                            'summary': 'Show form to create a new user',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Show form to create a new user',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
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
                    '/audit/{path}': {
                        'get': {
                            'summary': 'No description available',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        }
                    },
                    '/browse/{path}': {
                        'get': {
                            'summary': "Browser view displaying files and folders in user's repository",
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        }
                    },
                    '/delete/{path}': {
                        'post': {
                            'summary': 'Delete a repo, a file or folder history',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        }
                    },
                    '/favicon_ico': {
                        'get': {
                            'summary': 'Return favicon image file.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/octet-stream': {}}}},
                            'parameters': [],
                        }
                    },
                    '/graphs/activities/{path}': {
                        'get': {
                            'summary': 'Called to show every graphs',
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
                            'summary': 'Called to show every graphs',
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
                            'summary': 'Called to show every graphs',
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
                            'summary': 'Called to show every graphs',
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
                            'summary': 'Called to show every graphs',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '30'}},
                            ],
                        }
                    },
                    '/header_logo': {
                        'get': {
                            'summary': 'Return static `header-logo` image file.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/octet-stream': {}}}},
                            'parameters': [],
                        }
                    },
                    '/history/{path}': {
                        'get': {
                            'summary': 'Show repository, file or folder history',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                            ],
                        }
                    },
                    '/': {
                        'get': {
                            'summary': 'Shows repositories of current user',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/login/': {
                        'get': {
                            'summary': 'Display form to authenticate user.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Display form to authenticate user.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/logo': {
                        'get': {
                            'summary': 'Return static `logo` image file.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/octet-stream': {}}}},
                            'parameters': [],
                        }
                    },
                    '/logout': {
                        'post': {
                            'summary': 'Logout user',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        }
                    },
                    '/logs/{path}': {
                        'get': {
                            'summary': 'Show repository backup and restore logs',
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
                    '/main_css': {
                        'get': {
                            'summary': 'Return CSS file based on branding configuration',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/css': {}}}},
                            'parameters': [],
                        }
                    },
                    '/mfa/': {
                        'get': {
                            'summary': 'Show Multi Factor Authentication form',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Show Multi Factor Authentication form',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/general': {
                        'get': {
                            'summary': 'Show user settings',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Show user settings',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/': {
                        'get': {
                            'summary': 'Redirect user to general settings',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'panelid', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}}
                            ],
                        }
                    },
                    '/prefs/mfa': {
                        'get': {
                            'summary': 'Show MFA settings',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Show MFA settings',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/notification': {
                        'get': {
                            'summary': 'Show user notification settings',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Show user notification settings',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/session': {
                        'get': {
                            'summary': 'Show user sessions',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Show user sessions',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/sshkeys': {
                        'get': {
                            'summary': "Show user's SSH keys",
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': "Show user's SSH keys",
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/prefs/tokens': {
                        'get': {
                            'summary': 'Show current user access token',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                        'post': {
                            'summary': 'Show current user access token',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [],
                        },
                    },
                    '/restore/{path}': {
                        'get': {
                            'summary': 'Display a webpage to prepare download or trigger download of a file or folder.',
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
                    '/robots_txt': {
                        'get': {
                            'summary': 'robots.txt to disable search crawler',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/octet-stream': {}}}},
                            'parameters': [],
                        }
                    },
                    '/settings/{path}': {
                        'get': {
                            'summary': 'Show user general settings',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                        'post': {
                            'summary': 'Show user general settings',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        },
                    },
                    '/static/{filename}': {
                        'get': {
                            'summary': 'Serve static files',
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
                                    'schema': {'type': 'string'},
                                }
                            ],
                        }
                    },
                    '/stats/data.json/{path}': {
                        'get': {
                            'summary': 'Return a json array with stats',
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
                            'summary': 'Show file statistics',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'limit', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                                {'name': 'date', 'in': 'query', 'schema': {'type': 'string', 'default': 'None'}},
                            ],
                        }
                    },
                    '/status/activities.json/{path}': {
                        'get': {
                            'summary': 'Return list of repositories with less activities (new ,modified, deleted files).',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'days', 'in': 'query', 'schema': {'type': 'string', 'default': '7'}},
                                {'name': 'count', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                                {'name': 'sort', 'in': 'query', 'schema': {'type': 'string', 'default': '1'}},
                            ],
                        }
                    },
                    '/status/age.json/{path}': {
                        'get': {
                            'summary': 'Return the oldest backup.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'count', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                            ],
                        }
                    },
                    '/status/disk_usage.json/{path}': {
                        'get': {
                            'summary': 'Return disk usage.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True}
                            ],
                        }
                    },
                    '/status/elapsetime.json/{path}': {
                        'get': {
                            'summary': 'Return list of repositories with average elapse time (in minute).',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'days', 'in': 'query', 'schema': {'type': 'string', 'default': '7'}},
                                {'name': 'count', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                            ],
                        }
                    },
                    '/status/{path}': {
                        'get': {
                            'summary': 'Show current user status',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'text/html': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'days', 'in': 'query', 'schema': {'type': 'string', 'default': '7'}},
                                {'name': 'count', 'in': 'query', 'schema': {'type': 'string', 'default': '10'}},
                            ],
                        }
                    },
                    '/status/per_days.json/{path}': {
                        'get': {
                            'summary': 'Count number of backup per days.',
                            'description': ANY,
                            'responses': {'200': {'description': 'OK', 'content': {'application/json': {}}}},
                            'parameters': [
                                {'name': 'path', 'in': 'path', 'schema': {'type': 'string'}, 'required': True},
                                {'name': 'days', 'in': 'query', 'schema': {'type': 'string', 'default': '7'}},
                            ],
                        }
                    },
                },
            },
        )
