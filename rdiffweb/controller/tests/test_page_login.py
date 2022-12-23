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
import os

from parameterized import parameterized, parameterized_class

import rdiffweb.test
from rdiffweb.core.model import DbSession, SessionObject, UserObject
from rdiffweb.tools.auth_form import LOGIN_TIME, SESSION_KEY


class LoginPageTest(rdiffweb.test.WebCase):
    def test_getpage(self):
        # When making a query to a page while unauthenticated
        self.getPage('/')
        # Then user is redirected to login page
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/')
        # Then a session object is created without a username
        self.assertEqual(1, SessionObject.query.filter(SessionObject.id == self.session_id).count())
        SessionObject.query.filter(SessionObject.id == self.session_id).first()
        session = DbSession(id=self.session_id)
        session.load()
        self.assertIsNone(session.get(SESSION_KEY))

    def test_login_success(self):
        # Given an anonymous user
        self.getPage('/')
        prev_session_id = self.session_id
        # Then user is redirected to /login page
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/')
        # When authenticating with valid credentials.
        self.getPage('/login/', method='POST', body={'login': self.USERNAME, 'password': self.PASSWORD})
        # Then a new session_id is generated
        self.assertNotEqual(prev_session_id, self.session_id)
        # Then user is redirected
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/')
        # Then a session object is created with a username
        self.assertEqual(1, SessionObject.query.filter(SessionObject.id == self.session_id).count())
        SessionObject.query.filter(SessionObject.id == self.session_id).first()
        session = DbSession(id=self.session_id)
        session.load()
        self.assertEqual('admin', session.get(SESSION_KEY))
        self.assertIsNotNone(session.get(LOGIN_TIME))

    def test_login_case_insensitive(self):
        # When authenticating with valid credentials with all uppercase username
        self.getPage('/login/', method='POST', body={'login': self.USERNAME.upper(), 'password': self.PASSWORD})
        # Then a new session_id is generated
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/')
        self.getPage('/')
        self.assertStatus(200)

    def test_cookie_http_only(self):
        # Given a request made to rdiffweb
        # When receiving the response
        self.getPage('/')
        # Then the header contains Set-Cookie with HttpOnly
        cookie = self.assertHeader('Set-Cookie')
        self.assertIn('HttpOnly', cookie)

    def test_login_with_plaintext(self):
        """
        Requesting plain text without being authenticated should show the login form.
        """
        # When querying root page without authentication
        self.getPage('/', headers=[("Accept", "text/plain")])
        # Then user is redirected to /login page
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/')

    @parameterized.expand(
        [
            ('with_root', '/'),
            ('with_browse_url', '/browse/admin/testcases/Revisions/'),
            ('with_encoded_url', '/browse/admin/testcases/DIR%EF%BF%BD/'),
            (
                'with_broken_encoding',
                '/restore/admin/testcases/Fichier%20avec%20non%20asci%20char%20%C9velyne%20M%E8re.txt/?date=1415221507',
            ),
            ('with_query_string', '/restore/admin/testcases/Revisions?date=1477434528'),
            ('with_multiple_query_string', '/restore/admin/testcases/Revisions?date=1477434528&kind=tar.gz'),
            ('with_admin', '/admin/'),
        ]
    )
    def test_login(self, unused, original_url):
        # Given an unauthenticated user
        # Query the page without login-in
        self.getPage(original_url)
        # Then user is redirected to the login page
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/')
        # When authentication is successful
        self.getPage('/login/', method='POST', body={'login': self.USERNAME, 'password': self.PASSWORD})
        # Then user is redirected to original URL
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + original_url)
        # Then cookie is not persistent
        self.assertNotIn('expires', self.cookies[0][1])
        self.assertNotIn('Max-Age', self.cookies[0][1])
        # When requesting the original page
        self.getPage(original_url)
        # Then page return without error
        self.assertStatus(200)

    def test_getpage_with_redirect_post(self):
        """
        Check encoding of redirect url when send using POST method.
        """
        # When posting invalid credentials
        b = {'login': 'admin', 'password': 'invalid', 'redirect': '/browse/' + self.REPO + '/DIR%EF%BF%BD/'}
        self.getPage('/login/', method='POST', body=b)
        # Then page return without HTTP Error
        self.assertStatus('200 OK')
        # Then page display an error
        self.assertInBody('Invalid username or password.')
        self.assertInBody('form-login')
        # Then redirect URL is ignored
        self.assertNotInBody('/browse/' + self.REPO + '/DIR%EF%BF%BD/"')

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

    def test_login_twice(self):
        # Given an authenticated user
        self.getPage('/login/', method='POST', body={'login': self.USERNAME, 'password': self.PASSWORD})
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + "/")
        self.getPage('/')
        self.assertStatus(200)
        self.assertInBody(self.USERNAME)
        # Given another user
        userobj = UserObject.add_user('otheruser', password='password')
        userobj.commit()
        # When trying to re-authenticated with login page
        self.getPage('/login/', method='POST', body={'login': 'otheruser', 'password': 'password'})
        # Then user is still authenticated with previous user
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + "/")
        self.getPage('/')
        self.assertStatus(200)
        self.assertInBody(self.USERNAME)

    def test_login_persistent(self):
        # Given a user authenticated with persistent
        self.getPage('/logout', method="POST")
        self.assertStatus(303)
        self.getPage(
            '/login/', method='POST', body={'login': self.USERNAME, 'password': self.PASSWORD, 'persistent': '1'}
        )
        self.assertStatus(303)
        # Then a persistent cookie is return
        self.assertIn('expires', self.cookies[0][1])
        self.assertIn('Max-Age', self.cookies[0][1])
        # Then a session is created with persistent flag
        session = DbSession(id=self.session_id)
        session.load()
        self.assertTrue(session['login_persistent'])
        # Then session timeout is 30 days in future
        self.assertAlmostEqual(session.timeout, 43200, delta=2)


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


class LoginPageWithHeaderName(rdiffweb.test.WebCase):

    default_config = {'header-name': 'HEADER-NAME'}

    def test_getpage_default(self):
        # Given a custom header-name
        # When querying the loging page
        self.getPage('/login/')
        # Then the page display the header-name
        self.assertStatus('200 OK')
        self.assertInBody('HEADER-NAME')


@parameterized_class(
    [
        {"default_config": {'rate-limit': 5}},
        {"default_config": {'rate-limit': 5, 'rate-limit-dir': '/tmp'}},
    ]
)
class LoginPageRateLimitTest(rdiffweb.test.WebCase):
    def setUp(self):
        if os.path.isfile('/tmp/ratelimit-127.0.0.1'):
            os.unlink('/tmp/ratelimit-127.0.0.1')
        if os.path.isfile('/tmp/ratelimit-127.0.0.1.-login'):
            os.unlink('/tmp/ratelimit-127.0.0.1.-login')
        return super().setUp()

    def test_login_ratelimit(self):
        # Given an unauthenticate
        # When requesting multiple time the login page
        for i in range(1, 5):
            self.getPage('/login/', method='POST', body={'login': 'invalid', 'password': 'invalid'})
            self.assertStatus(200)
        # Then a 429 error (too many request) is return
        self.getPage('/login/', method='POST', body={'login': 'invalid', 'password': 'invalid'})
        self.assertStatus(429)


class LoginPageRateLimitTest2(rdiffweb.test.WebCase):

    default_config = {'rate-limit': 5}

    def test_login_ratelimit_forwarded_for(self):
        # Given an unauthenticate
        # When requesting multiple time the login page with different `X-Forwarded-For`
        for i in range(1, 5):
            self.getPage(
                '/login/',
                headers=[('X-Forwarded-For', '127.0.0.%s' % i)],
                method='POST',
                body={'login': 'invalid', 'password': 'invalid'},
            )
            self.assertStatus(200)
        # Then original IP get blocked
        self.getPage(
            '/login/',
            headers=[('X-Forwarded-For', '127.0.0.%s' % i)],
            method='POST',
            body={'login': 'invalid', 'password': 'invalid'},
        )
        self.assertStatus(429)


class LoginPageRateLimitTest3(rdiffweb.test.WebCase):
    default_config = {'rate-limit': 5}

    def test_login_ratelimit_real_ip(self):
        # Given an unauthenticate
        # When requesting multiple time the login page with different `X-Real-IP`
        for i in range(1, 5):
            self.getPage(
                '/login/',
                headers=[('X-Real-IP', '127.0.0.128')],
                method='POST',
                body={'login': 'invalid', 'password': 'invalid'},
            )
            self.assertStatus(200)
        # Then the X-Real-IP get blocked
        self.getPage(
            '/login/',
            headers=[('X-Real-IP', '127.0.0.128')],
            method='POST',
            body={'login': 'invalid', 'password': 'invalid'},
        )
        self.assertStatus(429)


class LogoutPageTest(rdiffweb.test.WebCase):
    def test_getpage_without_login(self):
        # Given an unauthenticated user
        # When Accessing logout page directly
        self.getPage('/logout', method="POST")
        # Then user is redirect to root '/'
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/')

    def test_getpage_with_login(self):
        # Given an anonymous user
        self.getPage('/')
        prev_session_id = self.session_id
        # Login
        b = {'login': 'admin', 'password': 'admin123'}
        self.getPage('/login/', method='POST', body=b)
        self.assertStatus('303 See Other')
        # Then a new session id is generated
        self.assertNotEqual(prev_session_id, self.session_id)
        prev_session_id = self.session_id
        # Get content of a page.
        self.getPage("/prefs/general")
        self.assertStatus('200 OK')
        # When logout
        self.getPage('/logout', method="POST")
        # Then a new session id is generated
        self.assertNotEqual(prev_session_id, self.session_id)
        # Then user is redirected to root page
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/')
        # Get content of a page.
        self.getPage("/prefs/general")
        self.assertStatus('303 See Other')
        self.assertHeaderItemValue('Location', self.baseurl + '/login/')
