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

import datetime
from unittest.mock import MagicMock

import cherrypy

import rdiffweb.test
from rdiffweb.core.model import DbSession, UserObject


class MfaPageTest(rdiffweb.test.WebCase):

    # Authenticated by default.
    login = True

    def _get_code(self):
        # Register an email listeer to capture email send
        self.listener = MagicMock()
        cherrypy.engine.subscribe('queue_mail', self.listener.queue_email, priority=50)
        # Query MFA page to generate a code
        self.getPage("/mfa/")
        self.assertStatus(200)
        self.assertInBody("A new verification code has been sent to your email.")
        # Extract code from email between <strong> and </strong>
        self.listener.queue_email.assert_called_once()
        message = self.listener.queue_email.call_args[1]['message']
        return message.split('<strong>', 1)[1].split('</strong>')[0]

    def setUp(self):
        super().setUp()
        # Enabled MFA for all test cases
        userobj = UserObject.get_user(self.USERNAME)
        userobj.mfa = UserObject.ENABLED_MFA
        userobj.email = 'admin@example.com'
        userobj.commit()

    def test_get_without_login(self):
        # Given an unauthenticated user
        self.getPage("/logout", method="POST")
        self.assertStatus(303)
        # When requesting /mfa/
        self.getPage("/mfa/")
        # Then user is redirected to /login/
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/login/')

    def test_get_with_mfa_disabled(self):
        # Given an authenticated user with MFA Disable
        userobj = UserObject.get_user(self.USERNAME)
        userobj.mfa = UserObject.DISABLED_MFA
        userobj.commit()
        self.getPage("/")
        self.assertStatus(200)
        # When requesting /mfa/ page
        self.getPage("/mfa/")
        # Then user is redirected to root page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/')

    def test_get_with_user_without_email(self):
        # Given an authenticated user without email.
        userobj = UserObject.get_user(self.USERNAME)
        userobj.email = ''
        userobj.commit()
        # When requesting /mfa/ page
        self.getPage("/mfa/")
        # Then user is redirected to root page
        self.assertStatus(200)
        self.assertInBody(
            "Multi-factor authentication is enabled for your account, but your account does not have a valid email address to send the verification code to. Check your account settings with your administrator."
        )

    def test_get_with_trusted(self):
        # Given an authenticated user with MFA enabled and already verified
        session = DbSession(id=self.session_id)
        session.load()
        session['_auth_mfa_username'] = self.USERNAME
        session['_auth_mfa_time'] = session.now()
        session['_auth_mfa_trusted_ip_list'] = ['127.0.0.1']
        session.save()
        # When requesting /mfa/ page when we are already trusted
        self.getPage("/mfa/")
        # Then user is redirected to root page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/')

    def test_get_with_trusted_expired(self):
        # Given an authenticated user with MFA enabled and already verified
        session = DbSession(id=self.session_id)
        session.load()
        session['_auth_mfa_username'] = self.USERNAME
        session['_auth_mfa_time'] = session.now() - datetime.timedelta(minutes=session.timeout)
        session.save()
        # When requesting /mfa/ page
        self.getPage("/mfa/")
        # Then an email get send with a new code
        self.assertStatus(200)
        self.assertInBody("A new verification code has been sent to your email.")

    def test_get_with_trusted_different_ip(self):
        # Given an authenticated user with MFA enabled and already verified
        session = DbSession(id=self.session_id)
        session.load()
        session['_auth_mfa_username'] = self.USERNAME
        session['_auth_mfa_time'] = session.now()
        session.save()
        # When requesting /mfa/ page from a different ip
        self.getPage("/mfa/", headers=[('X-Forwarded-For', '10.255.14.23')])
        # Then an email get send with a new code
        self.assertStatus(200)
        self.assertInBody("A new verification code has been sent to your email.")

    def test_get_without_verified(self):
        # Given an authenticated user With MFA enabled
        # When requesting /mfa/ page
        self.getPage("/mfa/")
        # Then an email get send with a new code
        self.assertStatus(200)
        self.assertInBody("A new verification code has been sent to your email.")

    def test_verify_code_valid(self):
        prev_session_id = self.session_id
        # Given an authenticated user With MFA enabled
        code = self._get_code()
        # When sending a valid verification code
        self.getPage("/mfa/", method='POST', body={'code': code, 'submit': '1'})
        # Then a new session_id is generated
        self.assertNotEqual(prev_session_id, self.session_id)
        # Then user is redirected to root page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/')
        # Then user has access
        self.getPage("/")
        self.assertStatus(200)

    def test_verify_code_invalid(self):
        # Given an authenticated user With MFA enabled
        # When sending an invalid verification code
        self.getPage("/mfa/", method='POST', body={'code': '1234567', 'submit': '1'})
        # Then an error get displayed to the user
        self.assertStatus(200)
        self.assertInBody("Invalid verification code.")

    def test_verify_code_expired(self):
        # Given an authenticated user With MFA enabled
        code = self._get_code()
        # When sending a valid verification code that expired
        session = DbSession(id=self.session_id)
        session.load()
        session['_auth_mfa_code_time'] = session.now() - datetime.timedelta(minutes=session.timeout + 1)
        session.save()
        self.getPage("/mfa/", method='POST', body={'code': code, 'submit': '1'})
        # Then a new code get generated.
        self.assertStatus(200)
        self.assertInBody("Invalid verification code.")
        self.assertInBody("A new verification code has been sent to your email.")

    def test_verify_code_invalid_after_3_tentative(self):
        # Given an authenticated user With MFA
        self._get_code()
        # When user enter an invalid verification code 3 times
        self.getPage("/mfa/", method='POST', body={'code': '1234567', 'submit': '1'})
        self.assertStatus(200)
        self.getPage("/mfa/", method='POST', body={'code': '1234567', 'submit': '1'})
        self.assertStatus(200)
        self.getPage("/mfa/", method='POST', body={'code': '1234567', 'submit': '1'})
        # Then an error get displayed to the user
        self.assertStatus(200)
        self.assertInBody("Invalid verification code.")
        self.assertInBody("A new verification code has been sent to your email.")

    def test_resend_code(self):
        # Given an authenticated user With MFA enabled with an existing code
        self._get_code()
        # When user request a new code
        self.getPage("/mfa/", method='POST', body={'resend_code': '1'})
        # Then a new code is sent to the user by email
        self.assertInBody("A new verification code has been sent to your email.")

    def test_redirect_to_original_url(self):
        # When querying a page that required mfa
        self.getPage('/prefs/general')
        # Then user is redirected to mfa page
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/mfa/')
        # When providing verification code
        code = self._get_code()
        self.getPage("/mfa/", method='POST', body={'code': code, 'submit': '1'})
        # Then user is redirected to original url
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/prefs/general')

    def test_login_persistent_when_login_timout(self):
        prev_session_id = self.session_id
        # Given a user authenticated with MFA with "login_persistent"
        code = self._get_code()
        self.getPage("/mfa/", method='POST', body={'code': code, 'submit': '1', 'persistent': '1'})
        self.assertStatus(303)
        self.getPage("/")
        self.assertStatus(200)
        self.assertNotEqual(prev_session_id, self.session_id)
        session = DbSession(id=self.session_id)
        session.load()
        self.assertTrue(session['login_persistent'])
        # When the login_time expired (after 15 min)
        session['login_time'] = session.now() - datetime.timedelta(minutes=15, seconds=1)
        session.save()
        # Then next query redirect user to same page (by mfa)
        self.getPage("/prefs/general")
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/prefs/general')
        self.getPage("/prefs/general")
        # Then user is redirected to /login/ page (by auth_form)
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/login/')
        prev_session_id = self.session_id
        # When user enter valid username password
        self.getPage("/login/", method='POST', body={'login': self.USERNAME, 'password': self.PASSWORD})
        self.assertNotEqual(prev_session_id, self.session_id)
        # Then user is redirected to original url
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/prefs/general')
        self.getPage("/")
        self.assertStatus(200)
        self.assertInBody('Repositories')

    def test_login_persistent_when_mfa_timeout(self):
        prev_session_id = self.session_id
        # Given a user authenticated with MFA with "login_persistent"
        code = self._get_code()
        self.getPage("/mfa/", method='POST', body={'code': code, 'submit': '1', 'persistent': '1'})
        self.assertStatus(303)
        self.getPage("/")
        self.assertStatus(200)
        self.assertNotEqual(prev_session_id, self.session_id)
        session = DbSession(id=self.session_id)
        session.load()
        self.assertTrue(session['login_persistent'])
        # When the mfa verification timeout (after 30 days)
        session['_auth_mfa_time'] = session.now() - datetime.timedelta(days=30, seconds=1)
        session.save()
        # Then next query redirect user to mfa page
        self.getPage("/prefs/general")
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/mfa/')
        # When user enter valid code
        code = self._get_code()
        self.getPage("/mfa/", method='POST', body={'code': code, 'submit': '1', 'persistent': '1'})
        # Then user is redirected to original page.
        self.assertStatus(303)
        self.assertHeaderItemValue('Location', self.baseurl + '/prefs/general')
        self.getPage("/")
        self.assertStatus(200)
        self.assertInBody('Repositories')


class MfaPageWithWelcomeMsgTest(rdiffweb.test.WebCase):

    login = True

    default_config = {'welcomemsg': 'default message', 'welcomemsg[fr]': 'french message'}

    def setUp(self):
        super().setUp()
        # Enabled MFA for all test cases
        userobj = UserObject.get_user(self.USERNAME)
        userobj.mfa = UserObject.ENABLED_MFA
        userobj.email = 'admin@example.com'
        userobj.commit()

    def test_getpage_default(self):
        # Given a user with MFA enabled
        # When querying the mfa page
        self.getPage('/mfa/', headers=[("Accept-Language", "it")])
        # Then page is return without error with the custom welcome message
        self.assertStatus('200 OK')
        self.assertInBody('default message')

    def test_getpage_french(self):
        # Given a user with MFA enabled
        # When querying the mfa page in french
        self.getPage('/mfa/', headers=[("Accept-Language", "fr")])
        # Then page is return without error with the custom welcome message in french
        self.assertStatus('200 OK')
        self.assertInBody('french message')
