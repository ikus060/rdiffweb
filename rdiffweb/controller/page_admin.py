# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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

import grp
import logging
import os
import platform
import pwd
import subprocess
import sys

import cherrypy
import humanfriendly
import psutil
from wtforms import validators, widgets
from wtforms.fields.core import StringField, SelectField, Field
from wtforms.fields.html5 import EmailField
from wtforms.fields.simple import PasswordField

from rdiffweb.controller import Controller, flash
from rdiffweb.controller.cherrypy_wtf import CherryForm
from rdiffweb.core.config import Option
from rdiffweb.core.i18n import ugettext as _
from rdiffweb.core.quota import QuotaUnsupported
from rdiffweb.core.store import ADMIN_ROLE, MAINTAINER_ROLE, USER_ROLE
from _collections import OrderedDict

# Define the logger
logger = logging.getLogger(__name__)


def get_pyinfo():
    try:
        import distro
        yield _('OS Version'), '%s %s (%s %s)' % (platform.system(), platform.release(), distro.linux_distribution()[0].capitalize(), distro.linux_distribution()[1])
    except:
        yield _('OS Version'), '%s %s' % (platform.system(), platform.release())
    if hasattr(os, 'path'): yield _('OS Path'), os.environ['PATH']
    if hasattr(sys, 'version'): yield _('Python Version'), ''.join(sys.version)
    if hasattr(sys, 'subversion'): yield _('Python Subversion'), ', '.join(sys.subversion)
    if hasattr(sys, 'prefix'): yield _('Python Prefix'), sys.prefix
    if hasattr(sys, 'executable'): yield _('Python Executable'), sys.executable
    if hasattr(sys, 'path'): yield _('Python Path'), ', '.join(sys.path)


def get_osinfo():

    def gr_name(gid):
        try:
            return grp.getgrgid(gid).gr_name
        except:
            return

    def pw_name(uid):
        try:
            return pwd.getpwuid(os.getuid()).pw_name
        except:
            return

    if hasattr(sys, 'getfilesystemencoding'): yield _('File System Encoding'), sys.getfilesystemencoding()
    if hasattr(os, 'getcwd'):
        yield _('Current Working Directory'), os.getcwd()
    if hasattr(os, 'getegid'):
        yield _('Effective Group'), '%s (%s)' % (os.getegid(), gr_name(os.getegid()))
    if hasattr(os, 'geteuid'):
        yield _('Effective User'), '%s (%s)' % (os.geteuid(), pw_name(os.geteuid))
    if hasattr(os, 'getgid'):
        yield _('Group'), '%s (%s)' % (os.getgid(), gr_name(os.getgid()))
    if hasattr(os, 'getuid'):
        yield _('User'), '%s (%s)' % (os.getuid(), gr_name(os.getuid()))
    if hasattr(os, 'getgroups'):
        yield _('Group Membership'), ', '.join(['%s (%s)' % (gid, gr_name(gid)) for gid in os.getgroups()])
    try:
        if hasattr(os, 'getpid') and hasattr(os, 'getppid'):
            yield _('Process ID'), ('%s (parent: %s)' % (os.getpid(), os.getppid()))
    except:
        pass


def get_hwinfo():
    if hasattr(os, 'getloadavg'):
        yield _('Load Average'), ', '.join(map(str, map(lambda x: round(x, 2), os.getloadavg())))
    yield _('CPU Count'), psutil.cpu_count()
    meminfo = psutil.virtual_memory()
    yield _('Memory usage'), '%s / %s' % (humanfriendly.format_size(meminfo.used), humanfriendly.format_size(meminfo.total))


def get_pkginfo():
    import jinja2
    yield _('Jinja2 Version'), getattr(jinja2, '__version__')
    yield _('CherryPy Version'), getattr(cherrypy, '__version__')
    from rdiffweb.core.store_sqlite import sqlite3  # @UnresolvedImport
    yield _('SQLite Version'), getattr(sqlite3, 'version')
    try:
        import ldap
        yield _('LDAP Version'), getattr(ldap, '__version__')
        yield _('LDAP SASL Support (Cyrus-SASL)'), ldap.SASL_AVAIL  # @UndefinedVariable
        yield _('LDAP TLS Support (OpenSSL)'), ldap.TLS_AVAIL  # @UndefinedVariable
    except:
        pass


class SizeField(Field):
    """
    A text field which stores a file size as GiB or GB format.
    """

    widget = widgets.TextInput()

    def __init__(self, label=None, validators=None, **kwargs):
        super(SizeField, self).__init__(label, validators, **kwargs)

    def _value(self):
        if self.raw_data:
            return ' '.join(self.raw_data)
        else:
            return self.data and humanfriendly.format_size(self.data, binary=True) or ''

    def process_formdata(self, valuelist):
        if valuelist:
            value_str = ''.join(valuelist)
            # parse_size doesn't handle locales.this mean we need to
            # replace ',' by '.' to get parse and prefix number with 0
            value_str = value_str.replace(',', '.').strip()
            # a value must start with a number.
            if value_str.startswith('.'):
                value_str = '0' + value_str
            try:
                self.data = humanfriendly.parse_size(value_str)
            except:
                self.data = None
                raise ValueError(self.gettext('Not a valid file size value'))


class UserForm(CherryForm):
    userid = StringField(_('UserID'))
    username = StringField(_('Username'), validators=[validators.required()])
    email = EmailField(_('Email'), validators=[validators.optional()])
    password = PasswordField(_('Password'))
    user_root = StringField(_('Root directory'), description=_("Absolute path defining the location of the repositories for this user."))
    role = SelectField(
        _('User Role'),
        coerce=int,
        choices=[(ADMIN_ROLE, _("Admin")), (MAINTAINER_ROLE, _("Maintainer")), (USER_ROLE, _("User"))],
        default=USER_ROLE,
        description=_("Admin: may browse and delete everything. Maintainer: may browse and delete their own repo. User: may only browser their own repo."))
    disk_quota = SizeField(
        _('User Quota'),
        validators=[validators.optional()],
        description=_("Users disk spaces (in bytes). Set to 0 for unlimited."))
    disk_usage = SizeField(
        _('Quota Used'),
        validators=[validators.optional()],
        description=_("Disk spaces (in bytes) used by this user."))

    @property
    def error_message(self):
        if self.errors:
            return ' '.join(['%s: %s' % (field, ', '.join(messages)) for field, messages in self.errors.items()])


@cherrypy.tools.is_admin()
class AdminPage(Controller):
    """Administration pages. Allow to manage users database."""

    logfile = Option('logfile')
    logaccessfile = Option('logaccessfile')

    def _get_log_files(self):
        """
        Return a list of log files to be shown in admin area.
        """
        return [fn for fn in [self.logfile, self.logaccessfile] if fn]

    def _get_log_data(self, fn, num=2000):
        """
        Return a list of log files to be shown in admin area.
        """
        try:
            return subprocess.check_output(['tail', '-n', str(num), fn], stderr=subprocess.STDOUT).decode('utf-8')
        except:
            logging.exception('fail to get log file content')
            return "Error getting file content"

    @cherrypy.expose
    def default(self):
        params = {"user_count": self.app.store.count_users(),
                  "repo_count": self.app.store.count_repos()}

        return self._compile_template("admin.html", **params)

    @cherrypy.expose
    def logs(self, filename=u""):
        # get list of log file available.
        data = ""
        logfiles = OrderedDict([(os.path.basename(fn), fn) for fn in self._get_log_files()])
        if logfiles:
            filename = filename or list(logfiles.keys())[0]
            if filename not in logfiles:
                raise cherrypy.HTTPError(404, 'invalid log file: ' + filename)
            data = self._get_log_data(logfiles.get(filename))

        params = {
            "filename": filename,
            "logfiles": logfiles.keys(),
            "data": data,
        }
        return self._compile_template("admin_logs.html", **params)

    @cherrypy.expose
    def users(self, criteria=u"", search=u"", action=u"", **kwargs):

        # If we're just showing the initial page, just do that
        form = UserForm()
        if action in ["add", "edit"] and not form.validate():
            # Display the form error to user using flash
            flash(form.error_message, level='error')

        elif action in ["add", "edit"] and form.validate():
            if action == 'add':
                user = self.app.store.add_user(form.username.data, form.password.data)
            else:
                user = self.app.store.get_user(form.username.data)
                if form.password.data:
                    user.set_password(form.password.data, old_password=None)
            # Don't allow the user to changes it's "role" state.
            if form.username.data != self.app.currentuser.username:
                user.role = form.role.data
            user.email = form.email.data or ''
            if form.user_root.data:
                user.user_root = form.user_root.data
                if not user.valid_user_root():
                    flash(_("User's root directory %s is not accessible!") % user.user_root, level='error')
                    logger.warning("user's root directory %s is not accessible" % user.user_root)
                user.update_repos()
            # Try to update disk quota if the human readable value changed.
            # Report error using flash.
            if form.disk_quota and form.disk_quota.data:
                try:
                    new_quota = form.disk_quota.data
                    old_quota = humanfriendly.parse_size(humanfriendly.format_size(user.disk_quota, binary=True))
                    if old_quota != new_quota:
                        user.disk_quota = new_quota
                        flash(_("User's quota updated"), level='success')
                except QuotaUnsupported as e:
                    flash(_("Setting user's quota is not supported"), level='warning')
                except Exception as e:
                    flash(_("Failed to update user's quota: %s") % e, level='error')
                    logger.warning("failed to update user's quota", exc_info=1)
            if action == 'add':
                flash(_("User added successfully."))
            else:
                flash(_("User information modified successfully."))
        elif action == 'delete':
            if form.username.data == self.app.currentuser.username:
                flash(_("You cannot remove your own account!"), level='error')
            else:
                try:
                    user = self.app.store.get_user(form.username.data)
                    if user:
                        user.delete()
                        flash(_("User account removed."))
                    else:
                        flash(_("User doesn't exists!"), level='warning')
                except ValueError as e:
                    flash(e, level='error')

        params = {
            "form": UserForm(formdata=None),
            "criteria": criteria,
            "search": search,
            "users": list(self.app.store.users(search=search, criteria=criteria))}

        # Build users page
        return self._compile_template("admin_users.html", **params)

    @cherrypy.expose
    def repos(self, criteria=u"", search=u""):
        params = {
            "criteria": criteria,
            "search": search,
            "repos": list(self.app.store.repos(search=search, criteria=criteria))
        }
        return self._compile_template("admin_repos.html", **params)

    @cherrypy.expose
    def sysinfo(self):

        params = {
            "version": self.app.version,
            "plugins": self.app.plugins,
            # Config
            "cfg": {
                k: '********' if 'password' in k else v
                for k, v in self.app.cfg.items()},
            # System Info entries
            "pyinfo": list(get_pyinfo()),
            "osinfo": list(get_osinfo()),
            "hwinfo": list(get_hwinfo()),
            "ldapinfo": list(get_pkginfo()),
        }

        return self._compile_template("admin_sysinfo.html", **params)
