# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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
"""
Created on Dec 26, 2015

@author: Patrik Dufresne
"""

from base64 import b64encode

import rdiffweb.test


class LoginPageTest(rdiffweb.test.WebCase):
    def test_getpage(self):
        """
        Make sure the login page can be rendered without error.
        """
        self.getPage('/')
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/?redirect=%2F')

    def test_cookie_http_only(self):
        # Given a request made to rdiffweb
        # When receiving the response
        self.getPage('/')
        # Then the header contains Set-Cookie with HttpOnly
        cookie = self.assertHeader('Set-Cookie')
        self.assertIn('HttpOnly', cookie)

    def test_getpage_with_plaintext(self):
        """
        Requesting plain text without being authenticated should show the login form.
        """
        self.getPage('/', headers=[("Accept", "text/plain")])
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/?redirect=%2F')

    def test_getpage_with_redirect_get(self):
        """
        Check encoding of redirect url when send using GET method.
        """
        #  Query the page without login-in
        self.getPage('/browse/' + self.USERNAME + "/" + self.REPO + '/DIR%EF%BF%BD/')
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue(
            'Location', self.baseurl + '/login/?redirect=%2Fbrowse%2Fadmin%2Ftestcases%2FDIR%C3%AF%C2%BF%C2%BD%2F'
        )

    def test_getpage_with_open_redirect(self):
        # Given a user browsing a URL with open redirect
        # When the user visit the login page
        self.getPage('/login/?redirect=https://attacker.com')
        # The URL is sanitize.
        self.assertNotInBody('https://attacker.com')

    def test_getpage_with_broken_encoding(self):
        """
        Check encoding of redirect url when send using GET method.
        """
        #  Query the page without login-in
        self.getPage(
            '/restore/'
            + self.USERNAME
            + "/"
            + self.REPO
            + '/Fichier%20avec%20non%20asci%20char%20%C9velyne%20M%E8re.txt'
        )
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue(
            'Location',
            self.baseurl
            + '/login/?redirect=%2Frestore%2Fadmin%2Ftestcases%2FFichier+avec+non+asci+char+%C3%89velyne+M%C3%A8re.txt',
        )

    def test_getpage_with_redirect_post(self):
        """
        Check encoding of redirect url when send using POST method.
        """
        b = {'login': 'admin', 'password': 'invalid', 'redirect': '/browse/' + self.REPO + '/DIR%EF%BF%BD/'}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('200 OK')
        self.assertInBody('id="form-login"')
        self.assertInBody('/browse/' + self.REPO + '/DIR%EF%BF%BD/"')

    def test_getpage_with_querystring_redirect_get(self):
        """
        Check if unauthenticated users are redirect properly to login page.
        """
        self.getPage('/browse/' + self.REPO + '/?restore=T')
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/?redirect=%2Fbrowse%2Ftestcases%2F%3Frestore%3DT')

    def test_getpage_with_multiple_querystring_redirect_get(self):
        self.getPage('/restore/' + self.REPO + '?date=1414871387&kind=zip')
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue(
            'Location', self.baseurl + '/login/?redirect=%2Frestore%2Ftestcases%3Fdate%3D1414871387%26kind%3Dzip'
        )

    def test_getpage_with_redirection(self):
        """
        Check if redirect url is properly rendered in HTML.
        """
        b = {
            'login': 'admin',
            'password': 'admin123',
            'redirect': '/restore/' + self.REPO + '?date=1414871387&kind=zip',
        }
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/restore/' + self.REPO + '?date=1414871387&kind=zip')

    def test_getpage_without_username(self):
        """
        Check if error is raised when requesting /login without a username.
        """
        self.getPage('/login/', method='GET')
        self.assertStatus('200 OK')

    def test_getpage_with_username_too_long(self):
        b = {'login': 'admin' * 52, 'password': 'admin123'}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('200 OK')
        self.assertInBody('Username too long.')

    def test_getpage_with_empty_password(self):
        """
        Check if authentication is failing without a password.
        """
        b = {'login': 'admin', 'password': ''}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('200 OK')
        self.assertInBody('This field is required.')

    def test_getpage_with_invalid_url(self):
        self.getPage('/login/kefuxian.mvc', method='GET')
        self.assertStatus('303 See Other')

    def test_post_with_invalid_url(self):
        self.getPage('/login/kefuxian.mvc', method='POST')
        self.assertStatus('303 See Other')

    def test_getpage_admin(self):
        """
        Access to admin area without session should redirect to login page.
        """
        self.getPage('/admin/')
        self.assertStatus('303 See Other')

    def test_getapi_without_authorization(self):
        """
        Check if 401 is return when authorization is not provided.
        """
        self.getPage('/api/')
        self.assertStatus('401 Unauthorized')

    def test_getapi_without_username(self):
        """
        Check if error 401 is raised when requesting /login without a username.
        """
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b":admin123").decode('ascii'))])
        self.assertStatus('401 Unauthorized')

    def test_getapi_with_empty_password(self):
        """
        Check if 401 is return when authorization is not provided.
        """
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b"admin:").decode('ascii'))])
        self.assertStatus('401 Unauthorized')

    def test_getapi_with_invalid_password(self):
        """
        Check if 401 is return when authorization is not provided.
        """
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b"admin:invalid").decode('ascii'))])
        self.assertStatus('401 Unauthorized')

    def test_getapi_with_authorization(self):
        """
        Check if 200 is return when authorization is not provided.
        """
        self.getPage('/api/', headers=[("Authorization", "Basic " + b64encode(b"admin:admin123").decode('ascii'))])
        self.assertStatus('200 OK')

    def test_getapi_with_session(self):
        """
        Check if 200 is return when authorization is not provided.
        """
        b = {'login': 'admin', 'password': 'admin123'}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('303 See Other')
        self.getPage('/')
        self.assertStatus('200 OK')
        # Get api using the same session.
        self.getPage('/api/')
        self.assertStatus('200 OK')


class LoginPageWithWelcomeMsgTest(rdiffweb.test.WebCase):

    default_config = {'welcomemsg': 'default message', 'welcomemsg[fr]': 'french message'}

    def test_getpage_default(self):
        """
        Make sure the login page can be rendered without error.
        """
        self.getPage('/login/', headers=[("Accept-Language", "it")])
        self.assertStatus('200 OK')
        self.assertInBody('default message')

    def test_getpage_french(self):
        """
        Make sure the login page can be rendered without error.
        """
        self.getPage('/login/', headers=[("Accept-Language", "fr")])
        self.assertStatus('200 OK')
        self.assertInBody('french message')


class LoginPageWithSessionDirTest(rdiffweb.test.WebCase):

    default_config = {
        'session-dir': '/tmp',
    }

    def test_login(self):
        # Query a page
        self.getPage('/login/')
        self.assertStatus('200 OK')
        self.assertInBody('Enter your username and password to log in.')
        # Login
        self.getPage("/login/", method='POST', body={'login': self.USERNAME, 'password': self.PASSWORD})
        self.assertStatus('303 See Other')
        # Query page again
        self.getPage('/')
        self.assertStatus('200 OK')
        self.assertNotInBody('Enter your username and password to log in.')


class LoginPageRateLimitTest(rdiffweb.test.WebCase):

    default_config = {
        'rate-limit': 5,
    }

    def test_login_ratelimit(self):
        # Given an unauthenticate
        # When requesting multple time the login page
        for i in range(0, 6):
            self.getPage('/login/')
        # Then a 429 error (too many request) is return
        self.assertStatus(429)


class LoginPageRateLimitWithSessionDirTest(rdiffweb.test.WebCase):

    default_config = {
        'session-dir': '/tmp',
        'rate-limit': 5,
    }

    def test_login_ratelimit(self):
        # Given an unauthenticate
        # When requesting multple time the login page
        for i in range(0, 6):
            self.getPage('/login/')
        # Then a 429 error (too many request) is return
        self.assertStatus(429)


class LoginPageRateLimitTestWithXForwardedFor(rdiffweb.test.WebCase):

    default_config = {
        'rate-limit': 5,
    }

    def test_login_ratelimit(self):
        # Given an unauthenticate
        # When requesting multple time the login page
        for i in range(0, 6):
            self.getPage('/login/', headers=[('X-Forwarded-For', '127.0.0.%s' % i)])
        # Then a 429 error (too many request) is return
        self.assertStatus(429)


class LoginPageRateLimitTestWithXRealIP(rdiffweb.test.WebCase):

    default_config = {
        'rate-limit': 5,
    }

    def test_login_ratelimit(self):
        # Given an unauthenticate
        # When requesting multple time the login page
        for i in range(0, 6):
            self.getPage('/login/', headers=[('X-Real-IP', '127.0.0.%s' % i)])
        # Then a 200 is return.
        self.assertStatus(200)


class LogoutPageTest(rdiffweb.test.WebCase):
    def test_getpage_without_login(self):
        # Accessing logout page directly will redirect to "/".
        self.getPage('/logout/')
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/')

    def test_getpage_with_login(self):
        # Login
        b = {'login': 'admin', 'password': 'admin123'}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('303 See Other')
        # Get content of a page.
        self.getPage("/prefs/")
        self.assertStatus('200 OK')
        # Then logout
        self.getPage('/logout/')
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/')
        # Get content of a page.
        self.getPage("/prefs/")
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/?redirect=%2Fprefs%2F')
