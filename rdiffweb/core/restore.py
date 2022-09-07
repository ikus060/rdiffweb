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
"""
Module is responsible to restore rdiff-backup repository into an archive in a
transparent way to restore and archive at the same time allowing creation of the
archive as the restore processing is still running.

It also handle all the encoding and decoding of filenames to generate an
appropriate archive usable by the target system. In few circumstances it's
impossible to properly generate a valid filename depending of the archive types.
"""

import argparse
import logging
import os
import shutil
import sys
import tarfile
import tempfile
import traceback
from zipfile import ZIP_DEFLATED, ZIP_STORED, ZipFile

import rdiffweb
from rdiffweb.core.librdiff import LANG, STDOUT_ENCODING, find_rdiff_backup, popen

logger = logging.getLogger(__name__)

# Increase the chunk size to improve performance.
CHUNK_SIZE = 4096 * 10

# Token used by rdiff-backup
TOKEN = b'Processing changed file '


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


# Log everything to stderr.
def _print_stderr(msg, exc_info=False):
    """
    Print messages to stderr.
    """
    assert isinstance(msg, str)
    print(msg, file=sys.stderr)
    if exc_info:
        traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()


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
        if basename == file.decode(STDOUT_ENCODING, 'replace').encode(STDOUT_ENCODING, 'replace'):
            fullpath = os.path.join(dirname, file)
            arcname = os.path.relpath(fullpath, base)
            return fullpath, arcname
    return None, None


def restore(restore, restore_as_of, kind, encoding, dest, log=logger.debug):
    """
    Used to restore a file or a directory.
    restore: relative or absolute file or folder to be restored (unquoted)
    restore_as_of: date to restore
    kind: type of archive to generate or raw to stream a single file.
    encoding: encoding of the repository (used to properly encode the filename in archive)
    dest: a filename or a file handler where to write the archive.
    """
    assert isinstance(restore, bytes)
    assert isinstance(restore_as_of, int)
    assert kind in ARCHIVERS

    # Generate a temporary location used to restore data.
    # This location will be deleted after restore.
    tmp_output = tempfile.mkdtemp(prefix=b'rdiffweb_restore_')
    log('restoring data into temporary folder: %r' % tmp_output)

    # Search full path location of rdiff-backup.
    rdiff_backup_path = find_rdiff_backup()

    # Need to explicitly export some environment variable. Do not export
    # all of them otherwise it also export some python environment variable
    # and might brake rdiff-backup process.
    env = {
        'LANG': LANG,
    }
    if os.environ.get('TMPDIR'):
        env['TMPDIR'] = os.environ['TMPDIR']

    cmd = [
        rdiff_backup_path,
        b'-v',
        b'5',
        b'--restore-as-of=' + str(restore_as_of).encode('latin'),
        restore,
        tmp_output,
    ]
    log('executing %r with env %r' % (cmd, env))

    # Open an archive.
    archive = ARCHIVERS[kind](dest)
    try:
        # Read the output of rdiff-backup
        with popen(cmd, env=env) as output:
            for line in output:
                # Since rdiff-backup 2.1.2b1 the line start with b'* '
                if line.startswith(b'* '):
                    line = line[2:]
                line = line.rstrip(b'\n')
                log('rdiff-backup: %r' % line)
                if not line.startswith(TOKEN):
                    continue
                # A new file or directory was processed. Extract the filename and
                # look for it on filesystem.
                value = line[len(TOKEN) :]
                fullpath, arcname = _lookup_filename(tmp_output, line[len(TOKEN) :])
                if not fullpath:
                    log('error: file not found %r' % value)
                    continue

                # Add the file to the archive.
                log('adding %r' % fullpath)
                try:
                    archive.addfile(fullpath, arcname, encoding)
                except Exception:
                    # Many error may happen when trying to add a file to the
                    # archive. To be more resilient, capture error and continue
                    # with the next file.
                    log('error: fail to add %r' % fullpath, exc_info=1)

                # Delete file once added to the archive.
                if os.path.isfile(fullpath) or os.path.islink(fullpath):
                    os.remove(fullpath)
    finally:
        # Close the pipe
        archive.close()
        # Clean-up the directory.
        if os.path.isdir(tmp_output):
            shutil.rmtree(tmp_output, ignore_errors=True)
        elif os.path.isfile(tmp_output):
            os.remove(tmp_output)


def main():
    parser = argparse.ArgumentParser(description='Rdiffweb restore script.')
    parser.add_argument('--restore-as-of', type=int, required=True)
    parser.add_argument('--encoding', type=str, default='utf-8', help='Define the encoding of the repository.')
    parser.add_argument(
        '--kind', type=str, choices=ARCHIVERS, default='zip', help='Define the type of archive to generate.'
    )
    parser.add_argument('restore', type=str, help='Define the path of the file or directory to restore.')
    parser.add_argument('output', type=str, default='-', help='Define the location of the archive. Default to stdout.')
    parser.add_argument('--version', action='version', version='%(prog)s ' + rdiffweb.__version__)
    args = parser.parse_args()
    # handle encoding of the path.
    path = args.restore
    if isinstance(path, str):
        path = os.fsencode(path)
    # handle output
    if args.output == '-':
        output = sys.stdout.buffer
    else:
        output = open(args.output, 'wb')
    # Execute the restore.
    try:
        restore(path, args.restore_as_of, args.kind, args.encoding, output, log=_print_stderr)
    except Exception:
        _print_stderr('error: failure to create the archive', exc_info=1)
        sys.exit(1)


if __name__ == "__main__":
    main()
