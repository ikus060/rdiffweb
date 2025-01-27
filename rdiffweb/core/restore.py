# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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
"""
Module is responsible to restore rdiff-backup repository into an archive in a
transparent way to restore and archive at the same time allowing creation of the
archive as the restore processing is still running.

It also handle all the encoding and decoding of filenames to generate an
appropriate archive usable by the target system. In few circumstances it's
impossible to properly generate a valid filename depending of the archive types.
"""
import logging
import os
import shutil
import stat
import subprocess
import tarfile
import tempfile
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

logger = logging.getLogger(__name__)

# Log used by rdiff-backup
TOKEN1 = b'* Processing changed file '
TOKEN2 = b'Processing changed file '

# Pick random exit code when exception are raised
CUST_EXIT_CODE = 65


class RestoreException(Exception):
    """Raised when restore fail."""

    pass


class TarArchiver(object):
    """
    Archiver to create tar archive (with compression).
    """

    def __init__(self, dest, compression=''):
        assert compression in ['', 'gz', 'bz2']
        mode = "w|" + compression

        # Open the tar archive with the right method.
        if isinstance(dest, str):
            self.z = tarfile.open(name=dest, mode=mode, encoding='UTF-8', format=tarfile.PAX_FORMAT)
            self.fileobj = None
        else:
            self.z = tarfile.open(fileobj=dest, mode=mode, encoding='UTF-8', format=tarfile.PAX_FORMAT)
            self.fileobj = dest

    def addfile(self, filename, arcname, encoding):
        assert isinstance(filename, bytes)
        assert isinstance(arcname, bytes)
        assert encoding
        # Do not create a folder "./"
        if os.path.isdir(filename) and arcname == b'.':
            return
        # The processing of symlink is broken when using bytes
        # for files, so let convert it to unicode with surrogateescape.
        filename = filename.decode('ascii', 'surrogateescape')
        # The archive name must be unicode and will be convert back to UTF8
        arcname = arcname.decode(encoding, 'surrogateescape')
        # Add file to archive.
        self.z.add(filename, arcname, recursive=False)

    def close(self):
        # Close tar archive
        self.z.close()
        # Also close file object.
        if self.fileobj:
            self.fileobj.close()


class ZipArchiver(object):
    """
    Write files to zip file or stream.
    Can write uncompressed, or compressed with deflate.
    """

    def __init__(self, dest, compress=True):
        compress = compress and ZIP_DEFLATED or ZIP_STORED
        self.z = ZipFile(dest, 'w', compress)

    def addfile(self, filename, arcname, encoding):
        assert isinstance(filename, bytes)
        assert isinstance(arcname, bytes)
        assert encoding
        # Do not create a folder "./"
        if os.path.isdir(filename) and arcname == b'.':
            return
        # As of today ZipFile doesn't support symlink or named pipe.
        # So we silently skip them. See bug #26269 and #18595
        if os.path.islink(filename) or not (os.path.isfile(filename) or os.path.isdir(filename)):
            return
        # The filename need to be unicode.
        filename = filename.decode('ascii', 'surrogateescape')
        # The archive name must be unicode.
        # But Zip doesn',t support surrogate, so let replace invalid char.
        arcname = arcname.decode(encoding, 'replace')
        # Add file to archive.
        self.z.write(filename, arcname)

    def close(self):
        self.z.close()


class RawArchiver(object):
    """
    Used to stream a single file.
    """

    def __init__(self, dest):
        assert dest
        self.dest = dest
        if isinstance(self.dest, str):
            self.output = open(self.dest, 'wb')
        else:
            self.outout = dest

    def addfile(self, filename, arcname, encoding):
        assert isinstance(filename, bytes)
        # Only stream files. Skip directories.
        if os.path.isdir(filename):
            return
        with open(filename, 'rb') as f:
            shutil.copyfileobj(f, self.outout)

    def close(self):
        self.outout.close()


ARCHIVERS = {
    'tar': TarArchiver,
    'tbz2': lambda dest: TarArchiver(dest, 'bz2'),
    'tar.bz2': lambda dest: TarArchiver(dest, 'bz2'),
    'tar.gz': lambda dest: TarArchiver(dest, 'gz'),
    'tgz': lambda dest: TarArchiver(dest, 'gz'),
    'zip': ZipArchiver,
    'raw': RawArchiver,
}


class _wrap_close:
    """Wrap fileobject."""

    def __init__(self, stream, pid):
        assert isinstance(pid, int) and pid > 0
        self._stream = stream
        self._pid = pid
        self._return_code = None

    def close(self):
        self._stream.close()
        if self._return_code is None:
            try:
                _pid, exit_status = os.waitpid(self._pid, 0)
                self._return_code = exit_status >> 8
                if self._return_code != 0:
                    logger.error(f'rdiff-backup restore return non-zero exit status: {self._return_code}')
            except ChildProcessError:
                logger.exception('fail to get child process exit status')

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __getattr__(self, name):
        return getattr(self._stream, name)

    def __iter__(self):
        return iter(self._stream)


def _lookup_filename(base, path):
    """
    Search for the given filename. This is used to mitigate encoding issue
    with rdiff-backup2. That replace invalid character.
    """
    assert isinstance(base, bytes)
    assert isinstance(path, bytes)
    # Easy path, if the file encoding is ok, will find the file.
    fullpath = os.path.normpath(os.path.join(base, path))
    if os.path.lexists(fullpath):
        return fullpath, path
    # Otherwise, Search the for a matching filename.
    dirname = os.path.dirname(os.path.join(base, path))
    basename = os.path.basename(path)
    for file in os.listdir(dirname):
        if basename == file.decode('utf-8', 'replace').encode('utf-8', 'replace'):
            fullpath = os.path.join(dirname, file)
            arcname = os.path.relpath(fullpath, base)
            return fullpath, arcname
    return None, None


def _yield_previous_lines(stream):
    """
    Generator to yield previous_line from a stream.

    This is particularly useful in scenarios like parsing the output of `rdiff-backup`,
    where the program logs messages such as "Processing changed file <file_path>"
    before actually processing the file. Using this generator, we can determine
    when the processing of a file is complete by observing when the next file starts
    being logged, allowing us to execute post-processing logic for the previous file
    before moving on to the next.
    """
    previous_line = None
    for current_line in stream:
        current_line = current_line.rstrip(b'\n')
        if previous_line is not None:
            yield previous_line
        previous_line = current_line
    if previous_line is not None:
        yield previous_line


def pipe_restore(rdiff_backup, path, restore_as_of, kind, encoding, env={}):
    """
    Fork execution to restore and archive files in a separate process to woraround python Global Interpreter Lock.

    Used to restore a file or a directory.

    rdiff_backup: location of rdiff-backup executable to be used.
    path: relative or absolute file or folder to be restored (unquoted)
    restore_as_of: date to restore
    kind: type of archive to generate or raw to stream a single file.
    encoding: encoding of the repository (used to properly encode the filename in archive)
    """
    assert rdiff_backup
    assert isinstance(path, bytes)
    assert isinstance(restore_as_of, int)
    assert kind in ARCHIVERS

    # Create a pipe for file transfert
    rfile, wfile = os.pipe()

    # Fork the process
    pid = os.fork()
    if pid > 0:
        # Parent - Close unused end
        os.close(wfile)
        # Parent receive response header, then file body.
        # This could later be expended to transport more status information.
        fileobj = os.fdopen(rfile, 'rb')
        # Expect "ok", then file content
        header_status = fileobj.readline()
        if header_status != b'ok\n':
            raise RestoreException()
        return _wrap_close(fileobj, pid)

    else:
        # Child - Close unused end
        os.close(rfile)
        try:
            with os.fdopen(wfile, 'wb') as dest:
                return_code = _restore(
                    rdiff_backup=rdiff_backup,
                    path=path,
                    restore_as_of=restore_as_of,
                    kind=kind,
                    encoding=encoding,
                    dest=dest,
                    env=env,
                    send_header=1,
                )
                os._exit(return_code)
        except Exception as e:
            # We need to catch _any_ exception so that it doesn't
            # propagate out of this function and cause exiting
            # with anything other than os._exit()
            logger.exception(f'restore failed: {e}')
            os._exit(CUST_EXIT_CODE)


def _restore(rdiff_backup, path, restore_as_of, kind, encoding, dest, env={}, send_header=False):
    assert isinstance(path, bytes)
    assert isinstance(restore_as_of, int)
    assert kind in ARCHIVERS

    # Generate a temporary location used to restore data.
    # This location will be deleted after restore.
    tmp_output = tempfile.mkdtemp(prefix=b'rdiffweb_restore_')
    logger.debug('restoring data into temporary folder: %r' % tmp_output)

    cmd = [
        rdiff_backup,
        b'-v',
        b'5',
        b'--restore-as-of=' + str(restore_as_of).encode('latin'),
        path,
        tmp_output,
    ]
    logger.debug('executing %r with env %r' % (cmd, env))

    archive = None
    try:
        proc = subprocess.Popen(
            cmd,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=env,
        )
        for line in _yield_previous_lines(proc.stdout):
            logger.debug('rdiff-backup: %s' % line.decode('utf-8', 'replace'))
            # Since rdiff-backup 2.1.2b1 the line start with b'* '
            if line.startswith(TOKEN1):
                value = line[len(TOKEN1) :]
            elif line.startswith(TOKEN2):
                value = line[len(TOKEN2) :]
            else:
                continue
            # A new file or directory was processed. Extract the filename and
            # look for it on filesystem.
            fullpath, arcname = _lookup_filename(tmp_output, value)
            if not fullpath:
                logger.debug('error: file not found %r' % value)
                continue

            # Add the file to the archive.
            logger.debug('adding %s' % fullpath.decode('utf-8', 'replace'))
            try:
                # Send status header.
                if archive is None and send_header:
                    dest.write(b'ok\n')
                if archive is None:
                    # Then send archive.
                    archive = ARCHIVERS[kind](dest)
                archive.addfile(fullpath, arcname, encoding)
            except Exception:
                # Many error may happen when trying to add a file to the
                # archive. To be more resilient, capture error and continue
                # with the next file.
                logger.debug('error: fail to add %r' % fullpath, exc_info=1)

            # Delete file once added to the archive.
            try:
                file_stat = os.lstat(fullpath)
                if stat.S_ISREG(file_stat.st_mode) or stat.S_ISLNK(file_stat.st_mode):
                    os.remove(fullpath)
            except (OSError, ValueError):
                pass

        # return rdiff-backup restore exit-code
        return proc.wait()
    finally:
        # Close the pipe
        if archive:
            archive.close()
        elif send_header:
            dest.write(b'fail\n')
            dest.flush()
        # Clean-up the directory.
        if os.path.isdir(tmp_output):
            shutil.rmtree(tmp_output, ignore_errors=True)
        elif os.path.isfile(tmp_output):
            os.remove(tmp_output)
