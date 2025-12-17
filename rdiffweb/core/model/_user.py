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
import logging
import os
import secrets
import string
import sys

import cherrypy
from sqlalchemy import (
    CheckConstraint,
    Column,
    Index,
    Integer,
    SmallInteger,
    String,
    and_,
    event,
    func,
    inspect,
    not_,
)
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import deferred, relationship, validates

import rdiffweb.plugins.db  # noqa
from rdiffweb.core.passwd import check_password, hash_password
from rdiffweb.plugins.scheduler import clear_db_sessions
from rdiffweb.tools.i18n import gettext_lazy as _

from ._callbacks import add_post_commit_tasks
from ._message import AUDIT_IGNORE, MessageMixin, get_model_changes
from ._repo import RepoObject
from ._session import SessionObject
from ._sshkey import SshKey
from ._timestamp import Timestamp
from ._token import Token
from ._update import column_add, column_exists, constraint_add, constraint_exists, index_exists

# Debian trixie drop python3-zxcvbn.
# Until further notice, let use zxcvbn-rs-py as a replacement
try:
    from zxcvbn import zxcvbn
except ImportError:
    from zxcvbn_rs_py import zxcvbn as _zxcvbn

    def zxcvbn(password):
        # Return a dict.
        entropy = _zxcvbn(password)
        return {
            'score': int(entropy.score),
            'feedback': (
                {
                    'warning': str(entropy.feedback.warning),
                    'suggestions': map(str, entropy.feedback.suggestions),
                }
                if entropy.feedback
                else {}
            ),
        }


logger = logging.getLogger(__name__)

Base = cherrypy.db.get_base()
Session = cherrypy.db.get_session()

SEP = b'/'


@clear_db_sessions
def delete_user_with_data(userid):
    """
    Job to delete user with all data.
    """
    # Let start by deleting all repositories from disk.
    userobj = UserObject.get_user(userid)
    username = userobj.username
    logger.info('deleting user [%s] with data', username)
    for repoobj in userobj.repo_objs:
        logger.info('deleting repository [%s]', repoobj.display_name)
        repoobj.delete_repo()
    # Finish by deleting the user it self.
    userobj.delete()
    userobj.commit()
    logger.info('user [%s] deleted', username)


class UserObject(MessageMixin, Base):
    __tablename__ = 'users'
    __table_args__ = {'sqlite_autoincrement': True}

    # Value for role.
    ADMIN_ROLE = 0
    MAINTAINER_ROLE = 5
    USER_ROLE = 10
    ROLES = {
        'admin': ADMIN_ROLE,
        'maintainer': MAINTAINER_ROLE,
        'user': USER_ROLE,
    }
    # Value for mfa field
    DISABLED_MFA = 0
    ENABLED_MFA = 1

    # Regex pattern to be used for validation.
    PATTERN_EMAIL = r"[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,4}$"
    PATTERN_FULLNAME = r"""[^!"#$%&()*+,./:;<=>?@[\]_{|}~]+$"""
    PATTERN_USERNAME = r"^[a-zA-Z][a-zA-Z0-9_.\-]+$"

    # Status values
    STATUS_DELETING = 'deleting'  # Mark for deletion.
    STATUS_DISABLED = 'disabled'  # User is disabled.

    id = Column('UserID', Integer, primary_key=True)
    username = Column('Username', String, nullable=False)
    hash_password = Column('Password', String, nullable=False, default="")
    user_root = Column('UserRoot', String, nullable=False, default="")
    _is_admin = deferred(
        Column(
            'IsAdmin',
            SmallInteger,
            nullable=False,
            server_default="0",
            doc="DEPRECATED This column is replaced by 'role'",
            info={AUDIT_IGNORE: True},
        )
    )
    email = Column('UserEmail', String, nullable=False, default='', server_default='')
    restore_format = deferred(
        Column(
            'RestoreFormat',
            SmallInteger,
            nullable=False,
            server_default="1",
            doc="DEPRECATED This column is not used anymore",
        )
    )
    role = Column('role', SmallInteger, nullable=False, server_default=str(USER_ROLE), default=USER_ROLE)
    fullname = Column('fullname', String, nullable=False, default='', server_default='')
    mfa = Column('mfa', SmallInteger, nullable=False, default=DISABLED_MFA, server_default=str(DISABLED_MFA))
    repo_objs = relationship(
        'RepoObject',
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="RepoObject.repopath",
    )
    lang = Column('lang', String, nullable=False, default='', server_default='')
    report_time_range = Column('report_time_range', SmallInteger, nullable=False, default=0, server_default=str(0))
    report_last_sent = Column('report_last_sent', Timestamp, nullable=True, default=None, info={AUDIT_IGNORE: True})
    notes = Column('notes', String, nullable=False, default='', server_default='')
    status = Column('status', String, nullable=False, default='', server_default='')
    authorizedkeys = relationship(
        'SshKey',
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    tokens = relationship(
        'Token',
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @classmethod
    def authenticate(cls, login, password):
        """
        Verify username password against local database.
        """
        # Check user password.
        userobj = cls.get_user_by_login(login)
        return userobj and userobj.status == '' and userobj.validate_password(password)

    @classmethod
    def get_user(cls, username_or_id):
        """Return a user object from username or id case-insensitive"""
        query = UserObject.query
        if str(username_or_id).isdigit():
            query = query.filter(UserObject.id == int(username_or_id))
        else:
            query = query.filter(func.lower(UserObject.username) == username_or_id.lower())
        return query.one_or_none()

    @classmethod
    def get_user_by_login(cls, login):
        """
        Return a user objectt from username or email (if enabled).
        """
        query = UserObject.query
        cfg = cherrypy.tree.apps[''].cfg
        if cfg.login_with_email and '@' in login:
            query = query.filter(func.lower(UserObject.email) == login.lower())
        else:
            query = query.filter(func.lower(UserObject.username) == login.lower())
        return query.one_or_none()

    @classmethod
    def get_create_or_update_user(cls, login, user_info=None):
        """
        Used during authentication process to search for existing user,
        create user if missing and update user if required.
        """
        # When enabled, create missing userobj in database.
        fullname = user_info.get('fullname') if user_info else None
        email = user_info.get('email') if user_info else None
        # Need to support lookup by username or email
        userobj = cls.get_user_by_login(login)
        cfg = cherrypy.tree.apps[''].cfg
        if userobj is None and cfg.add_missing_user:
            try:
                # At this point, we need to create a new user in database.
                # In case default values are invalid, let evaluate them
                # before creating the user in database.
                username = login if '@' not in login else login.replace('@', '_')
                default_user_root = cfg.add_user_default_userroot and cfg.add_user_default_userroot.format(
                    username=username, **user_info
                )
                default_role = UserObject.ROLES.get(cfg.add_user_default_role)
                userobj = UserObject.add_user(
                    username=username,
                    fullname=fullname,
                    email=email,
                    role=default_role,
                    user_root=default_user_root,
                ).commit()
            except Exception:
                UserObject.session.rollback()
                logger.error('fail to create new user', exc_info=1)
        if userobj is None:
            # User doesn't exists in database
            return None
        # Update user attributes
        dirty = False
        if fullname:
            userobj.fullname = fullname
            dirty = True
        if email:
            userobj.email = email
            dirty = True
        if dirty:
            userobj.commit()
        return userobj.username, userobj

    @classmethod
    def create_admin_user(cls, default_username, default_password):
        # Check if admin user exists. If not, created it.
        userobj = UserObject.get_user(default_username)
        if not userobj:
            userobj = cls.add_user(default_username, role=UserObject.ADMIN_ROLE, user_root='/backups')
            userobj.hash_password = hash_password('admin123')
        # Also make sure to update the password with latest value from config file.
        if default_password:
            if default_password.startswith('{SSHA}') or default_password.startswith('$argon2'):
                userobj.hash_password = default_password
            else:
                userobj.hash_password = hash_password(default_password)
        userobj.add()
        return userobj

    def add_change(self, new_message):
        """
        Override implementation to hide changes made to password field.
        """
        changes = new_message.changes
        if 'hash_password' in changes:
            changes['hash_password'] = ['unknown', '•••••••']
            new_message.changes = changes
        super().add_change(new_message)

    @classmethod
    def add_user(cls, username, password=None, role=USER_ROLE, **attrs):
        """
        Used to add a new user with an optional password.
        """
        assert password is None or isinstance(password, str)
        # Find a database where to add the user
        logger.info("adding new user [%s]", username)
        userobj = UserObject(
            username=username,
            hash_password=hash_password(password) if password else '',
            role=role,
            **attrs,
        ).add()
        # Return user object
        return userobj

    def add_authorizedkey(self, key, comment=None):
        """
        Add the given key to the user. Adding the key to his `authorized_keys`
        file if it exists and adding it to database.
        """
        logger.info("add key [%s] to [%s] database", key, self.username)
        sshkey = SshKey.from_authorizedkey(data=key, comment=comment)
        self.authorizedkeys.append(sshkey)

    def add_access_token(self, name, expiration_time=None, length=16, scope=[]):
        """
        Create a new access token. Return the un-encrypted value of the token.
        """
        assert name
        assert length >= 8
        # Generate a random token
        token = ''.join(secrets.choice(string.ascii_lowercase) for i in range(length))
        # Store hash token
        try:
            token_obj = Token(
                name=name,
                hash_token=hash_password(token),
                expiration_time=expiration_time,
                scope=scope,
            )
            self.tokens.append(token_obj)
            self.flush()
        except IntegrityError:
            raise ValueError(_("Duplicate token name: %s") % name)
        return token

    def valid_user_root(self):
        """
        Check if the current user_root is valid and readable
        """
        try:
            return os.access(self.user_root, os.F_OK) and os.path.isdir(self.user_root)
        except Exception:
            return False

    def schedule_delete(self, delete_data=False):
        """Schedule deletion of the user."""
        cfg = cherrypy.tree.apps[''].cfg
        # Mark this user for deletion
        if self.username == cfg.admin_user:
            raise ValueError(_("can't delete admin user"))
        if delete_data:
            self.status = UserObject.STATUS_DELETING
            for repoobj in self.repo_objs:
                repoobj._status = RepoObject.STATUS_DELETING
            add_post_commit_tasks(Session, 'scheduler:add_job_now', delete_user_with_data, self.id)
        else:
            # Otherwise, let delete use directly.
            return Base.delete(self)

    def delete(self):
        """Delete used from database."""
        cfg = cherrypy.tree.apps[''].cfg
        if self.username == cfg.admin_user:
            raise ValueError(_("can't delete admin user"))
        return Base.delete(self)

    def delete_authorizedkey(self, fingerprint):
        """
        Remove the given key from the user. Remove the key from his
        `authorized_keys` file if it exists and from database database.
        """
        # Also look in database.
        logger.info("removing key [%s] from [%s] database", fingerprint, self.username)
        try:
            record = SshKey.query.filter(and_(SshKey.user == self, SshKey.fingerprint == fingerprint)).one()
        except NoResultFound:
            raise ValueError(_("fingerprint doesn't exists: %s") % fingerprint)
        self.authorizedkeys.remove(record)

    def delete_access_token(self, name):
        assert name
        try:
            token_obj = Token.query.filter(Token.user == self, Token.name == name).one()
        except NoResultFound:
            raise ValueError(_("token name doesn't exists: %s") % name)
        self.tokens.remove(token_obj)

    @property
    def disk_usage(self):
        # Skip if user_root is invalid.
        if not self.user_root or not os.path.exists(self.user_root):
            return 0
        values = cherrypy.engine.publish('get_disk_usage', self)
        # Return the first not None value
        return next((v for v in values if v is not None), 0)

    @property
    def disk_quota(self):
        # Skip if user_root is invalid.
        if not self.user_root or not os.path.exists(self.user_root):
            return 0
        values = cherrypy.engine.publish('get_disk_quota', self)
        # Return the first not None value
        return next((v for v in values if v is not None), 0)

    @disk_quota.setter
    def disk_quota(self, value):
        # Skip if user_root is invalid.
        if not self.user_root or not os.path.exists(self.user_root):
            return
        cherrypy.engine.publish('set_disk_quota', self, value)

    def refresh_repos(self, delete=False):
        """
        Return list of repositories object to reflect the filesystem folders.

        Return a RepoObject for each sub directories under `user_root` with `rdiff-backup-data`.
        """

        # Update the repositories by walking in the directory tree.
        def _onerror(unused):
            logger.error('error updating user [%s] repos' % self.username, exc_info=1)

        # Get application config
        cfg = cherrypy.tree.apps[''].cfg

        dirty = False
        records = list(self.repo_objs)
        user_root = os.fsencode(self.user_root)
        for root, dirs, unused_files in os.walk(user_root, _onerror):
            for name in dirs.copy():
                if name.startswith(b'.'):
                    dirs.remove(name)
            if b'rdiff-backup-data' in dirs:
                repopath = os.path.relpath(root, start=user_root)
                del dirs[:]
                # Handle special scenario when the repo is the
                # user_root
                repopath = b'' if repopath == b'.' else repopath

                # Check if repo path exists.
                record_match = next((record for record in records if record.repopath == os.fsdecode(repopath)), None)
                if not record_match:
                    # Add repository to database.
                    RepoObject(user=self, repopath=os.fsdecode(repopath)).add()
                    dirty = True
                else:
                    records.remove(record_match)
            if root.count(SEP) - user_root.count(SEP) >= cfg.max_depth:
                del dirs[:]
        # If enabled, remove entries from database
        if delete:
            for record in records:
                self.repo_objs.remove(record)
        return dirty

    @property
    def disabled(self):
        return self.status == UserObject.STATUS_DISABLED

    @hybrid_property
    def is_admin(self):
        return self.role is not None and self.role <= self.ADMIN_ROLE

    @hybrid_property
    def is_maintainer(self):
        return self.role is not None and self.role <= self.MAINTAINER_ROLE

    def set_password(self, password):
        """
        Change the user's password. Raise a ValueError if the username or
        the password are invalid.
        """
        if not isinstance(password, str) or len(password.strip()) == 0:
            raise ValueError(_("password can't be empty"))
        cfg = cherrypy.tree.apps[''].cfg

        # Cannot update admin-password if defined
        if self.username == cfg.admin_user and cfg.admin_password:
            raise ValueError(_("can't update admin-password defined in configuration file"))

        # Check password length
        if cfg.password_min_length > len(password) or len(password) > cfg.password_max_length:
            raise ValueError(
                _('Password must have between %(min)d and %(max)d characters.')
                % {'min': cfg.password_min_length, 'max': cfg.password_max_length}
            )

        # Verify password score using zxcvbn
        stats = zxcvbn(password)
        if stats.get('score') < cfg.password_score:
            msg = _('Password too weak.')
            warning = stats.get('feedback', {}).get('warning')
            suggestions = stats.get('feedback', {}).get('suggestions')
            if warning:
                msg += ' ' + warning
            if suggestions:
                msg += ' ' + ' '.join(suggestions)
            raise ValueError(msg)

        # Store password
        logger.info("updating user password [%s] and revoke sessions", self.username)
        self.hash_password = hash_password(password)

        # Revoke other session to force re-login
        session_id = cherrypy.serving.session.id if hasattr(cherrypy.serving, 'session') else None
        SessionObject.query.filter(
            SessionObject.username == self.username,
            SessionObject.id != session_id,
        ).delete()

    def __eq__(self, other):
        return isinstance(other, UserObject) and inspect(self).key == inspect(other).key

    def __str__(self):
        return self.username

    def __repr__(self):
        return f'UserObject({self.username})'

    @validates('status')
    def _validate_status(self, key, value):
        if value != "":
            cfg = cherrypy.tree.apps[''].cfg
            if self.username == cfg.admin_user:
                raise ValueError(_("can't delete or disable admin user"))
        return value

    @validates('username')
    def _validates_username(self, key, value):
        if self.username:
            raise ValueError('Username cannot be modified.')
        return value

    def validate_access_token(self, token):
        """
        Check if the given token matches.
        """
        for access_token in Token.query.filter(Token.user == self).all():
            if access_token.is_expired:
                continue
            if check_password(token, access_token.hash_token):
                # When it matches, return the record.
                return access_token
        return False

    def validate_password(self, password):
        return check_password(password, self.hash_password)


# Username should be case insensitive
user_username_index = Index(
    'user_username_index',
    func.lower(UserObject.username),
    unique=True,
    info={
        "error_message": _('A user with this username address already exists.'),
    },
)

users_username_nan_ck = CheckConstraint(
    UserObject.username.regexp_match(UserObject.PATTERN_USERNAME),
    name="users_username_nan_ck",
    info={
        "error_message": _('Username must start with a letter and contain only letters, numbers, _, ., and -'),
        "description": "Make sure username are not a number (NaN) to avoid conflict when searching user by username vs userid.",
    },
)


@event.listens_for(Base.metadata, 'after_create', insert=True)
def update_user_schema(target, conn, **kw):
    # Create column for roles using "isadmin" column. Keep the
    # original column in case we need to revert to previous version.
    if not column_exists(conn, UserObject.role):
        column_add(conn, UserObject.role)
        UserObject.query.filter(UserObject._is_admin == 1).update({UserObject.role: UserObject.ADMIN_ROLE})
    else:
        # If column exists, make sure to define a non-null value.
        UserObject.query.filter(UserObject.role.is_(None)).update({UserObject.role: UserObject.USER_ROLE})

    # Add user's fullname column
    if not column_exists(conn, UserObject.fullname):
        column_add(conn, UserObject.fullname)
    else:
        UserObject.query.filter(UserObject.fullname.is_(None)).update({UserObject.fullname: ""})

    # Add user's mfa column
    if not column_exists(conn, UserObject.mfa):
        column_add(conn, UserObject.mfa)
    else:
        UserObject.query.filter(UserObject.mfa.is_(None)).update({UserObject.mfa: UserObject.DISABLED_MFA})

    # Add user's lang column
    if not column_exists(conn, UserObject.lang):
        column_add(conn, UserObject.lang)
    else:
        UserObject.query.filter(UserObject.lang.is_(None)).update({UserObject.lang: ""})

    # Add user's report column
    if not column_exists(conn, UserObject.report_time_range):
        column_add(conn, UserObject.report_time_range)
    else:
        UserObject.query.filter(UserObject.report_time_range.is_(None)).update({UserObject.report_time_range: 0})

    if not column_exists(conn, UserObject.report_last_sent):
        column_add(conn, UserObject.report_last_sent)

    # Add notes column
    if not column_exists(conn, UserObject.notes):
        column_add(conn, UserObject.notes)

    # Add status column
    if not column_exists(conn, UserObject.status):
        column_add(conn, UserObject.status)

    # Fix username case insensitive unique
    if not index_exists(conn, 'user_username_index'):
        duplicate_users = (
            UserObject.query.with_entities(func.lower(UserObject.username))
            .group_by(func.lower(UserObject.username))
            .having(func.count(UserObject.username) > 1)
        ).all()
        if duplicate_users:
            msg = (
                'Failure to upgrade your database to make Username case insensitive. '
                'You must downgrade and deleted duplicate Username: '
                '%s' % '\n'.join([str(k) for k in duplicate_users])
            )
            logger.error(msg)
            print(msg, file=sys.stderr)
            raise RuntimeError(msg)
        user_username_index.create(bind=conn)

    # Enforce username regex pattern
    if not constraint_exists(conn, users_username_nan_ck):
        invalid_users = (
            UserObject.query.with_entities(UserObject.username).filter(
                not_(UserObject.username.regexp_match(UserObject.PATTERN_USERNAME))
            )
        ).all()
        if invalid_users:
            msg = (
                'Failure to upgrade your database to ensure that the Username does not include special characters. '
                'You must downgrade and delete the users: '
                '%s' % '\n'.join([str(k) for k in invalid_users])
            )
            logger.error(msg)
            print(msg, file=sys.stderr)
            raise RuntimeError(msg)
        constraint_add(conn, users_username_nan_ck)

    # Enforce unique email if login by email is enabled.
    cfg = cherrypy.tree.apps[''].cfg
    if cfg.login_with_email:
        if not index_exists(conn, 'users_email_index'):
            duplicate_emails = (
                UserObject.query.with_entities(func.lower(UserObject.email))
                .filter(func.trim(UserObject.email) != "")
                .group_by(func.lower(UserObject.email))
                .having(func.count(UserObject.email) > 1)
            ).all()
            if duplicate_emails:
                msg = (
                    'Failure to upgrade your database to make email unique. '
                    'You must downgrade and deleted duplicate email: '
                    '%s' % '\n'.join([str(k) for k in duplicate_emails])
                )
                logger.error(msg)
                print(msg, file=sys.stderr)
                raise RuntimeError(msg)
        # Make sure the index is declared only once.
        if 'users_email_index' not in [idx.name for idx in UserObject.__table__.indexes]:
            users_email_index = Index(
                'users_email_index',
                func.lower(UserObject.email),
                unique=True,
                sqlite_where=UserObject.email != '',
                postgresql_where=UserObject.email != '',
                info={'error_message': _('A user with this email address already exists.')},
            )
            if not index_exists(conn, 'users_email_index'):
                users_email_index.create(bind=conn)


@event.listens_for(Session, 'before_flush')
def user_before_flush(session, flush_context, instances):
    """
    Publish event when user is about to get added.
    """
    for userobj in session.new:
        if isinstance(userobj, UserObject):
            cherrypy.engine.publish('user_adding', userobj)
    for userobj in session.deleted:
        if isinstance(userobj, UserObject):
            cherrypy.engine.publish('user_deleting', userobj)
    for userobj in session.dirty:
        if isinstance(userobj, UserObject):
            _change_type, changes = get_model_changes(userobj)
            if changes:
                cherrypy.engine.publish('user_updating', userobj, changes)


@event.listens_for(Session, 'after_flush')
def user_after_flush(session, flush_context):
    """
    Publish event when user is added, updated or deleted.
    """
    for userobj in session.new:
        if isinstance(userobj, UserObject):
            add_post_commit_tasks(session, 'user_added', userobj)
    for userobj in session.deleted:
        if isinstance(userobj, UserObject):
            add_post_commit_tasks(session, 'user_deleted', userobj.username)
    for userobj in session.dirty:
        if isinstance(userobj, UserObject):
            _change_type, changes = get_model_changes(userobj)
            if changes.pop('hash_password', False):
                add_post_commit_tasks(session, 'user_password_changed', userobj)
            if changes:
                add_post_commit_tasks(session, 'user_updated', userobj, changes)
