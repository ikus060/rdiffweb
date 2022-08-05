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

import grp
import os
import platform
import pwd
import sys

import cherrypy
import humanfriendly
import psutil

from rdiffweb.controller import Controller
from rdiffweb.core.librdiff import rdiff_backup_version
from rdiffweb.tools.i18n import ugettext as _


def get_pyinfo():
    try:
        import distro

        yield _('OS Version'), '%s %s (%s %s)' % (
            platform.system(),
            platform.release(),
            distro.name().capitalize(),
            distro.version(),
        )
    except Exception:
        yield _('OS Version'), '%s %s' % (platform.system(), platform.release())
    if hasattr(os, 'path'):
        yield _('OS Path'), os.environ['PATH']
    if hasattr(sys, 'version'):
        yield _('Python Version'), ''.join(sys.version)
    if hasattr(sys, 'subversion'):
        yield _('Python Subversion'), ', '.join(sys.subversion)
    if hasattr(sys, 'prefix'):
        yield _('Python Prefix'), sys.prefix
    if hasattr(sys, 'executable'):
        yield _('Python Executable'), sys.executable
    if hasattr(sys, 'path'):
        yield _('Python Path'), ', '.join(sys.path)


def get_osinfo():
    def gr_name(gid):
        try:
            return grp.getgrgid(gid).gr_name
        except Exception:
            return

    def pw_name(uid):
        try:
            return pwd.getpwuid(os.getuid()).pw_name
        except Exception:
            return

    if hasattr(sys, 'getfilesystemencoding'):
        yield _('File System Encoding'), sys.getfilesystemencoding()
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
    except Exception:
        pass


def get_hwinfo():
    if hasattr(os, 'getloadavg'):
        yield _('Load Average'), ', '.join(map(str, map(lambda x: round(x, 2), os.getloadavg())))
    yield _('CPU Count'), psutil.cpu_count()
    meminfo = psutil.virtual_memory()
    yield _('Memory usage'), '%s / %s' % (
        humanfriendly.format_size(meminfo.used),
        humanfriendly.format_size(meminfo.total),
    )


def get_pkginfo():
    yield _('Rdiff-Backup Version'), '.'.join([str(i) for i in rdiff_backup_version()])
    import jinja2

    yield _('Jinja2 Version'), getattr(jinja2, '__version__')
    yield _('CherryPy Version'), getattr(cherrypy, '__version__')
    import sqlalchemy

    yield _('SQLAlchemy Version'), getattr(sqlalchemy, '__version__')
    try:
        import ldap

        yield _('LDAP Version'), getattr(ldap, '__version__')
        yield _('LDAP SASL Support (Cyrus-SASL)'), ldap.SASL_AVAIL  # @UndefinedVariable
        yield _('LDAP TLS Support (OpenSSL)'), ldap.TLS_AVAIL  # @UndefinedVariable
    except Exception:
        pass


@cherrypy.tools.is_admin()
class AdminSysinfoPage(Controller):
    """Administration pages. Allow to manage users database."""

    @cherrypy.expose
    def default(self, **kwargs):
        params = {
            "version": self.app.version,
            # Config
            "cfg": {k: '********' if 'password' in k else v for k, v in vars(self.app.cfg).items()},
            # System Info entries
            "pyinfo": list(get_pyinfo()),
            "osinfo": list(get_osinfo()),
            "hwinfo": list(get_hwinfo()),
            "ldapinfo": list(get_pkginfo()),
        }
        return self._compile_template("admin_sysinfo.html", **params)
