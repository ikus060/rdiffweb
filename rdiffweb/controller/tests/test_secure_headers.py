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
Created on Oct 20, 2021

@author: Patrik Dufresne
"""
from parameterized import parameterized

import rdiffweb.test


class SecureHeadersTest(rdiffweb.test.WebCase):

    login = True

    def test_cookie_samesite_lax(self):
        # Given a request made to rdiffweb
        # When receiving the response
        self.getPage('/')
        # Then the header contains Set-Cookie with SameSite=Lax
        cookie = self.assertHeader('Set-Cookie')
        self.assertIn('SameSite=Lax', cookie)

    def test_cookie_samesite_lax_without_session(self):
        # Given not a client sending no cookie
        self.cookies = None
        # When a query is made to a static path (without session)
        self.getPage('/static/blue.css')
        # Then Set-Cookie is not defined.
        self.assertNoHeader('Set-Cookie')

    def test_cookie_with_https(self):
        # Given an https request made to rdiffweb
        self.getPage('/', headers=[('X-Forwarded-Proto', 'https')])
        # When receiving the response
        self.assertStatus(200)
        # Then the header contains Set-Cookie with Secure
        cookie = self.assertHeader('Set-Cookie')
        self.assertIn('Secure', cookie)

    @parameterized.expand(
        [
            ('/invalid', 404),
            ('/browse/invalid', 404),
            ('/login', 301),
            ('/logout', 405),
        ]
    )
    def test_cookie_with_https_http_error(self, url, expected_error_code):
        # Given an https request made to rdiffweb
        self.getPage(url, headers=[('X-Forwarded-Proto', 'https')])
        # When receiving the response
        self.assertStatus(expected_error_code)
        # Then the header contains Set-Cookie with Secure
        cookie = self.assertHeader('Set-Cookie')
        self.assertIn('Secure', cookie)

    def test_cookie_with_http(self):
        # Given an https request made to rdiffweb
        self.getPage('/')
        # When receiving the response
        # Then the header contains Set-Cookie with Secure
        cookie = self.assertHeader('Set-Cookie')
        self.assertNotIn('Secure', cookie)

    def test_get_with_wrong_origin(self):
        # Given a GET request made to rdiffweb
        # When the request is made using a different origin
        self.getPage('/', headers=[('Origin', 'http://www.examples.com')])
        # Then the response status it 200 OK.
        self.assertStatus(200)

    def test_post_with_wrong_origin(self):
        # Given a POST request made to rdiffweb
        # When the request is made using a different origin
        self.getPage('/', headers=[('Origin', 'http://www.examples.com')], method='POST')
        # Then the request is refused with 403 Forbiden
        self.assertStatus(403)
        self.assertInBody('Unexpected Origin header')

    def test_post_with_prefixed_origin(self):
        # Given a POST request made to rdiffweb
        # When the request is made using a different origin
        base = 'http://%s:%s' % (self.HOST + 'anything.com', self.PORT)
        self.getPage('/dashboard/', headers=[('Origin', base)], method='POST')
        # Then the request is accepted with 200 OK
        self.assertStatus(403)
        self.assertInBody('Unexpected Origin header')

    def test_post_with_valid_origin(self):
        # Given a POST request made to rdiffweb
        # When the request is made using a different origin
        base = 'http://%s:%s' % (self.HOST, self.PORT)
        self.getPage('/', headers=[('Origin', base)], method='POST')
        # Then the request is accepted with 200 OK
        self.assertStatus(200)

    def test_post_without_origin(self):
        # Given a POST request made to rdiffweb
        # When the request is made without an origin
        self.getPage('/', method='POST')
        # Then the request is accepted with 200 OK
        self.assertStatus(200)

    def test_clickjacking_defense(self):
        # Given a POST request made to rdiffweb
        # When the request is made without an origin
        self.getPage('/')
        # Then the request is accepted with 200 OK
        self.assertStatus(200)
        self.assertHeaderItemValue('X-Frame-Options', 'DENY')

    def test_no_cache(self):
        # Given a POST request made to rdiffweb
        # When the request is made without an origin
        self.getPage('/')
        # Then the request is accepted with 200 OK
        self.assertStatus(200)
        self.assertHeaderItemValue('Cache-control', 'no-cache')
        self.assertHeaderItemValue('Cache-control', 'no-store')
        self.assertHeaderItemValue('Cache-control', 'must-revalidate')
        self.assertHeaderItemValue('Cache-control', 'max-age=0')
        self.assertHeaderItemValue('Pragma', 'no-cache')
        self.assertHeaderItemValue('Expires', '0')

    def test_no_cache_with_static(self):
        self.getPage('/static/js/rdiffweb.js')
        # Then the request is accepted with 200 OK
        self.assertStatus(200)
        self.assertNoHeader('Cache-control')
        self.assertNoHeader('Pragma')
        self.assertNoHeader('Expires')

    def test_referrer_policy(self):
        # Given a POST request made to rdiffweb
        # When the request is made without an origin
        self.getPage('/')
        # Then the request is accepted with 200 OK
        self.assertStatus(200)
        self.assertHeaderItemValue('Referrer-Policy', 'same-origin')

    def test_nosniff(self):
        # Given a POST request made to rdiffweb
        # When the request is made without an origin
        self.getPage('/')
        # Then the request is accepted with 200 OK
        self.assertStatus(200)
        self.assertHeaderItemValue('X-Content-Type-Options', 'nosniff')

    def test_xss_protection(self):
        # Given a POST request made to rdiffweb
        # When the request is made without an origin
        self.getPage('/')
        # Then the request is accepted with 200 OK
        self.assertStatus(200)
        self.assertHeaderItemValue('X-XSS-Protection', '1; mode=block')

    def test_content_security_policy(self):
        # Given a POST request made to rdiffweb
        # When the request is made without an origin
        self.getPage('/')
        # Then the request is accepted with 200 OK
        self.assertStatus(200)
        self.assertHeaderItemValue(
            'Content-Security-Policy',
            "default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'",
        )

    def test_strict_transport_security(self):
        # Given a POST request made to rdiffweb
        # When the request is made without an origin
        self.getPage('/', headers=[('X-Forwarded-Proto', 'https')])
        # Then the request is accepted with 200 OK
        self.assertStatus(200)
        self.assertHeaderItemValue('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
