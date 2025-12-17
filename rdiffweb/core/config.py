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

import argparse
import logging
import re
import sys
from collections import OrderedDict
from urllib.parse import urlparse

import cherrypy
import configargparse
from cherrypy import Application

from rdiffweb import __version__

# Define the logger
logger = logging.getLogger(__name__)


def _css_color(value):
    """
    Arg type to handle CSS Color as hex.
    """
    # Validate the color code.
    if not re.match('^#?(?:[0-9a-fA-F]{3}){1,2}$', value):
        raise argparse.ArgumentTypeError("invalid CSS Color")
    if value.startswith('#'):
        return value
    return '#' + value


def _css_font(value):
    """
    Arg type to handle CSS Font.
    """
    # Only validate the name of the font.
    if not re.match('^[a-zA-Z0-9 ]+$', value):
        raise argparse.ArgumentTypeError("invalid CSS Font name")
    return value


def _comma_or_space_separated(value):
    """
    Parse comma or space separated values for argparse.

    Args:
        value (str): Input string containing comma or space separated values

    Returns:
        list: List of parsed values with whitespace stripped

    Raises:
        argparse.ArgumentTypeError: If the input cannot be parsed
    """
    if not isinstance(value, str):
        raise argparse.ArgumentTypeError(f"Expected string, got {type(value).__name__}")

    if not value.strip():
        return []

    # Split by comma first, then by spaces if no commas found
    if ',' in value:
        # Split by comma and strip whitespace from each item
        items = [item.strip() for item in value.split(',')]
    else:
        # Split by any whitespace
        items = value.split()

    # Filter out empty strings
    items = [item for item in items if item]
    return items


def _url(value):
    """
    Validate the URL.
    """
    if value == '':
        return value
    parsed = urlparse(value)
    if parsed.scheme not in ('http', 'https'):
        raise argparse.ArgumentTypeError('invalid URL value %s' % value)
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
        '--default-lang',
        help='default application locale. e.g.: `fr`',
        default='en',
    )

    parser.add_argument(
        '--default-theme',
        '--defaulttheme',
        help='define the default theme. Either: default, blue, orange or custom. Define a default set of colors and font for the web interface. Also read more about link-color, navbar-color and font-family.',
        choices=['default', 'blue', 'orange', 'custom'],
        default='default',
        action=ThemeAction,
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
        help='email address used for the `from:` field when sending email.',
    )

    parser.add_argument(
        '--email-notification-time',
        '--emailnotificationtime',
        metavar='TIME',
        help='time when the email notification should be sent for inactive backups. e.g.: 22:00 Default value: 23:00',
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
        '--email-catch-all',
        metavar='EMAIL',
        help='When defined, all notification email will be sent to this email address using Blind carbon copy (Bcc)',
        default=None,
    )

    parser.add_argument(
        '--brand-favicon',
        '--favicon',
        dest='favicon',
        help='location of an icon to be used as a favicon displayed in web browser.',
    )

    parser.add_argument(
        '--footer-name',
        '--footername',
        help=argparse.SUPPRESS,
        default='rdiffweb',
    )

    parser.add_argument(
        '--footer-url',
        '--footerurl',
        help=argparse.SUPPRESS,
        default='https://rdiffweb.org/',
    )

    parser.add_argument(
        '--brand-logo',
        '--logo',
        dest='logo',
        help='location of an image (preferably a .png) to be used as a replacement for the rdiffweb logo displayed in Login page.',
    )

    parser.add_argument(
        '--brand-header-logo',
        '--header-logo',
        '--headerlogo',
        dest='header_logo',
        help='location of an image (preferably a .png) to be used as a replacement for the rdiffweb header logo displayed in navigation bar.',
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
        type=_css_color,
        dest='link_color',
        help='define a CSS color to be used for link. e.g.: ff0000',
        default='#35979c',
    )

    parser.add_argument(
        '--brand-btn-bg-color',
        '--btn-bg-color',
        type=_css_color,
        dest='btn_bg_color',
        help="define a CSS color to be used for button's background. Default to `link-color` if undefined",
    )

    parser.add_argument(
        '--brand-btn-fg-color',
        '--btn-fg-color',
        type=_css_color,
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
        type=_css_color,
        dest='navbar_color',
        help='define a CSS color to be used for navigation bar background e.g.: 00ff00',
        default='#383e45',
    )

    parser.add_argument(
        '--brand-font-family',
        '--font-family',
        type=_css_font,
        dest='font_family',
        help='define a CSS font to be used as main font. e.g.: Roboto',
        default='Open Sans',
    )

    parser.add_argument(
        '--add-missing-user',
        '--ldap-add-missing-user',
        '--addmissinguser',
        action='store_true',
        help='enable creation of users from LDAP or OAuth when the credential are valid.',
        default=False,
    )

    parser.add_argument(
        '--add-user-default-role',
        '--ldap-add-user-default-role',
        help='default role used when creating users from LDAP or OAuth. This parameter is only useful when `--add-missing-user` is enabled.',
        default='user',
        choices=['admin', 'maintainer', 'user'],
    )

    parser.add_argument(
        '--add-user-default-userroot',
        '--ldap-add-user-default-userroot',
        help='default user root directory used when creating users from LDAP or OAuth. LDAP or OAuth attributes may be used to define the default location. e.g.: `/backups/{uid[0]}/`. This parameter is only useful when `--add-missing-user` is enabled.',
        default='',
    )

    parser.add_argument(
        '--login-with-email',
        help="Allow users to login with email. When enabled, user's email must be unique. This option is required when using OAuth.",
        action='store_true',
        default=False,
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
        type=_comma_or_space_separated,
    )

    parser.add_argument(
        '--ldap-user-filter',
        '--ldap-filter',
        '--ldapfilter',
        help="search filter to limit LDAP lookup. If not provided, defaults to (objectClass=*), which searches for all objects in the tree.",
        default='(objectClass=*)',
    )

    parser.add_argument(
        '--ldap-required-group',
        '--ldaprequiredgroup',
        metavar='CN',
        help="list of CN of the group(s) containing Guests. Not cn=groupname or the full DN.",
        action='append',
    )

    parser.add_argument(
        '--ldap-group-filter',
        help="search filter to limit LDAP lookup of groups. If not provided, defaults to `(objectClass=*)`, which searches for all objects in the tree. For improved performance it's recommended to narrow the search to your group object class. e.g.: `(objectClass=posixGroup)`",
        default='(objectClass=*)',
    )

    parser.add_argument(
        '--ldap-group-attribute',
        '--ldapgroupattribute',
        metavar='ATTRIBUTE',
        help="name of the attribute on the Group that hold the list of members. Default: `member`. Other common value is: `memberUid`",
        default='member',
    )

    parser.add_argument(
        '--ldap-group-attribute-is-dn',
        '--ldapgroupattributeisdn',
        help="True If the group contains list of user defined with DN instead of username.",
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
        '--ldap-fullname-attribute',
        help="LDAP attribute for user display name. If `fullname` is blank, the fullname is taken from the `firstname` and `lastname`. Attributes 'cn', or 'displayName' commonly carry full names.",
        type=_comma_or_space_separated,
    )

    parser.add_argument(
        '--ldap-firstname-attribute',
        help="LDAP attribute for user first name. Used when the attribute configured for name does not exist. e.g.: `givenName`",
        type=_comma_or_space_separated,
        default='givenName',
    )

    parser.add_argument(
        '--ldap-lastname-attribute',
        help="LDAP attribute for user last name. Used when the attribute configured for name does not exist. e.g.: `sn`",
        type=_comma_or_space_separated,
        default='sn',
    )

    parser.add_argument(
        '--ldap-email-attribute',
        help="LDAP attribute for user email. e.g.: mail, email, userPrincipalName",
        type=_comma_or_space_separated,
        default='mail,email',
    )
    parser.add_argument(
        '--oauth-provider-name',
        help="The Oauth provider friendly name.",
        default="OAuth",
    )
    parser.add_argument(
        '--oauth-client-id',
        help="Client ID provided by your OAuth provider when you register your application.",
        default="",
    )
    parser.add_argument(
        '--oauth-client-secret',
        help="Client secret provided by your OAuth provider",
        default="",
    )
    parser.add_argument(
        '--oauth-scope',
        help="OAuth scopes to request from the provider. Common scopes include openid, profile, email. Multiple scopes should be space-separated. Default: openid profile email",
        default="openid profile email",
    )
    parser.add_argument(
        '--oauth-auth-url',
        help="Authorization endpoint URL of your OAuth provider",
        default="",
        type=_url,
    )
    parser.add_argument(
        '--oauth-token-url',
        help="The token endpoint URL of your OAuth provider where access tokens are obtained.",
        default="",
        type=_url,
    )
    parser.add_argument(
        '--oauth-userinfo-url',
        help="The user information endpoint URL where user profile data can be retrieved.",
        default="",
        type=_url,
    )
    parser.add_argument(
        '--oauth-userkey-claim',
        help="OAuth claim containing a unique key matching internal database username or email (if email login is enabled).",
        default="email",
    )
    parser.add_argument(
        '--oauth-fullname-claim',
        help="OAuth claim containing the user's full display name. If not found or empty, the full name is constructed from first name and last name claims.",
        default="name,displayName,full_name",
        type=_comma_or_space_separated,
    )

    parser.add_argument(
        '--oauth-firstname-claim',
        help="OAuth claim containing the user's first name. Used as fallback when full name claim is not available.",
        default="given_name,first_name,givenName",
        type=_comma_or_space_separated,
    )
    parser.add_argument(
        '--oauth-lastname-claim',
        help="OAuth claim containing the user's last name. Used as fallback when full name claim is not available.",
        default="family_name,last_name,surname",
        type=_comma_or_space_separated,
    )
    parser.add_argument(
        '--oauth-email-claim',
        help="OAuth claim containing the user's email address.",
        default="email,mail,email_address",
        type=_comma_or_space_separated,
    )
    parser.add_argument(
        '--oauth-required-claims',
        help="OAuth claim required defined as <claim> <value>",
        type=_comma_or_space_separated,
        action='append',
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
        '--external-url',
        metavar='URL',
        help='URL that should be used to reach this service. You can use the IP of your server, but a Fully Qualified Domain Name (FQDN) is preferred. This URL is only used to generate URL for Email Notification.',
        type=_url,
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
        type=int,
        help='Sliding inactivity timeout for non‑persistent sessions; renews on user activity. Default 15 minutes.',
        default=15,
    )

    parser.add(
        '--session-absolute-timeout',
        metavar='MINUTES',
        type=int,
        help='Absolute maximum session lifetime from initial authentication; never renews on activity.  Default 30 days (or 43200 minutes).',
        default=43200,
    )

    parser.add(
        '--session-persistent-timeout',
        metavar='MINUTES',
        type=int,
        help='Sliding inactivity timeout for persistent (“remember me”) sessions; renews on activity (e.g., 7 days). Default 7 days.',
        default=10080,
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

    parser.add_argument(
        '--latest-version-url',
        help="URL used to check if the current version is the latest version. To disable this feature, the URL could be empty. Default to: https://latest.ikus-soft.com/rdiffweb/latest_version",
        default='https://latest.ikus-soft.com/rdiffweb/latest_version',
    )

    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)

    # Here we append a list of arguments for each locale.
    flags = ['--welcome-msg'] + ['--welcome-msg-' + i for i in ['ca', 'en', 'es', 'fr', 'ru']] + ['--welcomemsg']
    parser.add_argument(
        *flags,
        metavar='HTML',
        help='replace the welcome message displayed in the login page for default locale or for a specific locale',
        action=LocaleAction,
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


class ThemeAction(argparse.Action):
    """
    Custom action used to define the branding using the "theme".
    """

    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(ThemeAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, theme_value, option_string=None):
        param = {}
        if theme_value == 'default':
            param = {'link_color': '#35979c', 'navbar_color': '#383e45'}
        elif theme_value == 'blue':
            param = {'link_color': '#153a58', 'navbar_color': '#153a58'}
        elif theme_value == 'orange':
            param = {'link_color': '#dd4814', 'navbar_color': '#dd4814'}
        # Store theme values in namespace.
        for k, v in param.items():
            setattr(namespace, k, v)


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
