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
Created on June 30, 2022

Module to test `user` model.

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""
import datetime
import os
from io import StringIO, open
from unittest.mock import MagicMock

import cherrypy
import pkg_resources

import rdiffweb.test
from rdiffweb.core import authorizedkeys
from rdiffweb.core.model import DuplicateSSHKeyError, RepoObject, Token, UserObject
from rdiffweb.core.passwd import check_password


class UserObjectTest(rdiffweb.test.WebCase):

    default_config = {
        'email-send-changed-notification': True,
    }

    def _read_ssh_key(self):
        """Readthe pub key from test packages"""
        filename = pkg_resources.resource_filename('rdiffweb.core.tests', 'test_publickey_ssh_rsa.pub')
        with open(filename, 'r', encoding='utf8') as f:
            return f.readline()

    def _read_authorized_keys(self):
        """Read the content of test_authorized_keys"""
        filename = pkg_resources.resource_filename('rdiffweb.core.tests', 'test_authorized_keys')
        with open(filename, 'r', encoding='utf8') as f:
            return f.read()

    def setUp(self):
        super().setUp()
        self.listener = MagicMock()
        cherrypy.engine.subscribe('access_token_added', self.listener.access_token_added, priority=50)
        cherrypy.engine.subscribe('queue_mail', self.listener.queue_mail, priority=50)
        cherrypy.engine.subscribe('user_added', self.listener.user_added, priority=50)
        cherrypy.engine.subscribe('user_attr_changed', self.listener.user_attr_changed, priority=50)
        cherrypy.engine.subscribe('user_deleted', self.listener.user_deleted, priority=50)
        cherrypy.engine.subscribe('user_login', self.listener.user_login, priority=50)
        cherrypy.engine.subscribe('user_password_changed', self.listener.user_password_changed, priority=50)

    def tearDown(self):
        cherrypy.engine.unsubscribe('access_token_added', self.listener.access_token_added)
        cherrypy.engine.unsubscribe('queue_mail', self.listener.queue_mail)
        cherrypy.engine.unsubscribe('user_added', self.listener.user_added)
        cherrypy.engine.unsubscribe('user_attr_changed', self.listener.user_attr_changed)
        cherrypy.engine.unsubscribe('user_deleted', self.listener.user_deleted)
        cherrypy.engine.unsubscribe('user_login', self.listener.user_login)
        cherrypy.engine.unsubscribe('user_password_changed', self.listener.user_password_changed)
        return super().tearDown()

    def test_add_user(self):
        """Add user to database."""
        userobj = UserObject.add_user('joe')
        self.assertIsNotNone(userobj)
        self.assertIsNotNone(UserObject.get_user('joe'))
        # Check if listener called
        self.listener.user_added.assert_called_once_with(userobj)

    def test_add_user_updated_by_listener(self):
        """Add user to database."""
        # Given a listener with side effet
        def change_user_obj(userobj):
            userobj.user_root = '/new/value'

        self.listener.user_added.side_effect = change_user_obj
        # When adding user
        userobj = UserObject.add_user('joe')
        self.assertIsNotNone(userobj)
        self.assertIsNotNone(UserObject.get_user('joe'))
        # Then lister get called
        self.listener.user_added.assert_called_once_with(userobj)
        # Then object was updated by listener
        self.assertEqual('/new/value', userobj.user_root)

    def test_add_user_with_duplicate(self):
        """Add user to database."""
        UserObject.add_user('denise')
        self.listener.user_added.reset_mock()
        with self.assertRaises(ValueError):
            UserObject.add_user('denise')
        # Check if listener called
        self.listener.user_added.assert_not_called()

    def test_add_user_with_password(self):
        """Add user to database with password."""
        userobj = UserObject.add_user('jo', 'password')
        self.assertIsNotNone(UserObject.get_user('jo'))
        # Check if listener called
        self.listener.user_added.assert_called_once_with(userobj)

    def test_delete_admin_user(self):
        # Trying to delete admin user should raise an error.
        userobj = UserObject.get_user('admin')
        with self.assertRaises(ValueError):
            userobj.delete()

    def test_users(self):
        # Check admin exists
        self.assertEqual(1, UserObject.query.count())
        # Create user.
        UserObject.add_user('annik')
        users = UserObject.query.all()
        self.assertEqual(2, len(users))
        self.assertEqual('annik', users[1].username)
        # Then 2 user exists
        self.assertEqual(2, UserObject.query.count())

    def test_get_user(self):
        # Create new user
        user = UserObject.add_user('bernie', 'my-password')
        user.user_root = self.testcases
        user.role = UserObject.ADMIN_ROLE
        user.email = 'bernie@gmail.com'
        user.refresh_repos()
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in user.repo_objs]))
        user.repo_objs[0].maxage = -1
        user.repo_objs[1].maxage = 3

        # Get user record.
        obj = UserObject.get_user('bernie')
        self.assertIsNotNone(obj)
        self.assertEqual('bernie', obj.username)
        self.assertEqual('bernie@gmail.com', obj.email)
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in obj.repo_objs]))
        self.assertEqual(self.testcases, obj.user_root)
        self.assertEqual(True, obj.is_admin)
        self.assertEqual(UserObject.ADMIN_ROLE, obj.role)

        # Get repo object
        self.assertEqual('broker-repo', obj.repo_objs[0].name)
        self.assertEqual(-1, obj.repo_objs[0].maxage)
        self.assertEqual('testcases', obj.repo_objs[1].name)
        self.assertEqual(3, obj.repo_objs[1].maxage)

    def test_get_user_with_invalid_user(self):
        self.assertIsNone(UserObject.get_user('invalid'))

    def test_get_set(self):
        user = UserObject.add_user('larry', 'password')

        self.assertEqual('', user.email)
        self.assertEqual([], user.repo_objs)
        self.assertEqual('', user.user_root)
        self.assertEqual(False, user.is_admin)
        self.assertEqual(UserObject.USER_ROLE, user.role)

        user.user_root = self.testcases
        user.refresh_repos()
        self.listener.user_attr_changed.assert_called_with(user, {'user_root': ('', self.testcases)})
        self.listener.user_attr_changed.reset_mock()
        user.role = UserObject.ADMIN_ROLE
        self.listener.user_attr_changed.assert_called_with(
            user, {'role': (UserObject.USER_ROLE, UserObject.ADMIN_ROLE)}
        )
        self.listener.user_attr_changed.reset_mock()
        user.email = 'larry@gmail.com'
        self.listener.user_attr_changed.assert_called_with(user, {'email': ('', 'larry@gmail.com')})
        self.listener.user_attr_changed.reset_mock()

        self.assertEqual('larry@gmail.com', user.email)
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in user.repo_objs]))
        self.assertEqual(self.testcases, user.user_root)
        self.assertEqual(True, user.is_admin)
        self.assertEqual(UserObject.ADMIN_ROLE, user.role)

    def test_set_password_update(self):
        # Given a user in database with a password
        userobj = UserObject.add_user('annik', 'password')
        self.listener.user_password_changed.reset_mock()
        # When updating the user's password
        userobj.set_password('new_password')
        # Then password is SSHA
        self.assertTrue(check_password('new_password', userobj.hash_password))
        # Check if listener called
        self.listener.user_password_changed.assert_called_once_with(userobj)

    def test_set_password_with_old_password(self):
        # Given a user in drabase with a password
        userobj = UserObject.add_user('john', 'password')
        self.listener.user_password_changed.reset_mock()
        # When updating the user's password with old_password
        userobj.set_password('new_password', old_password='password')
        # Then password is SSHA
        self.assertTrue(check_password('new_password', userobj.hash_password))
        # Check if listener called
        self.listener.user_password_changed.assert_called_once_with(userobj)

    def test_set_password_with_invalid_old_password(self):
        # Given a user in drabase with a password
        userobj = UserObject.add_user('foo', 'password')
        self.listener.user_password_changed.reset_mock()
        # When updating the user's password with wrong old_password
        # Then an exception is raised
        with self.assertRaises(ValueError):
            userobj.set_password('new_password', old_password='invalid')
        # Check if listener called
        self.listener.user_password_changed.assert_not_called()

    def test_delete_user(self):
        # Given an existing user in database
        userobj = UserObject.add_user('vicky')
        self.assertIsNotNone(UserObject.get_user('vicky'))
        # When deleting that user
        userobj.delete()
        # Then user it no longer in database
        self.assertIsNone(UserObject.get_user('vicky'))
        # Then listner was called
        self.listener.user_deleted.assert_called_once_with('vicky')

    def test_set_password_empty(self):
        """Expect error when trying to update password of invalid user."""
        userobj = UserObject.add_user('john')
        with self.assertRaises(ValueError):
            self.assertFalse(userobj.set_password(''))

    def test_disk_quota(self):
        """
        Just make a call to the function.
        """
        userobj = UserObject.get_user(self.USERNAME)
        userobj.disk_quota

    def test_disk_usage(self):
        """
        Just make a call to the function.
        """
        userobj = UserObject.get_user(self.USERNAME)
        disk_usage = userobj.disk_usage
        self.assertIsInstance(disk_usage, int)

    def test_add_authorizedkey_without_file(self):
        """
        Add an ssh key for a user without an authorizedkey file.
        """
        # Read the pub key
        key = self._read_ssh_key()
        # Add the key to the user
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_authorizedkey(key)

        # validate
        keys = list(userobj.authorizedkeys)
        self.assertEqual(1, len(keys), "expecting one key")
        self.assertEqual("3c:99:ed:a7:82:a8:71:09:2c:15:3d:78:4a:8c:11:99", keys[0].fingerprint)

    def test_add_authorizedkey_duplicate(self):
        # Read the pub key
        key = self._read_ssh_key()
        # Add the key to the user
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_authorizedkey(key)
        # Add the same key
        with self.assertRaises(DuplicateSSHKeyError):
            userobj.add_authorizedkey(key)

    def test_add_authorizedkey_with_file(self):
        """
        Add an ssh key for a user with an authorizedkey file.
        """
        userobj = UserObject.get_user(self.USERNAME)

        # Create empty authorized_keys file
        os.mkdir(os.path.join(userobj.user_root, '.ssh'))
        filename = os.path.join(userobj.user_root, '.ssh', 'authorized_keys')
        open(filename, 'a').close()

        # Read the pub key
        key = self._read_ssh_key()
        userobj.add_authorizedkey(key)

        # Validate
        with open(filename, 'r') as fh:
            self.assertEqual(key, fh.read())

    def test_delete_authorizedkey_without_file(self):
        """
        Remove an ssh key for a user without authorizedkey file.
        """
        # Update user with ssh keys.
        data = self._read_authorized_keys()
        userobj = UserObject.get_user(self.USERNAME)
        for k in authorizedkeys.read(StringIO(data)):
            try:
                userobj.add_authorizedkey(k.getvalue())
            except ValueError:
                # Some ssh key in the testing file are not valid.
                pass

        # Get the keys
        keys = list(userobj.authorizedkeys)
        self.assertEqual(2, len(keys))

        # Remove a key
        userobj.delete_authorizedkey("9a:f1:69:3c:bc:5a:cd:02:5e:33:bc:cd:c0:01:eb:4c")

        # Validate
        keys = list(userobj.authorizedkeys)
        self.assertEqual(1, len(keys))

    def test_delete_authorizedkey_with_file(self):
        """
        Remove an ssh key for a user with authorizedkey file.
        """
        # Create authorized_keys file
        data = self._read_authorized_keys()
        userobj = UserObject.get_user(self.USERNAME)
        os.mkdir(os.path.join(userobj.user_root, '.ssh'))
        filename = os.path.join(userobj.user_root, '.ssh', 'authorized_keys')
        with open(filename, 'w') as f:
            f.write(data)

        # Get the keys
        keys = list(userobj.authorizedkeys)
        self.assertEqual(5, len(keys))

        # Remove a key
        userobj.delete_authorizedkey("9a:f1:69:3c:bc:5a:cd:02:5e:33:bc:cd:c0:01:eb:4c")

        # Validate
        keys = list(userobj.authorizedkeys)
        self.assertEqual(4, len(keys))

    def test_repo_objs(self):
        # Given a user with a list of repositories
        userobj = UserObject.get_user(self.USERNAME)
        repos = sorted(userobj.repo_objs, key=lambda r: r.name)
        self.assertEqual(['broker-repo', 'testcases'], [r.name for r in repos])
        # When deleting a repository empty list
        repos[1].delete()
        # Then the repository is removed from the list.
        self.assertEqual(['broker-repo'], sorted([r.name for r in userobj.repo_objs]))

    def test_refresh_repos_without_delete(self):
        # Given a user with invalid repositories
        userobj = UserObject.get_user(self.USERNAME)
        RepoObject.query.delete()
        RepoObject(userid=userobj.userid, repopath='invalid').add()
        self.assertEqual(['invalid'], sorted([r.name for r in userobj.repo_objs]))
        # When updating the repository list without deletion
        userobj.refresh_repos()
        # Then the list invlaid the invalid repo and new repos
        self.assertEqual(['broker-repo', 'invalid', 'testcases'], sorted([r.name for r in userobj.repo_objs]))

    def test_refresh_repos_with_delete(self):
        # Given a user with invalid repositories
        userobj = UserObject.get_user(self.USERNAME)
        RepoObject.query.delete()
        RepoObject(userid=userobj.userid, repopath='invalid').add()
        self.assertEqual(['invalid'], sorted([r.name for r in userobj.repo_objs]))
        # When updating the repository list without deletion
        userobj.refresh_repos(delete=True)
        # Then the list invlaid the invalid repo and new repos
        userobj.expire()
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in userobj.repo_objs]))

    def test_refresh_repos_with_single_repo(self):
        # Given a user with invalid repositories
        userobj = UserObject.get_user(self.USERNAME)
        userobj.user_root = os.path.join(self.testcases, 'testcases')
        # When updating the repository list without deletion
        userobj.refresh_repos(delete=True)
        # Then the list invlaid the invalid repo and new repos
        userobj.expire()
        self.assertEqual([''], sorted([r.name for r in userobj.repo_objs]))

    def test_add_access_token(self):
        # Given a user with an email
        userobj = UserObject.get_user(self.USERNAME)
        userobj.email = 'test@examples.com'
        userobj.add()
        # When adding a new token
        token = userobj.add_access_token('test')
        # Then a new token get created
        self.assertTrue(token)
        tokenobj = Token.query.filter(Token.userid == userobj.userid).first()
        self.assertTrue(tokenobj)
        self.assertEqual(None, tokenobj.expiration_time)
        self.assertEqual(None, tokenobj.access_time)
        # Then an email is sent to the user.
        self.listener.access_token_added.assert_called_once_with(userobj, 'test')
        self.listener.queue_mail.assert_called_once()

    def test_add_access_token_duplicate_name(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test')
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When adding a new token with the same name
        with self.assertRaises(ValueError):
            userobj.add_access_token('test')
        # Then token is not created
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # Then an email is not sent.
        self.listener.access_token_added.assert_called_once_with(userobj, 'test')

    def test_delete_access_token(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test')
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When deleting an access token
        userobj.delete_access_token('test')
        # Then Token get deleted
        self.assertEqual(0, Token.query.filter(Token.userid == userobj.userid).count())

    def test_delete_access_token_invalid(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test')
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When deleting an invalid access token
        with self.assertRaises(ValueError):
            userobj.delete_access_token('invalid')
        # Then Token not deleted
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())

    def test_delete_user_remove_access_tokens(self):
        # Given a user with an existing token
        userobj = UserObject.add_user('testuser', 'password')
        userobj.add_access_token('test')
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When deleting the user
        userobj.delete()
        # Then Token get deleted
        self.assertEqual(0, Token.query.filter(Token.userid == userobj.userid).count())

    def test_verify_access_token(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        token = userobj.add_access_token('test')
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When validating the token
        # Then token is valid
        self.assertTrue(userobj.validate_access_token(token))

    def test_verify_access_token_with_expired(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        token = userobj.add_access_token(
            'test', expiration_time=datetime.datetime.now() - datetime.timedelta(seconds=1)
        )
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When validating the token
        # Then token is invalid
        self.assertFalse(userobj.validate_access_token(token))
        # Then token get removed
        self.assertEqual(0, Token.query.filter(Token.userid == userobj.userid).count())

    def test_verify_access_token_with_invalid(self):
        # Given a user with an existing token
        userobj = UserObject.get_user(self.USERNAME)
        userobj.add_access_token('test', expiration_time=datetime.datetime.now())
        self.assertEqual(1, Token.query.filter(Token.userid == userobj.userid).count())
        # When validating the token
        # Then token is invalid
        self.assertFalse(userobj.validate_access_token('invalid'))


class UserObjectWithAdminPassword(rdiffweb.test.WebCase):

    # password: test
    default_config = {'admin-password': '{SSHA}wbSK4hlEX7mtGJplFi2oN6ABm6Y3Bo1e'}

    def setUp(self):
        # Do nothing - We need to skip the default setup to avoid deleting the records.
        pass

    def test_create_admin_user(self):
        # Given admin-password is configure
        # When database get created
        # Then admin user get created with 'test' password
        userobj = UserObject.get_user(self.USERNAME)
        self.assertIsNotNone(userobj)
        self.assertEqual('{SSHA}wbSK4hlEX7mtGJplFi2oN6ABm6Y3Bo1e', userobj.hash_password)
        self.assertTrue(check_password('test', userobj.hash_password))

    def test_set_password(self):
        # Given admin-password is configure
        # When trying to update admin password
        # Then an exception is raised
        userobj = UserObject.get_user(self.USERNAME)
        with self.assertRaises(ValueError):
            userobj.set_password('newpassword')
