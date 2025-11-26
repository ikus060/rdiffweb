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

import logging
import os

import cherrypy
from cherrypy.process.plugins import SimplePlugin
from oauthlib.oauth2 import OAuth2Error
from requests.exceptions import RequestException
from requests_oauthlib import OAuth2Session

OAUTH_STATE = '_oauth_state'

# Don't mind HTTPS verification done by oauthlib.
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

logger = logging.getLogger(__name__)


def _get_first_claim(user_info, claims):
    """
    Extract the first available claim from OpenID user info.

    Args:
        user_info (dict): OpenID user info dictionary containing claims
        claims (list): List of possible claim

    Returns:
        str or None: The value of the first matching claim found, or None if no match
    """
    if isinstance(claims, str):
        claims = [claims]
    assert isinstance(user_info, (dict, list))
    for claim in claims:
        if claim in user_info and user_info[claim] is not None:
            return user_info[claim]
    return None


class OAuthPlugin(SimplePlugin):

    client_id = None
    client_secret = None
    scope = ["openid", "profile", "email"]
    auth_url = None
    token_url = None
    userinfo_url = None

    fullname_claim = None
    firstname_claim = None
    lastname_claim = None
    email_claim = "email"
    userkey_claim = "email"
    required_claims = []

    def _verified_required_claim(self, user_info):
        """
        Verifies if the user_info contains all required claims with the expected value(s).
        Handles both scalar and list-type claims.

        Args:
            user_info (dict): The claims of the current user.

        Returns:
            bool: True if all required claims are satisfied, False otherwise.
        """
        if self.required_claims:
            for claim, expected_value in self.required_claims:
                value = user_info.get(claim, None)
                # If the value in user_info is a list
                if isinstance(value, list):
                    if expected_value not in value:
                        return False
                else:
                    if value != expected_value:
                        return False
        return True

    def start(self):
        """Plugin start - mount OAuth endpoints"""
        if self.client_id or self.client_secret:
            self.bus.log('Starting OAuth plugin')
            # Mount OAuth endpoints
            app = cherrypy.tree.apps.get('')
            if app and hasattr(app, 'root'):
                app.merge(
                    {
                        '/oauth': {
                            'tools.sessions.on': True,
                            'tools.auth.on': False,  # Don't protect OAuth endpoints
                            'tools.auth_mfa.on': False,
                        }
                    }
                )
                app.root.oauth = self

    def stop(self):
        self.bus.log('Stopping OAuth plugin')

    def graceful(self):
        """Reload of subscribers."""
        self.stop()
        self.start()

    @cherrypy.expose()
    def login(self, **kwargs):
        # Create a redirect URI.
        redirect_uri = cherrypy.url('callback')
        # Redirect to OAuth provider
        oauth = OAuth2Session(self.client_id, redirect_uri=redirect_uri, scope=self.scope)
        authorization_url, state = oauth.authorization_url(self.auth_url)
        # Need to store the "state" in session for verification
        cherrypy.serving.session[OAUTH_STATE] = state
        raise cherrypy.HTTPRedirect(authorization_url)

    @cherrypy.expose()
    def callback(self, code=None, state=None, error=None, error_description=None, **kwargs):

        # Check for error
        if error or error_description:
            logger.warning(f'OAuth error: {error} - {error_description}')
            raise cherrypy.HTTPError(400, "Authentication failed. OAuth error: " + error)

        # Verify state parameter
        session_state = cherrypy.serving.session.get(OAUTH_STATE, None)
        if not state or not session_state or state != session_state:
            logger.warning('OAuth state mismatch or missing')
            raise cherrypy.HTTPError(400, "Invalid state parameter")
        del cherrypy.serving.session[OAUTH_STATE]

        # Check code value.
        if not code:
            logger.warning('no authorization code received')
            raise cherrypy.HTTPError(400, "No authorization code received")

        # Query the token.
        redirect_uri = cherrypy.url('/oauth/callback')
        oauth = OAuth2Session(self.client_id, state=session_state, redirect_uri=redirect_uri)
        try:
            # Don't need to store the token, since we are not calling OAuth afterward.
            oauth.fetch_token(self.token_url, client_secret=self.client_secret, code=code)
        except OAuth2Error as e:
            logger.warning(f'OAuth2 error: {e}', exc_info=1)
            raise cherrypy.HTTPError(400, "Authentication failed")
        except RequestException as e:
            logger.warning(f'network error during token fetch: {e}', exc_info=1)
            raise cherrypy.HTTPError(503, "Service temporarily unavailable")
        except Exception as e:
            logger.error(f'unexpected error during token fetch: {e}', exc_info=1)
            raise cherrypy.HTTPError(500, "Internal server error")

        # Query user_info
        try:
            response = oauth.get(self.userinfo_url)
            response.raise_for_status()  # Raise exception for HTTP errors
            user_info = response.json()
        except Exception:
            logger.warning('fail to fetch user info', exc_info=1)
            raise cherrypy.HTTPError(400, "Failed to fetch user info")

        if not isinstance(user_info, dict):
            raise cherrypy.HTTPError(400, "Invalid user info format")

        logger.debug("OAuth user info: %s", user_info)

        # Verify required claims
        if not self._verified_required_claim(user_info):
            raise cherrypy.HTTPError(403, "Missing required claim")

        # Extract fields from the user_info.
        fullname = _get_first_claim(user_info, self.fullname_claim)
        if fullname is None:
            firstname = _get_first_claim(user_info, self.firstname_claim)
            lastname = _get_first_claim(user_info, self.lastname_claim)
            fullname = ' '.join([name for name in [firstname, lastname] if name])
        email = _get_first_claim(user_info, self.email_claim)
        userkey = _get_first_claim(user_info, self.userkey_claim)

        # Let fail if the provide doesn't has the required info.
        if not userkey or (isinstance(userkey, str) and not userkey.strip()):
            logger.warning('No usable user key in user info (claims tried: %s)', self.userkey_claim)
            raise cherrypy.HTTPError(400, "Failed to determine user identifier from OAuth provider")

        # With OAuth with loging with email.
        userobj = cherrypy.tools.auth.login_with_result(
            login=userkey,
            user_info={
                'email': email,
                'fullname': fullname,
            },
        )
        # Login might fail if user doesn't exists.
        if userobj is None:
            logger.warning(f'login failed for email: {email}')
            raise cherrypy.HTTPError(403, "Authentication failed")

        # Redirect user
        raise cherrypy.tools.auth.redirect_to_original_url()


cherrypy.oauth = OAuthPlugin(cherrypy.engine)
cherrypy.oauth.subscribe()

cherrypy.config.namespaces['oauth'] = lambda key, value: setattr(cherrypy.oauth, key, value)
