#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2015 Patrik Dufresne Service Logiciel
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

from __future__ import unicode_literals

import base64
import hashlib
import logging
import re
import os

from collections import namedtuple, OrderedDict

"""
Created on May 12, 2015

@author: patrik dufresne
"""

_logger = logging.getLogger(__name__)

# Pattern used to read a line.
PATTERN_LINE = re.compile(r'^(?:(.+) )?(ssh-dss|ssh-ed25519|ssh-rsa|ecdsa-sha2-nistp256|ecdsa-sha2-nistp384|ecdsa-sha2-nistp521)\s+([^ \r\n\t]+)\s?(.*)$')
# Patterns for options parsing.
PATTERN_OPTION1 = re.compile(r'^[ \t]*,[ \t]*')
PATTERN_OPTION2 = re.compile(r'^([-a-z0-9A-Z_]+)=\"(.*?[^\"])\"')
PATTERN_OPTION3 = re.compile(r'^([-a-z0-9A-Z_]+)')
# Patterns to split string
PATTERN_SPACES = re.compile(r'\s+')


class KeySplit(namedtuple('KeySplit', 'lineno options keytype key comment')):
    """
    The `key`field contains the ssh key. e.g.: ssh-rsa ...
    The `options` contains a dict() of options.

    See http://man.he.net/man5/authorized_keys
    """

    @property
    def fingerprint(self):
        """
        Generate a fingerprint from ssh key.
        """
        key = base64.b64decode(self.key.strip())
        fp_plain = hashlib.md5(key).hexdigest()
        return ':'.join(a + b for a, b in zip(fp_plain[::2], fp_plain[1::2]))

    def __str__(self):
        return unicode(self).encode('ascii', 'replace')

    def __unicode__(self):
        buf = ''
        if self.options:
            for key, value in self.options.items():
                if len(buf) > 0:
                    buf += ','
                buf += key
                if isinstance(value, basestring):
                    buf += '="'
                    buf += value
                    buf += '"'
            buf += ' '
        buf += self.keytype
        buf += ' '
        buf += self.key.encode()
        if self.comment:
            buf += ' '
            buf += self.comment
        return buf


def add(filename, key):
    """
    Add a key to an `authorized_keys` file.
    """
    # Open the file
    with open(filename, 'r+') as f:
        # last character in file
        f.seek(-1, 2)
        if f.read(1) != '\n':
            f.write('\n')
        f.write(str(key))
        f.write('\n')


def check_publickey(data):
    """
    Validate the given key. Check if the `data` is a valid SSH key.
    If `Crypto.PublicKey` is available, read any supported key and
    generate an SSH key.
    """
    assert isinstance(data, basestring)

    # Remove any extra space.
    data = data.strip()
    data = PATTERN_SPACES.sub(' ', data)
    # Try to parse the data
    m = PATTERN_LINE.match(data)
    if m:
        key = KeySplit(lineno=False, options=False, keytype=m.group(2), key=m.group(3), comment=m.group(4))
    # Check if the key is valid base64
    try:
        rawkey = base64.b64decode(key.key)
    except:
        raise ValueError()
    if (len(rawkey) * 8) < 2048:
        raise ValueError('SSH key too small')
    return key


def exists(filename, key):
    """
    Check if the given key already exists in the file.
    Return True if the `key` exists in the file. Otherwise return False --
    when the file can't be read this method won't raise an exception.
    """
    # Check if file can be read.
    if not os.access(filename, os.R_OK):
        return False
    # Read the keys.
    try:
        keys = read(filename)
    except IOError:
        return False
    for k in keys:
        if (k.keytype == key.keytype and
                k.key == key.key):
            return True
    return False


def parse_options(value):
    """
    Parse the options part using regex. Return a dict().
    """
    if not value:
        return None
    i = 0
    options = OrderedDict()
    while len(value[i:]) > 0:
        # Check if the string match a comma.
        m = PATTERN_OPTION1.match(value[i:])
        if m:
            i += len(m.group(0))
            continue

        # Try to match a key=value or an option.
        m = (PATTERN_OPTION2.match(value[i:]) or
             PATTERN_OPTION3.match(value[i:]))
        if not m:
            _logger.warn("invalid options: %s", value)
            break
        i += len(m.group(0))
        if m.lastindex == 2:
            options[m.group(1)] = m.group(2)
        else:
            options[m.group(1)] = False

    return options


def read(filename):
    """
    Read an authorized_keys file.
    The `filename` must define a filename path.
    Return a named tuple to represent each line of the file.
    Parse the line as follow:

        options, keytype, base64-encoded key, comment

    See https://github.com/grawity/code/blob/master/lib/python/nullroute/authorized_keys.py
    See http://www.openbsd.org/cgi-bin/man.cgi/OpenBSD-current/man8/sshd.8?query=sshd
    """
    # Open the file
    with open(filename) as f:

        # Read file line by line.
        keys = list()
        for lineno, line in enumerate(f, start=1):
            # Skip comments
            if len(line.strip()) == 0 or line.strip().startswith('#'):
                continue
            # Try to parse the line using regex.
            m = PATTERN_LINE.match(line)
            # Print warning is a line is invalide.
            if not m:
                _logger.warn("invalid authorised_key line: %s", line)
                continue
            options = parse_options(m.group(1))
            keys.append(KeySplit(lineno, options, m.group(2), m.group(3), m.group(4)))
        return keys


def remove(filename, keylineno):
    """
    Remove a key from the authorised_key.

    The `keylineno` represent the line number to be removed.
    """
    # Copy file to temp
    with open(filename, "r") as f:
        lines = f.readlines()
    with open(filename, "w") as f:
        for lineno, line in enumerate(lines, start=1):
            if lineno == keylineno:
                continue
            f.write(line)
