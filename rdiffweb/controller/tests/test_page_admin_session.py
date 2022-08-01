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


import rdiffweb.test
from rdiffweb.core.model import DbSession, SessionObject


class AdminSessionTest(rdiffweb.test.WebCase):

    PAGE = "/admin/session"

    login = True

    def test_get_page(self):
        # When querying the page
        self.getPage(self.PAGE)
        # Then the page is returned with sessions
        self.assertStatus(200)
        self.assertInBody('Active Sessions')
        self.assertInBody('current session')
        # Then sessionid are not exposed
        self.assertNotInBody(self.session_id)

    def test_revoke_current_session(self):
        # Given a user authenticated
        self.assertEqual(1, len(SessionObject.query.all()))
        session_number = SessionObject.query.filter(SessionObject.id == self.session_id).first().number
        # When trying to revoke current session
        self.getPage(self.PAGE, method='POST', body={'action': 'delete', 'number': str(session_number)})
        self.assertStatus(200)
        # Then an error is returned
        self.assertInBody('You cannot revoke your current session.')
        self.assertEqual(1, len(SessionObject.query.all()))

    def test_revoke_invalid_session(self):
        # Given a user authenticated
        self.assertEqual(1, len(SessionObject.query.all()))
        # When trying to revoke current session
        self.getPage(self.PAGE, method='POST', body={'action': 'delete', 'number': str(34)})
        self.assertStatus(200)
        # Then an error is returned
        self.assertInBody("The given session cannot be removed because it cannot be found.")
        self.assertEqual(1, len(SessionObject.query.all()))

    def test_revoke_another_user_session(self):
        # Given another user session
        session = DbSession()
        session.load()
        session['_cp_username'] = 'test'
        session.save()
        self.assertEqual(2, len(SessionObject.query.all()))
        session_number = SessionObject.query.filter(SessionObject.id == session.id).first().number
        self.session.commit()
        # When trying to revoke another user session
        self.getPage(self.PAGE, method='POST', body={'action': 'delete', 'number': str(session_number)})
        self.assertStatus(200)
        # Then the session is revoke.
        self.assertInBody("The session was successfully revoked.")
        self.assertEqual(1, len(SessionObject.query.all()))

    def test_revoke_session(self):
        # Given a user with multiple sessionid
        session = DbSession()
        session.load()
        session['_cp_username'] = self.USERNAME
        session.save()
        self.assertEqual(2, len(SessionObject.query.all()))
        session_number = SessionObject.query.filter(SessionObject.id == session.id).first().number
        self.session.commit()
        # When trying to revoke current session
        self.getPage(self.PAGE, method='POST', body={'action': 'delete', 'number': str(session_number)})
        self.assertStatus(200)
        # Then the session is removed
        self.assertInBody("The session was successfully revoked.")
        self.assertEqual(1, len(SessionObject.query.all()))
