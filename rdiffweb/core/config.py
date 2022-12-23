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

import argparse
import logging
import re
import sys
from collections import OrderedDict

import cherrypy
import configargparse
import pkg_resources
from cherrypy import Application

# Define the logger
logger = logging.getLogger(__name__)

# Get rdiffweb version.
try:
    VERSION = pkg_resources.get_distribution("rdiffweb").version
except pkg_resources.DistributionNotFound:
    VERSION = "DEV"


def css_color(value):
    if not re.match('^#?(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise argparse.ArgumentTypeError("invalid CSS Color")
    if value.startswith('#'):
        return value
    return '#' + value


def css_font(value):
    if not re.match('^[a-zA-Z0-9 ]+$', value):
        raise argparse.ArgumentTypeError("invalid CSS Font name")
    return value


def get_parser():
    # Get global config argument parser
    parser = configargparse.ArgumentParser(
        prog='rdiffweb',
        description='Web interface to browse and restore rdiff-backup repositories.',
        default_config_files=['/etc/rdiffweb/rdw.conf', '/etc/rdiffweb/rdw.conf.d/*.conf'],
        add_env_var_help=True,
        auto_env_var_prefix='RDIFFWEB_',
        config_file_parser_class=ConfigFileParser,
        conflict_handler='resolve',
    )

    parser.add_argument(
        '-f', '--config', is_config_file=True, metavar='FILE', help='location of Rdiffweb configuration file'
    )

    parser.add(
        '--database-uri',
        '--sqlitedb-file',
        '--sqlitedbfile',
        metavar='URI',
        help="""Location of the database used for persistence. SQLite and PostgreSQL
            database are supported officially. To use a SQLite database you may
            define the location using a file path or a URI.
            e.g.: /srv/rdiffweb/file.db or sqlite:///srv/rdiffweb/file.db`.
            To use PostgreSQL server you must provide
            a URI similar to postgresql://user:pass@10.255.1.34/dbname and you
            must install required dependencies.
            By default, Rdiffweb uses a SQLite embedded database located at
            /etc/rdiffweb/rdw.db.""",
        default='/etc/rdiffweb/rdw.db',
    )

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',
        help='enable rdiffweb debug mode - change the log level to DEBUG, print exception stack trace to the web interface and show SQL query in logs',
    )

    parser.add_argument(
        '--admin-user',
        '--adminuser',
        metavar='USERNAME',
        help='administrator username. The administrator user get created on startup if the database is empty.',
        default='admin',
    )

    parser.add_argument(
        '--admin-password',
        metavar='USERNAME',
        help="""administrator encrypted password as SSHA. Read online
            documentation to know more about how to encrypt your password
            into SSHA or use http://projects.marsching.org/weave4j/util/genpassword.php
            When defined, administrator password cannot be updated using the web interface.
            When undefined, default administrator password is `admin123` and
            it can be updated using the web interface.""",
    )

    parser.add_argument(
        '--default-theme',
        '--defaulttheme',
        help='define the default theme. Either: default, blue, orange or custom. Define a default set of colors and font for the web interface. Also read more about link-color, navbar-cloor and font-family.',
        choices=['default', 'blue', 'orange', 'custom'],
        default='default',
    )

    parser.add_argument(
        '--environment',
        choices=['development', 'production'],
        help='define the type of environment: development, production. This is used to limit the information shown to the user when an error occur.',
        default='production',
    )

    parser.add_argument(
        '--email-encryption',
        '--emailencryption',
        choices=['none', 'ssl', 'starttls'],
        help='type of encryption to be used when establishing communication with SMTP server. Default: none',
        default='none',
    )

    parser.add_argument(
        '--email-host',
        '--emailhost',
        metavar='HOST',
        help='SMTP server used to send email in the form <host>:<port>. If the port is not provided, default to standard port 25 or 465 is used. e.g.: smtp.gmail.com:587',
    )

    parser.add_argument(
        '--email-sender',
        '--emailsender',
        metavar='EMAIL',
        help='email addres used for the `from:` field when sending email.',
    )

    parser.add_argument(
        '--email-notification-time',
        '--emailnotificationtime',
        metavar='TIME',
        help='time when the email notifcation should be sent for inactive backups. e.g.: 22:00 Default value: 23:00',
        default='23:00',
    )

    parser.add_argument(
        '--email-username',
        '--emailusername',
        metavar='USERNAME',
        help='username used for authentication with the SMTP server.',
    )

    parser.add_argument(
        '--email-password',
        '--emailpassword',
        metavar='PASSWORD',
        help='password used for authentication with the SMTP server.',
    )

    parser.add_argument(
        '--email-send-changed-notification',
        '--emailsendchangednotification',
        help='True to send notification when sensitive information get change in user profile.',
        action='store_true',
        default=True,
    )

    parser.add_argument(
        '--brand-favicon',
        '--favicon',
        dest='favicon',
        help='location of an icon to be used as a favicon displayed in web browser.',
    )  # @UndefinedVariable

    parser.add_argument(
        '--footer-name',
        '--footername',
        help=argparse.SUPPRESS,
        default='rdiffweb',
    )  # @UndefinedVariable

    parser.add_argument(
        '--footer-url',
        '--footerurl',
        help=argparse.SUPPRESS,
        default='https://rdiffweb.org/',
    )  # @UndefinedVariable

    parser.add_argument(
        '--brand-logo',
        '--logo',
        dest='logo',
        help='location of an image (preferably a .svg) to be used as a replacement for the rdiffweb logo displayed in Login page.',
    )

    parser.add_argument(
        '--brand-header-logo',
        '--header-logo',
        '--headerlogo',
        dest='header_logo',
        help='location of an image (preferably a .svg) to be used as a replacement for the rdiffweb header logo displayed in navigation bar.',
    )

    parser.add_argument(
        '--brand-header-name',
        '--header-name',
        '--headername',
        dest='header_name',
        help='application name displayed in the title bar and header menu.',
        default='Rdiffweb',
    )

    parser.add_argument(
        '--brand-link-color',
        '--link-color',
        type=css_color,
        dest='link_color',
        help='define a CSS color to be used for link. e.g.: ff0000',
    )

    parser.add_argument(
        '--brand-btn-bg-color',
        '--btn-bg-color',
        type=css_color,
        dest='btn_bg_color',
        help="define a CSS color to be used for button's background. Default to `link-color` if undefined",
    )

    parser.add_argument(
        '--brand-btn-fg-color',
        '--btn-fg-color',
        type=css_color,
        dest='btn_fg_color',
        help="define a CSS color to be used for button's text. Default to white if undefined",
    )

    parser.add_argument(
        '--brand-btn-rounded',
        '--btn-rounded',
        type=bool,
        dest='btn_rounded',
        help='define if the button should be rounded',
    )

    parser.add_argument(
        '--brand-navbar-color',
        '--navbar-color',
        type=css_color,
        dest='navbar_color',
        help='define a CSS color to be used for navigation bar background e.g.: 00ff00',
    )

    parser.add_argument(
        '--brand-font-family',
        '--font-family',
        type=css_font,
        dest='font_family',
        help='define a CSS font to be used as main font. e.g.: Roboto',
    )

    parser.add_argument(
        '--ldap-add-missing-user',
        '--addmissinguser',
        action='store_true',
        help='enable creation of users from LDAP when the credential are valid.',
        default=False,
    )

    parser.add_argument(
        '--ldap-add-user-default-role',
        help='default role used when creating users from LDAP. This parameter is only useful when `--ldap-add-missing-user` is enabled.',
        default='user',
        choices=['admin', 'maintainer', 'user'],
    )

    parser.add_argument(
        '--ldap-add-user-default-userroot',
        help='default user root directory used when creating users from LDAP. LDAP attributes may be used to define the default location. e.g.: `/backups/{uid[0]}/`. This parameter is only useful when `--ldap-add-missing-user` is enabled.',
        default='',
    )

    parser.add_argument(
        '--ldap-uri',
        '--ldapuri',
        help='URL to the LDAP server used to validate user credentials. e.g.: ldap://localhost:389',
    )

    parser.add_argument(
        '--ldap-base-dn',
        '--ldapbasedn',
        metavar='DN',
        help='DN of the branch of the directory where all searches should start from. e.g.: dc=my,dc=domain',
        default="",
    )

    parser.add_argument(
        '--ldap-scope',
        '--ldapscope',
        help='scope of the search. Can be either base, onelevel or subtree',
        choices=['base', 'onelevel', 'subtree'],
        default="subtree",
    )

    parser.add_argument('--ldap-tls', '--ldaptls', action='store_true', help='enable TLS')

    parser.add_argument(
        '--ldap-username-attribute',
        '--ldapattribute',
        metavar='ATTRIBUTE',
        help="The attribute to search username. If no attributes are provided, the default is to use `uid`. It's a good idea to choose an attribute that will be unique across all entries in the subtree you will be using.",
        default='uid',
    )

    parser.add_argument(
        '--ldap-filter',
        '--ldapfilter',
        help="search filter to limit LDAP lookup. If not provided, defaults to (objectClass=*), which searches for all objects in the tree.",
        default='(objectClass=*)',
    )

    parser.add_argument(
        '--ldap-required-group',
        '--ldaprequiredgroup',
        metavar='GROUPNAME',
        help="name of the group of which the user must be a member to access rdiffweb. Should be used with ldap-group-attribute and ldap-group-attribute-is-dn.",
    )

    parser.add_argument(
        '--ldap-group-attribute',
        '--ldapgroupattribute',
        metavar='ATTRIBUTE',
        help="name of the attribute defining the groups of which the user is a member. Should be used with ldap-required-group and ldap-group-attribute-is-dn.",
        default='member',
    )

    parser.add_argument(
        '--ldap-group-attribute-is-dn',
        '--ldapgroupattributeisdn',
        help="True if the content of the attribute `ldap-group-attribute` is a DN.",
        action='store_true',
    )

    parser.add_argument(
        '--ldap-bind-dn',
        '--ldapbinddn',
        metavar='DN',
        help="optional DN used to bind to the server when searching for entries. If not provided, will use an anonymous bind.",
        default="",
    )

    parser.add_argument(
        '--ldap-bind-password',
        '--ldapbindpassword',
        metavar='PASSWORD',
        help="password to use in conjunction with LdapBindDn. Note that the bind password is probably sensitive data, and should be properly protected. You should only use the LdapBindDn and LdapBindPassword if you absolutely need them to search the directory.",
        default="",
    )

    parser.add_argument(
        '--ldap-version',
        '--ldapversion',
        '--ldapprotocolversion',
        help="version of LDAP in use either 2 or 3. Default to 3.",
        default=3,
        type=int,
        choices=[2, 3],
    )

    parser.add_argument(
        '--ldap-network-timeout',
        '--ldapnetworktimeout',
        metavar='SECONDS',
        help="timeout in seconds value used for LDAP connection",
        default=100,
        type=int,
    )

    parser.add_argument(
        '--ldap-timeout',
        '--ldaptimeout',
        metavar='SECONDS',
        help="timeout in seconds value used for LDAP request",
        default=300,
        type=int,
    )

    parser.add_argument(
        '--ldap-encoding',
        '--ldapencoding',
        metavar='ENCODING',
        help="encoding used by your LDAP server.",
        default="utf-8",
    )

    parser.add_argument(
        '--log-access-file', '--logaccessfile', metavar='FILE', help='location of Rdiffweb log access file.'
    )

    parser.add_argument(
        '--log-file',
        '--logfile',
        metavar='FILE',
        help='location of Rdiffweb log file. Print log to the console if not define in config file.',
    )

    parser.add_argument(
        '--log-level',
        '--loglevel',
        help='Define the log level.',
        choices=['ERROR', 'WARN', 'INFO', 'DEBUG'],
        default='INFO',
    )

    parser.add_argument(
        '--max-depth',
        '--maxdepth',
        metavar='DEPTH',
        help="define the maximum folder depthness to search into the user's root directory to find repositories. This is commonly used if you repositories are organised with multiple sub-folder.",
        type=int,
        default=3,
    )

    parser.add('--quota-set-cmd', '--quotasetcmd', metavar='COMMAND', help="command line to set the user's quota.")

    parser.add('--quota-get-cmd', '--quotagetcmd', metavar='COMMAND', help="command line to get the user's quota.")

    parser.add(
        '--quota-used-cmd', '--quotausedcmd', metavar='COMMAND', help="Command line to get user's quota disk usage."
    )

    parser.add(
        '--remove-older-time',
        '--removeoldertime',
        metavar='TIME',
        help="Time when to execute the remove older scheduled job. e.g.: 22:30",
        default='23:00',
    )

    parser.add('--server-host', '--serverhost', metavar='IP', default='127.0.0.1', help='IP address to listen to')

    parser.add(
        '--server-port',
        '--serverport',
        metavar='PORT',
        help='port to listen to for HTTP request',
        default='8080',
        type=int,
    )

    parser.add(
        '--rate-limit-dir',
        '--session-dir',
        '--sessiondir',
        metavar='FOLDER',
        help='location where to store rate-limit information. When undefined, the data is kept in memory. `--session-dir` are deprecated and kept for backward compatibility.',
    )

    parser.add(
        '--rate-limit',
        metavar='LIMIT',
        type=int,
        default=20,
        help='maximum number of requests per hour that can be made on sensitive endpoints. When this limit is reached, an HTTP 429 message is returned to the user or the user is logged out. This security measure is used to limit brute force attacks on the login page and the RESTful API. default: 20 requests / hour',
    )

    parser.add(
        '--session-idle-timeout',
        metavar='MINUTES',
        help='This timeout defines the amount of time a session will remain active in case there is no activity in the session. User Session will be revoke after this period of inactivity, unless the user selected "remember me". Default 5 minutes.',
        default=5,
    )

    parser.add(
        '--session-absolute-timeout',
        metavar='MINUTES',
        help='This timeout defines the maximum amount of time a session can be active. After this period, user is forced to (re)authenticate, unless the user selected "remember me". Default 20 minutes.',
        default=20,
    )

    parser.add(
        '--session-persistent-timeout',
        metavar='MINUTES',
        help='This timeout defines the maximum amount of time to remember and trust a user device. This timeout is used when user select "remember me". Default 30 days.',
        default=43200,
    )

    parser.add(
        '--ssl-certificate',
        '--sslcertificate',
        metavar='CERT',
        help='location of the SSL Certification to enable HTTPS (not recommended)',
    )

    parser.add(
        '--ssl-private-key',
        '--sslprivatekey',
        metavar='KEY',
        help='location of the SSL Private Key to enable HTTPS (not recommended)',
    )

    parser.add(
        '--tempdir',
        metavar='FOLDER',
        help='alternate temporary folder to be used when restoring files. Might be useful if the default location has limited disk space. Default to TEMPDIR environment or `/tmp`.',
    )

    parser.add(
        '--disable-ssh-keys',
        action='store_true',
        help='used to hide SSH Key management to avoid users to add or remove SSH Key using the web application',
        default=False,
    )

    parser.add(
        '--password-min-length',
        type=int,
        help="Minimum length of the user's password",
        default=8,
    )

    parser.add(
        '--password-max-length',
        type=int,
        help="Maximum length of the user's password",
        default=128,
    )

    parser.add(
        '--password-score',
        type=lambda x: max(1, min(int(x), 4)),
        help="Minimum zxcvbn's score for password. Value from 1 to 4. Default value 2. Read more about it here: https://github.com/dropbox/zxcvbn",
        default=2,
    )

    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION)

    # Here we append a list of arguments for each locale.
    flags = ['--welcome-msg'] + ['--welcome-msg-' + i for i in ['ca', 'en', 'es', 'fr', 'ru']] + ['--welcomemsg']
    parser.add_argument(
        *flags,
        metavar='HTML',
        help='replace the welcome message displayed in the login page for default locale or for a specific locale',
        action=LocaleAction
    )
    return parser


def parse_args(args=None, config_file_contents=None):
    args = sys.argv[1:] if args is None else args
    return get_parser().parse_args(args, config_file_contents=config_file_contents)


class LocaleAction(argparse.Action):
    """
    Custom Action to support defining arguments with locale.
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(LocaleAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, value, option_string=None):
        if option_string[-3] == '-':
            # When using arguments, we can extract the locale from the argument key
            locale = option_string[-2:]
        elif value[2] == ':':
            # When using config file, the locale could be extract from the value e.g. fr:message
            locale = value[0:2]
            value = value[3:]
        else:
            locale = ''
        # Create a dictionary with locale.
        items = getattr(namespace, self.dest) or {}
        items[locale] = value
        setattr(namespace, self.dest, items)


class ConfigFileParser(object):
    """
    Custom config file parser to support rdiffweb config file format.
    """

    def get_syntax_description(self):
        msg = "Configuration file syntax allows: key=value, flag=true."
        return msg

    def parse(self, stream):
        """
        Used to read the rdiffweb config file as dict.
        """

        result = OrderedDict()

        for i, line in enumerate(stream):
            line = re.compile("(.*?)#.*").sub(r'\1', line).strip()
            if not line:
                continue
            if '=' not in line:
                raise configargparse.ConfigFileParserException(
                    "Unexpected line {} in {}: {}".format(i, getattr(stream, 'name', 'stream'), line)
                )
            split_line = line.partition('=')
            if len(split_line) != 3:
                raise configargparse.ConfigFileParserException(
                    "Unexpected line {} in {}: {}".format(i, getattr(stream, 'name', 'stream'), line)
                )

            # Get key & value
            key = split_line[0].lower().strip().replace('_', '-')
            value = split_line[2].strip()

            # Support welcome-msg locale for backward compatibility
            m = re.match("welcome-?msg\\[(ca|en|es|fr|ru)\\]", key.lower())
            if m:
                key = "welcome-msg-" + m.group(1)
                value = m.group(1) + ":" + value

            result[key] = value

        # This dictionary is read by cherrypy. So create appropriate structure.
        return result


class Option(object):
    def __init__(self, key):
        assert key
        self.key = key

    def __get__(self, instance, owner):
        """
        Return a property to wrap the given option.
        """
        return self.get(instance)

    def get(self, instance=None):
        """
        Return the value of this options.
        """
        if isinstance(instance, Application):
            app = instance
        else:
            app = cherrypy.request.app or getattr(instance, 'app', None)
        assert app, "Option() can't get reference to app"
        assert app.cfg, "Option() can't get reference to app.cfg"
        return getattr(app.cfg, self.key)
