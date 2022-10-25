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

'''
Created on Apr. 10, 2020

@author: patrik dufresne
'''


import hashlib
import os
from base64 import b64decode, b64encode

try:
    import argon2

    _argon = argon2.PasswordHasher()

    def hash_password(password):
        assert password and isinstance(password, str)
        return _argon.hash(password)

except ImportError:

    _argon = None

    def hash_password(password):
        assert password and isinstance(password, str)
        password = password.encode(encoding='utf8')
        salt = os.urandom(4)
        h = hashlib.sha1(password)
        h.update(salt)
        return "{SSHA}" + b64encode(h.digest() + salt).decode('latin1')


def check_password(password, challenge):
    """
    Check if the password matches the challenge.
    The challenge is an encrypted password.
    """
    if not password or not challenge:
        return False
    assert isinstance(password, str)
    assert isinstance(challenge, str)
    if _argon and challenge.startswith('$argon2'):
        try:
            return _argon.verify(challenge, password)
        except Exception:
            return False
    elif challenge.startswith('{SSHA}'):
        digest_salt = b64decode(challenge[6:])
        digest = digest_salt[:20]
        sha = hashlib.sha1(password.encode(encoding='utf8'))
        sha.update(digest_salt[20:])
        return digest == sha.digest()
    else:
        # Fallback to previous SHA
        sha = hashlib.sha1(password.encode('utf8'))
        return challenge == sha.hexdigest()
