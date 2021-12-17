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
Created on Oct 14, 2015

Module to test `user` module.

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""

import os
from io import StringIO, open
from unittest.mock import MagicMock

import pkg_resources
from rdiffweb.core import RdiffError, authorizedkeys
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.store import (_REPOS, ADMIN_ROLE, MAINTAINER_ROLE,
                                 USER_ROLE, DuplicateSSHKeyError,
                                 IUserChangeListener)
from rdiffweb.test import AppTestCase


def _ldap_user(name, password='password', email=None):
    """Create ldap entry to be mock."""
    assert isinstance(name, str)
    assert isinstance(password, str)
    data = {
        'uid': [name],
        'cn': [name],
        'userPassword': [password],
        'sAMAccountName': [name],
        'objectClass': ['person', 'organizationalPerson', 'inetOrgPerson', 'posixAccount']
    }
    if email:
        data['mail'] = [email]
    return ('uid=%s,ou=People,dc=nodomain' % (name), data)


class AbstractStoreTest(AppTestCase):
    """
    Abstract class used to test store module.
    """

    def setUp(self):
        super().setUp()
        self.mlistener = IUserChangeListener(self.app)
        self.mlistener.user_added = MagicMock()
        self.mlistener.user_attr_changed = MagicMock()
        self.mlistener.user_deleted = MagicMock()
        self.mlistener.user_logined = MagicMock()
        self.mlistener.user_password_changed = MagicMock()


class AbstractLdapStoreTest(AbstractStoreTest):
    """
    Abstract class used to test store module with a mock ldap.
    """

    basedn = ('dc=nodomain', {
        'dc': ['nodomain'],
        'o': ['nodomain']})
    people = ('ou=People,dc=nodomain', {
        'ou': ['People'],
        'objectClass': ['organizationalUnit']})

    # This is the content of our mock LDAP directory. It takes the form
    # {dn: {attr: [value, ...], ...}, ...}.
    ldap_directory = dict([
        basedn,
        people,
        _ldap_user('annik'),
        _ldap_user('bob'),
        _ldap_user('foo'),
        _ldap_user('jeff'),
        _ldap_user('john'),
        _ldap_user('karl'),
        _ldap_user('kim'),
        _ldap_user('larry'),
        _ldap_user('mike'),
        _ldap_user('tony'),
        _ldap_user('vicky'),
        _ldap_user('userwithemail', email='user@example.com'),
    ])

    default_config = {
        'LdapUri': '__default__',
        'LdapBaseDn': 'dc=nodomain',
    }

    def setUp(self):
        # Original setup
        super().setUp()
        # Get reference to LdapStore
        self.ldapstore = self.app.store._ldap_store
        # Create fake listener
        self.mlistener = IUserChangeListener(self.app)
        self.mlistener.user_added = MagicMock()
        self.mlistener.user_attr_changed = MagicMock()
        self.mlistener.user_deleted = MagicMock()
        self.mlistener.user_logined = MagicMock()
        self.mlistener.user_password_changed = MagicMock()


class StoreTest(AbstractStoreTest):

    def test_add_user(self):
        """Add user to database."""
        userobj = self.app.store.add_user('joe')
        self.assertIsNotNone(userobj)
        self.assertIsNotNone(self.app.store.get_user('joe'))
        # Check if listener called
        self.mlistener.user_added.assert_called_once_with(userobj, None)

    def test_add_user_with_duplicate(self):
        """Add user to database."""
        userobj = self.app.store.add_user('denise')
        with self.assertRaises(RdiffError):
            self.app.store.add_user('denise')
        # Check if listener called
        self.mlistener.user_added.assert_called_once_with(userobj, None)

    def test_add_user_with_password(self):
        """Add user to database with password."""
        userobj = self.app.store.add_user('jo', 'password')
        self.assertIsNotNone(self.app.store.get_user('jo'))
        self.assertTrue(self.app.store.login('jo', 'password'))
        # Check if listener called
        self.mlistener.user_added.assert_called_once_with(userobj, None)

    def test_delete_admin_user(self):
        # Trying to delete admin user should raise an error.
        userobj = self.app.store.get_user('admin')
        with self.assertRaises(ValueError):
            userobj.delete()

    def test_delete_user(self):
        # Create user
        userobj = self.app.store.add_user('vicky', 'password')
        self.assertIsNotNone(self.app.store.get_user('vicky'))
        # Delete user
        userobj.delete()
        self.assertIsNone(self.app.store.get_user('vicky'))
        # Check if listener called
        self.mlistener.user_deleted.assert_called_once_with('vicky')

    def test_get_repo(self):
        user = self.app.store.add_user('bernie', 'my-password')
        user.user_root = self.app.testcases

        # Get as bernie
        repo_obj = self.app.store.get_repo('bernie/testcases', user)
        self.assertEqual('testcases', repo_obj.name)
        self.assertEqual('bernie', repo_obj.owner)

    def test_get_repo_as_other_user(self):
        user = self.app.store.add_user('bernie', 'my-password')
        user.user_root = self.app.testcases
        self.app.store.get_repo('bernie/testcases', user)

        # Get as otheruser
        other = self.app.store.add_user('other')
        with self.assertRaises(AccessDeniedError):
            self.app.store.get_repo('bernie/testcases', other)

    def test_get_repo_as_admin(self):
        user = self.app.store.add_user('bernie', 'my-password')
        user.user_root = self.app.testcases

        # Get as admin
        other = self.app.store.add_user('other')
        other.role = ADMIN_ROLE
        repo_obj3 = self.app.store.get_repo('bernie/testcases', other)
        self.assertEqual('testcases', repo_obj3.name)
        self.assertEqual('bernie', repo_obj3.owner)

    def test_get_repo_with_user(self):
        user = self.app.store.add_user('other', 'my-password')
        with self.assertRaises(DoesNotExistError):
            user.get_repo('testcases')

    def test_get_user(self):
        """
        Test user record.
        """
        # Create new user
        user = self.app.store.add_user('bernie', 'my-password')
        user.user_root = self.app.testcases
        user.role = ADMIN_ROLE
        user.email = 'bernie@gmail.com'
        user.repo_objs[0].maxage = -1
        user.repo_objs[1].maxage = 3

        # Get user record.
        obj = self.app.store.get_user('bernie')
        self.assertIsNotNone(obj)
        self.assertEqual('bernie', obj.username)
        self.assertEqual('bernie@gmail.com', obj.email)
        self.assertEqual(['broker-repo', 'testcases'],
                         sorted([r.name for r in obj.repo_objs]))
        self.assertEqual(self.app.testcases, obj.user_root)
        self.assertEqual(True, obj.is_admin)
        self.assertEqual(ADMIN_ROLE, obj.role)

        # Get repo object
        self.assertEqual('broker-repo', obj.repo_objs[0].name)
        self.assertEqual(-1, obj.repo_objs[0].maxage)
        self.assertEqual('testcases', obj.repo_objs[1].name)
        self.assertEqual(3, obj.repo_objs[1].maxage)

    def test_get_set(self):
        user = self.app.store.add_user('larry', 'password')

        self.assertEqual('', user.email)
        self.assertEqual([], user.repo_objs)
        self.assertEqual('', user.user_root)
        self.assertEqual(False, user.is_admin)
        self.assertEqual(USER_ROLE, user.role)

        user.user_root = self.app.testcases
        self.mlistener.user_attr_changed.assert_called_with(
            user, {'user_root': self.app.testcases})
        self.mlistener.user_attr_changed.reset_mock()
        user.role = ADMIN_ROLE
        self.mlistener.user_attr_changed.assert_called_with(
            user, {'role': ADMIN_ROLE})
        self.mlistener.user_attr_changed.reset_mock()
        user.email = 'larry@gmail.com'
        self.mlistener.user_attr_changed.assert_called_with(
            user, {'email': 'larry@gmail.com'})
        self.mlistener.user_attr_changed.reset_mock()
        self.mlistener.user_attr_changed.assert_not_called()

        self.assertEqual('larry@gmail.com', user.email)
        self.assertEqual(['broker-repo', 'testcases'],
                         sorted([r.name for r in user.repo_objs]))
        self.assertEqual(self.app.testcases, user.user_root)
        self.assertEqual(True, user.is_admin)
        self.assertEqual(ADMIN_ROLE, user.role)

    def test_users(self):
        # Check admin exists
        self.assertEqual(1, len(self.app.store.users()))
        # Create user.
        self.app.store.add_user('annik')
        users = list(self.app.store.users())
        self.assertEqual(2, len(users))
        self.assertEqual('annik', users[1].username)
        self.assertEqual(2, self.app.store.count_users())

    def test_users_with_search(self):
        # Check admin exists
        self.assertEqual(1, len(self.app.store.users()))
        # Create users.
        self.app.store.add_user('annik')
        self.app.store.add_user('tom')
        self.app.store.add_user('jeff')
        self.app.store.add_user('josh')
        # Search users.
        users = list(self.app.store.users(search='j'))
        self.assertEqual(2, len(users))
        self.assertIn('jeff', [u.username for u in users])
        self.assertIn('josh', [u.username for u in users])
        self.assertEqual(5, self.app.store.count_users())

    def test_users_with_criteria_admins(self):
        # Check admin exists
        self.assertEqual(1, len(self.app.store.users()))
        # Create users.
        self.app.store.add_user('annik').role = ADMIN_ROLE
        self.app.store.add_user('tom').role = ADMIN_ROLE
        self.app.store.add_user('jeff')
        self.app.store.add_user('josh')
        # Search
        users = list(self.app.store.users(criteria='admins'))
        self.assertEqual(3, len(users))
        self.assertEqual(['admin', 'annik', 'tom'],
                         sorted([u.username for u in users]))

    def test_users_with_criteria_ldap(self):
        # Check admin users exists
        self.assertEqual(1, len(self.app.store.users()))
        # Create users.
        self.app.store.add_user('annik', 'coucou')
        self.app.store.add_user('tom')
        # search
        users = list(self.app.store.users(criteria='ldap'))
        self.assertEqual(1, len(users))
        self.assertEqual('tom', users[0].username)

    def test_users_with_criteria_invalid(self):
        # Check admin users exists
        self.assertEqual(1, len(self.app.store.users()))
        # Create users
        self.app.store.add_user('annik', 'coucou')
        self.app.store.add_user('tom')
        # Search
        users = list(self.app.store.users(criteria='invalid'))
        self.assertEqual(0, len(users))

    def test_login(self):
        """Check if login work"""
        userobj = self.app.store.add_user('tom', 'password')
        self.assertIsNotNone(self.app.store.login('tom', 'password'))
        self.assertFalse(self.app.store.login('tom', 'invalid'))
        # Check if listener called
        self.mlistener.user_logined.assert_called_once_with(userobj, None)

    def login_with_invalid_password(self):
        self.app.store.add_user('jeff', 'password')
        self.assertFalse(self.app.store.login('jeff', 'invalid'))
        # password is case sensitive
        self.assertFalse(self.app.store.login('jeff', 'Password'))
        # Match entire password
        self.assertFalse(self.app.store.login('jeff', 'pass'))
        self.assertFalse(self.app.store.login('jeff', ''))
        # Check if listener called
        self.mlistener.user_logined.assert_not_called()

    def test_login_with_invalid_user(self):
        """Check if login work"""
        self.assertIsNone(self.app.store.login('josh', 'password'))
        # Check if listener called
        self.mlistener.user_logined.assert_not_called()

    def test_repos(self):
        # Check default repo exists
        self.assertEqual(2, len(list(self.app.store.repos())))
        user_obj = self.app.store.add_user('annik')
        user_obj.user_root = self.app.testcases
        data = list(self.app.store.repos())
        self.assertEqual(4, len(data))

    def test_repos_with_search(self):
        """
        Check if search is working.
        """
        repos = self.app.store.repos('test')
        self.assertEqual(['testcases'], [r.name for r in repos])
        repos = self.app.store.repos('e')
        self.assertEqual(['broker-repo', 'testcases'],
                         sorted([r.name for r in repos]))

    def test_set_password_update(self):
        userobj = self.app.store.add_user('annik', 'password')
        userobj.set_password('new_password')
        # Check new credentials
        self.assertIsNotNone(self.app.store.login('annik', 'new_password'))
        # Check if listener called
        self.mlistener.user_password_changed.assert_called_once_with(
            'annik', 'new_password')

    def test_set_password_with_old_password(self):
        userobj = self.app.store.add_user('john', 'password')
        userobj.set_password('new_password', old_password='password')
        # Check new credentials
        self.assertIsNotNone(self.app.store.login('john', 'new_password'))
        # Check if listener called
        self.mlistener.user_password_changed.assert_called_once_with(
            'john', 'new_password')

    def test_set_password_with_invalid_old_password(self):
        userobj = self.app.store.add_user('foo', 'password')
        with self.assertRaises(ValueError):
            userobj.set_password('new_password', old_password='invalid')
        # Check if listener called
        self.mlistener.user_password_changed.assert_not_called()

    def test_update_remove_duplicates(self):
        # Update repos should remove duplicate entries from the database
        # generate by previous versions.
        userobj = self.app.store.get_user(self.USERNAME)
        self.assertEqual(['broker-repo', 'testcases'],
                         sorted([r.name for r in userobj.repo_objs]))
        with self.app.store.engine.connect() as conn:
            conn.execute(_REPOS.insert().values(
                userid=userobj._userid, repopath='/testcases'))
        self.assertEqual(['/testcases', 'broker-repo', 'testcases'],
                         sorted([r.name for r in userobj.repo_objs]))
        self.app.store._update()
        self.assertEqual(['broker-repo', 'testcases'],
                         sorted([r.name for r in userobj.repo_objs]))

    def test_update_remove_nested(self):
        # Update repos should remove duplicate entries from the database
        # generate by previous versions.
        userobj = self.app.store.get_user(self.USERNAME)
        self.assertEqual(['broker-repo', 'testcases'],
                         sorted([r.name for r in userobj.repo_objs]))
        with self.app.store.engine.connect() as conn:
            conn.execute(_REPOS.insert().values(
                userid=userobj._userid, repopath='testcases/home/admin/testcases'))
            conn.execute(_REPOS.insert().values(
                userid=userobj._userid, repopath='/testcases/home/admin/data'))
        self.assertEqual(['/testcases/home/admin/data', 'broker-repo', 'testcases',
                          'testcases/home/admin/testcases'], sorted([r.name for r in userobj.repo_objs]))
        self.app.store._update()
        self.assertEqual(['broker-repo', 'testcases'],
                         sorted([r.name for r in userobj.repo_objs]))

    def test_update_repos_remove_slash(self):
        # Check if "/" get removed
        userobj = self.app.store.get_user(self.USERNAME)
        self.assertEqual(['broker-repo', 'testcases'],
                         sorted([r.name for r in userobj.repo_objs]))
        with self.app.store.engine.connect() as conn:
            conn.execute(_REPOS.delete().where(_REPOS.c.userid == userobj._userid))  # @UndefinedVariable
            conn.execute(_REPOS.insert().values(userid=userobj._userid, repopath='/testcases'))
        self.assertEqual(['/testcases', 'broker-repo', 'testcases'], sorted([r.name for r in userobj.repo_objs]))
        self.app.store._update()
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in userobj.repo_objs]))


class StoreWithLdapTest(AbstractLdapStoreTest):

    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=nodomain',
        'ldap-allow-password-change': 'true'
    }

    def test_add_user_to_sqlite(self):
        """Add user to local database."""
        self.app.store.add_user('joe', 'password')
        userobj = self.app.store.login('joe', 'password')
        self.assertIsNotNone(userobj)
        self.assertEqual('joe', userobj.username)
        # Check if listener called
        self.mlistener.user_added.assert_called_once_with(userobj, None)

    def test_add_user_to_ldap(self):
        """Add user to LDAP."""
        self.app.store.add_user('karl', 'password')
        userobj = self.app.store.login('karl', 'password')
        self.assertIsNotNone(userobj)
        self.assertEqual('karl', userobj.username)
        # Check if listener called
        self.mlistener.user_added.assert_called_once_with(userobj, None)

    def test_delete_user(self):
        """Create then delete a user."""
        # Create user
        userobj = self.app.store.add_user('vicky')
        self.assertIsNotNone(self.app.store.get_user('vicky'))
        self.assertIsNotNone(self.app.store.login('vicky', 'password'))
        # Delete user.
        self.assertTrue(userobj.delete())
        self.assertIsNone(self.app.store.get_user('vicky'))

    def test_get_user_with_invalid_user(self):
        self.assertIsNone(self.app.store.get_user('invalid'))

    def test_list(self):
        # Check admin exists
        self.assertEqual(1, len(self.app.store.users()))
        # Add users
        self.app.store.add_user('annik')
        users = list(self.app.store.users())
        self.assertIn('annik', [u.username for u in users])

    def test_login(self):
        """Check if login work"""
        self.app.store.add_user('tom', 'password')
        self.assertIsNotNone(self.app.store.login('tom', 'password'))
        self.assertIsNone(self.app.store.login('tom', 'invalid'))

    def test_login_with_invalid_password(self):
        self.app.store.add_user('jeff', 'password')
        self.assertIsNone(self.app.store.login('jeff', 'invalid'))
        # password is case sensitive
        self.assertIsNone(self.app.store.login('jeff', 'Password'))
        # Match entire password
        self.assertIsNone(self.app.store.login('jeff', 'pass'))
        self.assertIsNone(self.app.store.login('jeff', ''))

    def test_login_with_invalid_user(self):
        """Check if login work"""
        self.assertIsNone(self.app.store.login('josh', 'password'))

    def test_login_with_invalid_user_in_ldap(self):
        """Check if login work"""
        self.assertIsNone(self.app.store.login('kim', 'password'))

    def test_get_user_invalid(self):
        self.assertIsNone(self.app.store.get_user('invalid'))

    def test_set_password_update(self):
        userobj = self.app.store.add_user('annik')
        self.assertFalse(userobj.set_password('new_password'))
        # Check new credentials
        self.assertIsNotNone(self.app.store.login('annik', 'new_password'))

    def test_set_password_with_old_password(self):
        userobj = self.app.store.add_user('john')
        userobj.set_password('new_password', old_password='password')
        # Check new credentials
        self.assertIsNotNone(self.app.store.login('john', 'new_password'))

    def test_set_password_with_invalid_old_password(self):
        userobj = self.app.store.add_user('foo')
        with self.assertRaises(ValueError):
            userobj.set_password('new_password', old_password='invalid')

    def test_set_password_empty(self):
        """Expect error when trying to update password of invalid user."""
        userobj = self.app.store.add_user('john')
        with self.assertRaises(ValueError):
            self.assertFalse(userobj.set_password(''))


class StoreWithLdapAddMissing(AbstractLdapStoreTest):

    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=nodomain',
        'ldap-add-missing-user': 'true'
    }

    def test_login_with_create_user(self):
        """Check if login create the user in database if user exists in LDAP"""
        self.assertIsNone(self.app.store.get_user('tony'))
        userobj = self.app.store.login('tony', 'password')
        self.assertIsNotNone(self.app.store.get_user('tony'))
        self.assertFalse(userobj.is_admin)
        self.assertEqual(USER_ROLE, userobj.role)
        self.assertEqual('', userobj.user_root)
        self.assertEqual('', userobj.email)
        # Check listener
        self.mlistener.user_added.assert_called_once_with(userobj, {u'objectClass': [
                                                          u'person', u'organizationalPerson', u'inetOrgPerson', u'posixAccount'], u'userPassword': [u'password'], u'uid': [u'tony'], u'cn': [u'tony'], u'sAMAccountName': [u'tony']})
        self.mlistener.user_logined.assert_called_once_with(userobj, {u'objectClass': [
                                                            u'person', u'organizationalPerson', u'inetOrgPerson', u'posixAccount'], u'userPassword': [u'password'], u'uid': [u'tony'], u'cn': [u'tony'], u'sAMAccountName': [u'tony']})

    def test_login_with_create_user_with_email(self):
        """Check if login create the user in database if user exists in LDAP"""
        self.assertIsNone(self.app.store.get_user('userwithemail'))
        userobj = self.app.store.login('userwithemail', 'password')
        self.assertIsNotNone(self.app.store.get_user('userwithemail'))
        self.assertFalse(userobj.is_admin)
        self.assertEqual(USER_ROLE, userobj.role)
        self.assertEqual('', userobj.user_root)
        self.assertEqual('user@example.com', userobj.email)


class StoreWithLdapAddMissingWithDefaults(AbstractLdapStoreTest):

    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=nodomain',
        'ldap-add-missing-user': 'true',
        'ldap-add-user-default-role': 'maintainer',
        'ldap-add-user-default-userroot': '/backups/users/{uid[0]}',
    }

    def test_login_with_create_user(self):
        """Check if login create the user in database if user exists in LDAP"""
        self.assertIsNone(self.app.store.get_user('tony'))
        userobj = self.app.store.login('tony', 'password')
        self.assertIsNotNone(self.app.store.get_user('tony'))
        self.assertFalse(userobj.is_admin)
        self.assertEqual(MAINTAINER_ROLE, userobj.role)
        self.assertEqual('/backups/users/tony', userobj.user_root)
        # Check listener
        self.mlistener.user_added.assert_called_once_with(userobj, {u'objectClass': [
                                                          u'person', u'organizationalPerson', u'inetOrgPerson', u'posixAccount'], u'userPassword': [u'password'], u'uid': [u'tony'], u'cn': [u'tony'], u'sAMAccountName': [u'tony']})
        self.mlistener.user_logined.assert_called_once_with(userobj, {u'objectClass': [
                                                            u'person', u'organizationalPerson', u'inetOrgPerson', u'posixAccount'], u'userPassword': [u'password'], u'uid': [u'tony'], u'cn': [u'tony'], u'sAMAccountName': [u'tony']})


class StoreWithLdapAddMissingWithComplexUserroot(AbstractLdapStoreTest):

    default_config = {
        'ldap-uri': '__default__',
        'ldap-base-dn': 'dc=nodomain',
        'ldap-add-missing-user': 'true',
        'ldap-add-user-default-role': 'maintainer',
        'ldap-add-user-default-userroot': '/home/{sAMAccountName[0]}/backups',
    }

    def test_login_with_create_user(self):
        """Check if login create the user in database if user exists in LDAP"""
        self.assertIsNone(self.app.store.get_user('tony'))
        userobj = self.app.store.login('tony', 'password')
        self.assertIsNotNone(self.app.store.get_user('tony'))
        self.assertFalse(userobj.is_admin)
        self.assertEqual(MAINTAINER_ROLE, userobj.role)
        self.assertEqual('/home/tony/backups', userobj.user_root)
        # Check listener
        self.mlistener.user_added.assert_called_once_with(userobj, {u'objectClass': [
                                                          u'person', u'organizationalPerson', u'inetOrgPerson', u'posixAccount'], u'userPassword': [u'password'], u'uid': [u'tony'], u'cn': [u'tony'], u'sAMAccountName': [u'tony']})
        self.mlistener.user_logined.assert_called_once_with(userobj, {u'objectClass': [
                                                            u'person', u'organizationalPerson', u'inetOrgPerson', u'posixAccount'], u'userPassword': [u'password'], u'uid': [u'tony'], u'cn': [u'tony'], u'sAMAccountName': [u'tony']})


class StoreWithAdmin(AppTestCase):

    def test_disk_quota(self):
        """
        Just make a call to the function.
        """
        userobj = self.app.store.get_user(self.USERNAME)
        userobj.disk_quota

    def test_disk_usage(self):
        """
        Just make a call to the function.
        """
        userobj = self.app.store.get_user(self.USERNAME)
        disk_usage = userobj.disk_usage
        self.assertIsInstance(disk_usage, int)


class StoreWithAdminPassword(AppTestCase):

    # password: test
    default_config = {
        'admin-password': '{SSHA}wbSK4hlEX7mtGJplFi2oN6ABm6Y3Bo1e'
    }

    def test_login_with_admin_password(self):
        # Password validation should work with "test"
        userobj = self.app.store.login(self.USERNAME, 'test')
        self.assertIsNotNone(userobj)

    def test_login_with_default_password(self):
        # Password validation should not work with "admin123"
        userobj = self.app.store.login(self.USERNAME, self.PASSWORD)
        self.assertIsNone(userobj)

    def test_set_password(self):
        # # Update password should fail.
        userobj = self.app.store.get_user(self.USERNAME)
        with self.assertRaises(ValueError):
            userobj.set_password('newpassword')


class StoreTestSSHKeys(AppTestCase):
    """
    Testcases for ssh key management.
    """

    def _read_ssh_key(self):
        """Readthe pub key from test packages"""
        filename = pkg_resources.resource_filename(
            __name__, 'test_publickey_ssh_rsa.pub')  # @UndefinedVariable
        with open(filename, 'r', encoding='utf8') as f:
            return f.readline()

    def _read_authorized_keys(self):
        """Read the content of test_authorized_keys"""
        filename = pkg_resources.resource_filename(
            __name__, 'test_authorized_keys')  # @UndefinedVariable
        with open(filename, 'r', encoding='utf8') as f:
            return f.read()

    def test_add_authorizedkey_without_file(self):
        """
        Add an ssh key for a user without an authorizedkey file.
        """
        # Read the pub key
        key = self._read_ssh_key()
        # Add the key to the user
        userobj = self.app.store.get_user(self.USERNAME)
        userobj.add_authorizedkey(key)

        # validate
        keys = list(userobj.authorizedkeys)
        self.assertEqual(1, len(keys), "expecting one key")
        self.assertEqual(
            "3c:99:ed:a7:82:a8:71:09:2c:15:3d:78:4a:8c:11:99", keys[0].fingerprint)

    def test_add_authorizedkey_duplicate(self):
        # Read the pub key
        key = self._read_ssh_key()
        # Add the key to the user
        userobj = self.app.store.get_user(self.USERNAME)
        userobj.add_authorizedkey(key)
        # Add the same key
        with self.assertRaises(DuplicateSSHKeyError):
            userobj.add_authorizedkey(key)

    def test_add_authorizedkey_with_file(self):
        """
        Add an ssh key for a user with an authorizedkey file.
        """
        userobj = self.app.store.get_user(self.USERNAME)

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
        userobj = self.app.store.get_user(self.USERNAME)
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
        userobj.delete_authorizedkey(
            "9a:f1:69:3c:bc:5a:cd:02:5e:33:bc:cd:c0:01:eb:4c")

        # Validate
        keys = list(userobj.authorizedkeys)
        self.assertEqual(1, len(keys))

    def test_delete_authorizedkey_with_file(self):
        """
        Remove an ssh key for a user with authorizedkey file.
        """
        # Create authorized_keys file
        data = self._read_authorized_keys()
        userobj = self.app.store.get_user(self.USERNAME)
        os.mkdir(os.path.join(userobj.user_root, '.ssh'))
        filename = os.path.join(userobj.user_root, '.ssh', 'authorized_keys')
        with open(filename, 'w') as f:
            f.write(data)

        # Get the keys
        keys = list(userobj.authorizedkeys)
        self.assertEqual(5, len(keys))

        # Remove a key
        userobj.delete_authorizedkey(
            "9a:f1:69:3c:bc:5a:cd:02:5e:33:bc:cd:c0:01:eb:4c")

        # Validate
        keys = list(userobj.authorizedkeys)
        self.assertEqual(4, len(keys))


class UserObjectTest(AppTestCase):
    """Testcases for UserObject"""

    def test_set_get_repos(self):
        userobj = self.app.store.get_user(self.USERNAME)
        self.assertEqual(['broker-repo', 'testcases'],
                         sorted([r.name for r in userobj.repo_objs]))

        # Test empty list
        userobj.get_repo('testcases').delete()
        self.assertEqual(
            ['broker-repo'], sorted([r.name for r in userobj.repo_objs]))

        # Make sure we get a repo
        repo_obj = userobj.get_repo('broker-repo')
        self.assertEqual("broker-repo", repo_obj.name)
        repo_obj.maxage = 10
        self.assertEqual(10, repo_obj.maxage)

        # Make sure we get a repo_path
        repo_obj = userobj.get_repo('broker-repo')
        repo_obj.maxage = 7
        self.assertEqual(7, repo_obj.maxage)


class RepoObjectTest(AppTestCase):
    """Testcases for RepoObject."""

    def test_str(self):
        userobj = self.app.store.get_user(self.USERNAME)
        repo_obj = userobj.get_repo(self.REPO)
        self.assertEqual("RepoObject[%s, testcases]" %
                         userobj._userid, str(repo_obj))

    def test_eq(self):
        userobj = self.app.store.get_user(self.USERNAME)
        repo_obj1 = userobj.get_repo(self.REPO)
        repo_obj2 = userobj.get_repo(self.REPO)
        self.assertEqual(repo_obj1, repo_obj2)

    def test_set_get_encoding(self):
        userobj = self.app.store.get_user(self.USERNAME)
        repo_obj = userobj.get_repo(self.REPO)
        repo_obj.encoding = "cp1252"
        self.assertEqual("cp1252", repo_obj.encoding)
        # Check with invalid value.
        with self.assertRaises(ValueError):
            repo_obj.encoding = "invalid"

    def test_set_get_maxage(self):
        userobj = self.app.store.get_user(self.USERNAME)
        repo_obj = userobj.get_repo(self.REPO)
        repo_obj.maxage = 10
        self.assertEqual(10, repo_obj.maxage)
        # Check with invalid value.
        with self.assertRaises(ValueError):
            repo_obj.maxage = "invalid"

    def test_set_get_keepdays(self):
        userobj = self.app.store.get_user(self.USERNAME)
        repo_obj = userobj.get_repo(self.REPO)
        repo_obj.keepdays = 10
        self.assertEqual(10, repo_obj.keepdays)
        # Check with invalid value.
        with self.assertRaises(ValueError):
            repo_obj.keepdays = "invalid"
