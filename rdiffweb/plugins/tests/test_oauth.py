# OAuth Plugins for cherrypy
# Copyright (C) 2025 IKUS Software
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


from collections import namedtuple

import cherrypy
import responses
from cherrypy.test import helper

from ...tools import auth  # noqa
from .. import oauth  # noqa

UserObj = namedtuple('UserObj', 'username,email,fullname')


def user_lookup_func(login, user_info):
    if login in 'test@example.com':
        # Called with email by OAuth
        user = UserObj(username='my-user', email=user_info['email'], fullname=user_info['fullname'])
        return user.username, user
    elif login == 'my-user':
        # Called with username to restore session.
        user = UserObj(username='my-user', email='test@example.com', fullname='Test User')
        return user.username, user
    return None


def user_from_key_func(user_key):
    if user_key == 'my-user':
        # Called with username to restore session.
        user = UserObj(username='my-user', email='test@example.com', fullname='Test User')
        return user
    return None


@cherrypy.tools.auth(on=True, user_lookup_func=user_lookup_func, user_from_key_func=user_from_key_func)
@cherrypy.tools.sessions()
class Root:
    @cherrypy.expose
    def index(self):
        return "OK"


class OAuthPluginTest(helper.CPWebCase):

    interactive = False

    def setUp(self):
        # Mock OAuth provider.
        responses.add(
            responses.POST,
            "https://mock-provider.com/oauth/token",
            json={
                "access_token": "mock_access_token",
                "token_type": "Bearer",
                "expires_in": 3600,
                "refresh_token": "mock_refresh_token",
            },
            status=200,
        )
        responses.add(
            responses.GET,
            "https://mock-provider.com/user",
            json={"id": "12345", "email": "test@example.com", "name": "Test User"},
            status=200,
            headers={"Authorization": "Bearer mock_access_token"},
        )
        responses.start()
        return super().setUp()

    def tearDown(self):
        responses.stop()
        responses.reset()
        return super().tearDown()

    @classmethod
    def setup_server(cls):
        cherrypy.config.update(
            {
                # Mock OAuth
                'oauth.client_id': "test_client_id",
                'oauth.client_secret': "test_client_secret",
                'oauth.auth_url': "https://mock-provider.com/oauth/authorize",
                'oauth.token_url': "https://mock-provider.com/oauth/token",
                'oauth.userinfo_url': "https://mock-provider.com/user",
                'oauth.fullname_claim': "name",
            }
        )
        cherrypy.tree.mount(Root(), '/')

    def test_oauth_login_success(self):
        # Given a OAuth provider
        # When trying to authenticate using OAuth
        self.getPage('/oauth/login')
        # Then user get redirected to OAuth provider
        self.assertStatus(303)
        redirect = self.assertHeader('Location')
        self.assertIn(
            'https://mock-provider.com/oauth/authorize?response_type=code&client_id=test_client_id&redirect_uri=http%3A%2F%2F127.0.0.1%3A54583%2Foauth%2Fcallback&scope=openid+profile+email&state=',
            redirect,
        )
        state = redirect.split('state=')[1]
        # When OAuth provider callback
        self.getPage(f'/oauth/callback?code=test&state={state}', headers=self.cookies)
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', 'http://%s:%s/' % (self.HOST, self.PORT))
        # Then user is authenticated
        self.getPage('/', headers=self.cookies)
        self.assertStatus(200)
        self.assertBody('OK')

    def test_oauth_wrong_state(self):
        # Given a OAuth provider
        # When trying to authenticate using OAuth
        self.getPage('/oauth/login')
        # Then user get redirected to OAuth provider
        self.assertStatus(303)
        redirect = self.assertHeader('Location')
        self.assertIn(
            'https://mock-provider.com/oauth/authorize?response_type=code&client_id=test_client_id&redirect_uri=http%3A%2F%2F127.0.0.1%3A54583%2Foauth%2Fcallback&scope=openid+profile+email&state=',
            redirect,
        )
        # When OAuth provider callback with invalid state
        self.getPage('/oauth/callback?code=test&state=INVALID', headers=self.cookies)
        # Then http error 400 get raised
        self.assertStatus(400)
        self.assertInBody("Invalid state parameter")

    def test_oauth_missing_code(self):
        # Given a OAuth provider
        # When trying to authenticate using OAuth
        self.getPage('/oauth/login')
        # Then user get redirected to OAuth provider
        self.assertStatus(303)
        redirect = self.assertHeader('Location')
        self.assertIn(
            'https://mock-provider.com/oauth/authorize?response_type=code&client_id=test_client_id&redirect_uri=http%3A%2F%2F127.0.0.1%3A54583%2Foauth%2Fcallback&scope=openid+profile+email&state=',
            redirect,
        )
        # When OAuth provider callback with missing code.
        state = redirect.split('state=')[1]
        self.getPage(f'/oauth/callback?state={state}', headers=self.cookies)
        # Then http error 400 get raised
        self.assertStatus(400)
        self.assertInBody("No authorization code received")

    def test_oauth_with_error(self):
        # Given a OAuth provider
        # When trying to authenticate using OAuth
        self.getPage('/oauth/login')
        # Then user get redirected to OAuth provider
        self.assertStatus(303)
        redirect = self.assertHeader('Location')
        self.assertIn(
            'https://mock-provider.com/oauth/authorize?response_type=code&client_id=test_client_id&redirect_uri=http%3A%2F%2F127.0.0.1%3A54583%2Foauth%2Fcallback&scope=openid+profile+email&state=',
            redirect,
        )
        # When OAuth provider callback with error code.
        self.getPage('/oauth/callback?error=invalid_request', headers=self.cookies)
        # Then http error 400 get raised
        self.assertStatus(400)
        self.assertInBody("Authentication failed. OAuth error: invalid_request")
