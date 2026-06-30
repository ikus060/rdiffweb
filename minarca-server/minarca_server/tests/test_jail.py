# Copyright (C) 2026 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.

import os
import shutil
import subprocess
import tempfile
import unittest

from minarca_server.core.jail import run_jailed
from tzlocal import get_localzone_name

USERROOT = tempfile.gettempdir() + '/backups/joe'


class JailTest(unittest.TestCase):
    def setUp(self):
        unittest.TestCase.setUp(self)
        os.makedirs(USERROOT, exist_ok=True)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        shutil.rmtree(USERROOT, ignore_errors=True)

    def test_jail(self):
        # Write a file in jail folder
        with open(os.path.join(USERROOT, 'test.txt'), 'w') as f:
            f.write('coucou\n')
            f.write('foo\n')
            f.write('bar\n')
        # Run jail and print content of the file.
        run_jailed(['cat', 'test.txt'], path=USERROOT, cwd=USERROOT)

    def test_jail_readonly_bin(self):
        # Skip this test if running as root. Because root can write everywhere
        if os.getuid() == 0:
            return
        # Try to write in /bin directory should fail.
        with self.assertRaises(subprocess.CalledProcessError) as e:
            run_jailed(['touch', '/bin/test.yxy'], path=USERROOT)
        self.assertEqual(e.exception.returncode, 1)

    def test_jail_proc(self):
        # Given a Jail, it's possible to get access to /proc.
        run_jailed(['ps'], path=USERROOT)

    def test_jail_non_zero_return_code(self):
        # Given a Jail that return a non-zero return code
        with self.assertRaises(subprocess.CalledProcessError) as e:
            run_jailed(['/bin/bash', '-c', 'echo FOO 1>&2; echo Éric 1>&2; exit 22'], path=USERROOT)
        # Then an exception is raised
        self.assertIsInstance(e.exception, subprocess.CalledProcessError)
        # The exit code is matching
        self.assertEqual(e.exception.returncode, 22)

    def test_jail_tz(self):
        tz = get_localzone_name()
        run_jailed(['/bin/bash', '-c', 'echo $TZ > tz.txt'], path=USERROOT, cwd=USERROOT, env={'TZ': tz})
        with open(os.path.join(USERROOT, 'tz.txt'), 'r') as f:
            self.assertEqual(tz + '\n', f.read(), "timezone should be define in jail")
