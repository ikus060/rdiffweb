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
Created on  June 30, 2022

Module to test `repo` model.

@author: Patrik Dufresne <patrik@ikus-soft.com>
"""
import cherrypy

import rdiffweb.test
from rdiffweb.core.librdiff import AccessDeniedError, DoesNotExistError
from rdiffweb.core.model import RepoObject, UserObject


class RepoObjectTest(rdiffweb.test.WebCase):
    def test_update_remove_duplicates(self):
        # Given a database with duplicate path
        userobj = UserObject.get_user(self.USERNAME)
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in userobj.repo_objs]))
        RepoObject(userid=userobj.userid, repopath='/testcases').add().commit()
        self.assertEqual(['/testcases', 'broker-repo', 'testcases'], sorted([r.name for r in userobj.repo_objs]))
        # When creating database
        cherrypy.tools.db.create_all()
        # Then duplicates are removed
        userobj = UserObject.get_user(self.USERNAME)
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in userobj.repo_objs]))

    def test_update_remove_nested(self):
        # Given a database with nested path
        userobj = UserObject.get_user(self.USERNAME)
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in userobj.repo_objs]))
        RepoObject(userid=userobj.userid, repopath='testcases/home/admin/testcases').add()
        RepoObject(userid=userobj.userid, repopath='/testcases/home/admin/data').add().commit()
        self.assertEqual(
            ['/testcases/home/admin/data', 'broker-repo', 'testcases', 'testcases/home/admin/testcases'],
            sorted([r.name for r in userobj.repo_objs]),
        )
        # When creating database
        cherrypy.tools.db.create_all()
        # Then nested path are removed
        userobj = UserObject.get_user(self.USERNAME)
        self.assertEqual(['broker-repo', 'testcases'], sorted([r.name for r in userobj.repo_objs]))

    def test_update_repos_remove_slash(self):
        # Given a user with a repository named "/testcases"
        userobj = UserObject.get_user(self.USERNAME)
        RepoObject.query.filter(RepoObject.userid == userobj.userid).delete()
        RepoObject(userid=userobj.userid, repopath='/testcases').add().commit()
        self.assertEqual(['/testcases'], sorted([r.name for r in userobj.repo_objs]))
        # When updating the database schema
        cherrypy.tools.db.create_all()
        # Then the repository name stripped the "/"
        userobj = UserObject.get_user(self.USERNAME)
        self.assertEqual(['testcases'], sorted([r.name for r in userobj.repo_objs]))

    def test_get_repo(self):
        user = UserObject.add_user('bernie', 'my-password')
        user.user_root = self.testcases
        user.refresh_repos()
        user.commit()
        # Get as bernie
        repo_obj = RepoObject.get_repo('bernie/testcases', user)
        self.assertEqual('testcases', repo_obj.name)
        self.assertEqual('bernie', repo_obj.owner)

    def test_get_repo_refresh(self):
        # Given a user with a valid user without any repository
        userobj = UserObject.get_user(self.USERNAME)
        RepoObject.query.filter(RepoObject.userid == userobj.userid).delete()
        with self.assertRaises(DoesNotExistError):
            RepoObject.get_repo('admin/testcases', userobj)
        # When getting a repo with refresh
        repo = RepoObject.get_repo('admin/testcases', userobj, refresh=True)
        # Then the repository is found
        self.assertIsNotNone(repo)

    def test_get_repo_as_other_user(self):
        user = UserObject.add_user('bernie', 'my-password')
        user.user_root = self.testcases
        user.refresh_repos()
        user.commit()
        RepoObject.get_repo('bernie/testcases', user)

        # Get as otheruser
        other = UserObject.add_user('other')
        other.commit()
        with self.assertRaises(AccessDeniedError):
            RepoObject.get_repo('bernie/testcases', other)

    def test_get_repo_as_admin(self):
        user = UserObject.add_user('bernie', 'my-password')
        user.user_root = self.testcases
        user.refresh_repos()
        user.commit()

        # Get as admin
        other = UserObject.add_user('other')
        other.role = UserObject.ADMIN_ROLE
        other.commit()
        repo_obj3 = RepoObject.get_repo('bernie/testcases', other)
        self.assertEqual('testcases', repo_obj3.name)
        self.assertEqual('bernie', repo_obj3.owner)

    def test_str(self):
        userobj = UserObject.get_user(self.USERNAME)
        repo_obj = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        self.assertEqual("RepoObject[%s, testcases]" % userobj.userid, str(repo_obj))

    def test_eq(self):
        userobj = UserObject.get_user(self.USERNAME)
        repo_obj1 = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        repo_obj2 = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        self.assertEqual(repo_obj1, repo_obj2)

    def test_set_get_encoding(self):
        userobj = UserObject.get_user(self.USERNAME)
        repo_obj = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        repo_obj.encoding = "cp1252"
        repo_obj.commit()
        repo_obj = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        self.assertEqual("cp1252", repo_obj.encoding)
        # Check with invalid value.
        with self.assertRaises(ValueError):
            repo_obj.encoding = "invalid"

    def test_set_get_maxage(self):
        userobj = UserObject.get_user(self.USERNAME)
        repo_obj = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        repo_obj.maxage = 10
        repo_obj.commit()
        repo_obj = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        self.assertEqual(10, repo_obj.maxage)
        # Check with invalid value.
        with self.assertRaises(ValueError):
            repo_obj.maxage = "invalid"

    def test_set_get_keepdays(self):
        userobj = UserObject.get_user(self.USERNAME)
        repo_obj = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        repo_obj.keepdays = 10
        repo_obj.commit()
        repo_obj = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        self.assertEqual(10, repo_obj.keepdays)
        # Check with invalid value.
        with self.assertRaises(ValueError):
            repo_obj.keepdays = "invalid"

    def test_keepdays_default_value_from_get_repo(self):
        # Given a User with repository
        userobj = UserObject.get_user(self.USERNAME)
        repo_obj = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        # New repo get created with keepdays == -1
        self.assertEqual('-1', repo_obj._keepdays)
        self.assertEqual(-1, repo_obj.keepdays)

    def test_keepdays_default_value_from_init(self):
        # Given a User
        userobj = UserObject.get_user(self.USERNAME)
        # When creating a new repository
        repo_obj = RepoObject(user=userobj, repopath='repopath').add().commit()
        # New repo get created with keepdays == -1
        self.assertEqual('-1', repo_obj._keepdays)
        self.assertEqual(-1, repo_obj.keepdays)

    def test_keepdays_empty_string(self):
        # Given a User
        userobj = UserObject.get_user(self.USERNAME)
        # When creating a new repository
        repo_obj = RepoObject(user=userobj, repopath='repopath').add().commit()
        RepoObject.session.execute(
            RepoObject.__table__.update().where(RepoObject.__table__.c.RepoID == repo_obj.repoid).values(keepdays='')
        )
        RepoObject.session.commit()
        repo_obj.expire()
        # New repo get created with keepdays == -1
        self.assertEqual('', repo_obj._keepdays)
        self.assertEqual(-1, repo_obj.keepdays)

    def test_encoding_default_value_from_get_repo(self):
        # Given a User with repository
        userobj = UserObject.get_user(self.USERNAME)
        repo_obj = RepoObject.query.filter(RepoObject.user == userobj, RepoObject.repopath == self.REPO).first()
        # New repo get created with utf-8
        self.assertEqual('utf-8', repo_obj.encoding)

    def test_encoding_default_value_from_init(self):
        # Given a User
        userobj = UserObject.get_user(self.USERNAME)
        # When creating a new repository
        repo_obj = RepoObject(user=userobj, repopath='repopath').add().commit()
        # New repo get created with utf-8
        self.assertEqual('utf-8', repo_obj.encoding)
