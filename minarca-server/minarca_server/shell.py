#
# Minarca server
#
# Copyright (C) 2026 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.
'''
Created on Sep. 25, 2020

@author: Patrik Dufresne <patrik@ikus-soft.com>
'''

import argparse
import logging
import logging.handlers
import os
import shutil
import subprocess
import sys

import configargparse
from minarca_server import __version__
from minarca_server.config import get_parser
from minarca_server.core.jail import Jail
from tzlocal import get_localzone_name

# Enforce a specific timezone when running rdiff-backup
try:
    TZ = get_localzone_name()
except Exception:
    TZ = "UTC"

# Enforce a specific local and encoding when running rdiff-backup.
LANG = 'en_US.utf-8'

DEFAULT_RDIFF_BACKUP_VERSION = '2.0'

_EXIT_EXCEPTION = 201
_EXIT_PERM_ERROR = 202
_EXIT_UNSUPPORTED_VERSION = 203
_EXIT_NO_COMMAND = 204
_EXIT_NO_USER_HOME = 205


logger = logging.getLogger(__name__)


def _setup_logging(cfg, user, ip):
    """
    Configure minarca-shell log file.
    """

    def add_user_and_ip(record):
        record.user = user or "-"
        record.ip = ip or "-"
        return True

    # Capture warnings
    logging.captureWarnings(True)

    # For backward compatibility use logfile as a reference to define the
    # location of the minarca-shell log file.
    if cfg.log_file:
        shell_logfile = os.path.join(os.path.dirname(cfg.log_file), 'shell.log')
        root = logging.getLogger()
        root.setLevel(logging.DEBUG)
        default_handler = logging.handlers.RotatingFileHandler(shell_logfile, maxBytes=10485760, backupCount=20)
        default_handler.addFilter(add_user_and_ip)
        default_handler.setFormatter(
            logging.Formatter("[%(asctime)s][%(levelname)-7s][%(ip)s][%(user)s][PID:%(process)d][%(name)s] %(message)s")
        )
        root.addHandler(default_handler)


def _jail(userroot, args):
    """
    Create a chroot jail using namespaces to isolate completely
    rdiff-backup execution.
    """
    with Jail(userroot):
        subprocess.check_call(args, cwd=userroot, env={'LANG': 'en_US.utf-8', 'TZ': TZ, 'HOME': userroot})


def _find_rdiff_backup(version=DEFAULT_RDIFF_BACKUP_VERSION):
    return shutil.which('rdiff-backup-%s' % (version,))


def _parse_config():
    """
    Use the default configuration parser to retrieve the configuration from environment variable or
    config file. But to avoid any parsing error, keep only the values we are interested in.
    """
    server_parser = get_parser()
    parser = configargparse.ArgumentParser(
        default_config_files=server_parser._default_config_files, auto_env_var_prefix=server_parser._auto_env_var_prefix
    )
    parser.add_argument('--log-file', '--logfile', default=server_parser._defaults['log_file'])
    parser.add_argument('--minarca-rdiff-backup-extra-args', '--rdiffbackup-args')
    return parser.parse_known_args(args=[])[0]


def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.parse_args(args)

    # Try to configure logging system using minarca-server config.
    cfg = _parse_config()

    # Parse arguments
    username = os.environ.get('MINARCA_USERNAME')
    userroot = os.environ.get('MINARCA_USER_ROOT')

    # Configure logging
    ip = os.environ.get('SSH_CLIENT', '').split(' ')[0]
    _setup_logging(cfg, username, ip)

    # Check if folder exists
    if not userroot or not os.path.isdir(userroot):
        logger.info("invalid user home: %s", userroot)
        print("ERROR user home directory is miss configured.", file=sys.stderr)
        sys.exit(_EXIT_NO_USER_HOME)

    # Get Original ssh command from environment variable.
    ssh_original_command = os.environ.get("SSH_ORIGINAL_COMMAND", '')
    if not ssh_original_command:
        print("ERROR no command provided.", file=sys.stderr)
        sys.exit(_EXIT_NO_COMMAND)

    # Get extra arguments for rdiff-backup.
    _extra_args = cfg.minarca_rdiff_backup_extra_args
    if _extra_args:
        _extra_args = _extra_args.split(' ')
    else:
        _extra_args = []

    # Either we get called by rdiff-backup directly
    # or we get called by minarca client which replace the command by the name of the repository.
    try:
        if ssh_original_command in ["echo -n 1", "echo -n host is alive"]:
            # Used by backup-ninja to verify connectivity
            subprocess.check_call(
                ssh_original_command.split(' '),
                env={'LANG': LANG},
                stdout=sys.stdout.fileno(),
                stderr=sys.stderr.fileno(),
            )
        elif ssh_original_command in ["/usr/bin/rdiff-backup -V"]:
            rdiff_backup = _find_rdiff_backup()
            subprocess.check_call(
                [rdiff_backup, '-V'],
                env={'LANG': LANG},
                stdout=sys.stdout.fileno(),
                stderr=sys.stderr.fileno(),
            )
        else:
            if ssh_original_command.startswith("rdiff-backup ") and "--server" in ssh_original_command:
                # When called directly by rdiff-backup.
                # So let use default rdiff-backup version.
                rdiff_backup = _find_rdiff_backup()
            elif 'minarca/' in ssh_original_command:
                # When called by Minarca, we receive a user agent string.
                if 'rdiff-backup/2.0' in ssh_original_command:
                    rdiff_backup = _find_rdiff_backup(version='2.0')
                elif 'rdiff-backup/2.2' in ssh_original_command:
                    rdiff_backup = _find_rdiff_backup(version='2.2')
                else:
                    logger.info("unsupported version: %s", ssh_original_command)
                    print("ERROR: unsupported version: %s" % ssh_original_command, file=sys.stderr)
                    sys.exit(_EXIT_UNSUPPORTED_VERSION)
            else:
                # When called by legacy minarca client with rdiff-backup v1.2.8.
                # the command should be the name of the repository.
                sys.exit(_EXIT_UNSUPPORTED_VERSION)

            # Run the server in chroot jail.
            cmd = [rdiff_backup, '--server'] + _extra_args
            logger.info("running command [%s] in jail [%s] for: %s", ' '.join(cmd), userroot, ssh_original_command)
            try:
                _jail(userroot, cmd)
                logger.info("rdiff-backup terminated successfully")
            except PermissionError:
                logger.error("fail to create rdiff-backup jail", exc_info=1)
                print("ERROR: fail to create rdiff-backup jail", file=sys.stderr)
                sys.exit(_EXIT_PERM_ERROR)
    except subprocess.CalledProcessError as e:
        logger.warning("%s Last output: \n%s" % (e, e.stderr))
        sys.exit(e.returncode)
    except Exception:
        logger.error("unhandled exception in minarca-shell", exc_info=1)
        sys.exit(_EXIT_EXCEPTION)


if __name__ == '__main__':
    main()
