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


import rdiffweb.test
from rdiffweb.core.model import SessionObject, UserObject


class PagePrefSessionTest(rdiffweb.test.WebCase):
    PREFS = "/prefs/session"

    login = True

    def test_get_page(self):
        # When querying the page
        self.getPage(self.PREFS)
        # Then the page is returned with sessions
        self.assertStatus(200)
        self.assertInBody('Active Sessions')
        self.assertInBody('current session')
        # Then sessionid are not exposed
        self.assertNotInBody(self.session_id)

    def test_get_page_persistent(self):
        # Given a persistent user session
        self.cookies = None
        self.getPage(
            '/login/',
            method='POST',
            body={
                'login': self.USERNAME,
                'password': self.PASSWORD,
                'persistent': '1',
            },
        )
        self.assertStatus(303)
        # When listing the action session
        self.getPage(self.PREFS)
        self.assertStatus(200)
        # Then a badge identify the persistent session.
        self.assertInBody('current session')
        self.assertInBody('persistent')

    def test_revoke_current_session(self):
        # Given a user authenticated
        self.assertEqual(1, len(SessionObject.query.all()))
        session_number = SessionObject.query.filter(SessionObject.session_id == self.session_id).first().number
        # When trying to revoke current session
        self.getPage(self.PREFS, method='POST', body={'action': 'delete', 'number': str(session_number)})
        self.assertStatus(200)
        # Then an error is returned
        self.assertInBody('You cannot revoke your current session.')
        self.assertEqual(1, len(SessionObject.query.all()))

    def test_revoke_invalid_session(self):
        # Given a user authenticated
        self.assertEqual(1, len(SessionObject.query.all()))
        # When trying to revoke current session
        self.getPage(self.PREFS, method='POST', body={'action': 'delete', 'number': str(34)})
        self.assertStatus(200)
        # Then an error is returned
        self.assertInBody("The given session cannot be removed because it cannot be found.")
        self.assertEqual(1, len(SessionObject.query.all()))

    def test_revoke_another_user_session(self):
        # Given another user session
        new_user = UserObject.add_user('test', 'test123')
        new_user.commit()
        prev_cookies = self.cookies
        del self.cookies
        self.getPage("/login/", method='POST', body={'login': 'test', 'password': 'test123'})
        second_session_id = self.session_id
        self.cookies = prev_cookies
        self.assertEqual(2, len(SessionObject.query.all()))
        session_number = SessionObject.query.filter(SessionObject.session_id == second_session_id).first().number
        # When trying to revoke another user session
        self.getPage(self.PREFS, method='POST', body={'action': 'delete', 'number': str(session_number)})
        self.assertStatus(200)
        # Then an error is returned
        self.assertInBody("The given session cannot be removed because it cannot be found.")
        self.assertEqual(2, len(SessionObject.query.all()))

    def test_revoke_session(self):
        # Given a user with multiple sessionid
        prev_cookies = self.cookies
        del self.cookies
        self.getPage("/login/", method='POST', body={'login': self.USERNAME, 'password': self.PASSWORD})
        second_session_id = self.session_id
        self.cookies = prev_cookies
        self.assertEqual(2, len(SessionObject.query.all()))
        session_number = SessionObject.query.filter(SessionObject.session_id == second_session_id).first().number
        # When trying to revoke current session
        self.getPage(self.PREFS, method='POST', body={'action': 'delete', 'number': str(session_number)})
        self.assertStatus(200)
        # Then the session is removed
        self.assertInBody("The session was successfully revoked.")
        self.assertEqual(1, len(SessionObject.query.all()))
