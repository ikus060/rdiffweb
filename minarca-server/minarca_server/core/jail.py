# Copyright (C) 2026 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.
import ctypes
import operator
import os
import shutil
import subprocess
import tempfile
from functools import reduce

# libc
_libc = ctypes.CDLL("libc.so.6", use_errno=True)

# Mount flags from <sys/mount.h>
MS_RDONLY = 1
MS_NOSUID = 2
MS_NODEV = 4
MS_REMOUNT = 32
MS_BIND = 4096
MS_REC = 16384

# Umount flags from <sys/mount.h>
MNT_DETACH = 2

# Clone flags from <sched.h>
CLONE_NEWUSER = 0x10000000
CLONE_NEWNS = 0x00020000
CLONE_NEWNET = 0x40000000

_JAIL_INTERNAL_ERROR = 125


def _unshare(flags):
    ret = _libc.unshare(ctypes.c_int(flags))
    if ret != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))


def _mount(source, target, fstype, flags, data=None):
    ret = _libc.mount(
        source.encode() if source else None,
        target.encode() if target else None,
        fstype.encode() if fstype else None,
        ctypes.c_ulong(flags),
        data.encode() if data else None,
    )
    if ret != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))


def _umount(target):
    ret = _libc.umount2(target.encode(), ctypes.c_int(MNT_DETACH))
    if ret != 0:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))


def _umount_all(root):
    """
    Unmount all bind mounts inside root in reverse order to avoid busy mounts.
    """
    mounts = []
    with open('/proc/mounts', 'r') as f:
        for line in f:
            mountpoint = line.split()[1]
            if mountpoint.startswith(root):
                mounts.append(mountpoint)
    for mountpoint in reversed(sorted(mounts)):
        _umount(mountpoint)


def _setup_user_namespace():
    self_pid = os.getpid()
    uid = os.getuid()
    gid = os.getgid()
    _unshare(CLONE_NEWUSER | CLONE_NEWNS | CLONE_NEWNET)
    with open(f"/proc/{self_pid}/setgroups", "w") as f:
        f.write("deny")
    with open(f"/proc/{self_pid}/uid_map", "w") as f:
        f.write(f"0 {uid} 1\n")
    with open(f"/proc/{self_pid}/gid_map", "w") as f:
        f.write(f"0 {gid} 1\n")


def run_jailed(argv, path=None, **kwargs):
    """
    Fork a child process into an isolated namespace and chroot jail,
    then execute argv using subprocess.call.

    :param argv: Command and arguments to execute, e.g. ["rdiff-backup", "--server"]
    :param path: The only writable directory exposed inside the jail.
    :param kwargs: Optional subprocess kwargs.
    """

    root = tempfile.mkdtemp(prefix='minarca-jail-')
    if path:
        path = os.path.abspath(path)

    pid = os.fork()

    if pid != 0:
        # Parent: wait for child, clean up, relay exit code
        try:
            _, status = os.waitpid(pid, 0)
            exit_code = os.waitstatus_to_exitcode(status)
            if exit_code != 0:
                if exit_code == _JAIL_INTERNAL_ERROR:
                    raise RuntimeError(f"Jail setup failed for {argv}, see logs for details")
                raise subprocess.CalledProcessError(exit_code, argv)
        finally:
            _umount_all(root)
            shutil.rmtree(root, ignore_errors=True)
        return

    # Child
    try:
        _setup_user_namespace()

        # Mount /proc read-only with the risk of leaking process information
        # This is required to have the same pid inside and outside the namespace.
        proc_target = os.path.join(root, 'proc')
        os.mkdir(proc_target)
        _mount(source='/proc', target=proc_target, fstype=None, flags=MS_BIND | MS_REC | MS_RDONLY)

        # Mount /dev/null
        os.mkdir(os.path.join(root, 'dev'))
        os.mknod(os.path.join(root, 'dev/null'), 0o0666, device=os.makedev(1, 3))

        # Read-only system mounts
        for mountpoint in ['/bin', '/lib', '/lib64', '/usr', '/opt']:
            if not os.path.exists(mountpoint):
                continue
            dest = os.path.join(root, mountpoint.lstrip('/'))
            os.mkdir(dest)
            _mount(
                source=mountpoint,
                target=dest,
                fstype=None,
                flags=reduce(operator.or_, [MS_BIND, MS_REC, MS_RDONLY], 0),
            )

        # Writable mount for backup path only
        if path:
            dest = os.path.join(root, path.lstrip('/'))
            os.makedirs(dest, exist_ok=True)
            _mount(source=path, target=dest, fstype=None, flags=MS_BIND | MS_REC)

        # chroot
        os.chmod(root, 0o700)
        os.chroot(root)
        os.chdir('/')

        retcode = subprocess.call(argv, **kwargs)
        os._exit(retcode)

    except Exception:
        import traceback

        traceback.print_exc()
        os._exit(_JAIL_INTERNAL_ERROR)
