# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2019 rdiffweb contributors
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
from distutils import spawn
import logging
import os
import rdiffweb
import shutil
import stat
import struct
import subprocess
import sys
import tarfile
import tempfile
import threading
import time
import traceback
from zipfile import ZipFile, ZipInfo, ZIP_STORED, ZIP64_LIMIT, crc32, zlib, \
    ZIP_DEFLATED

logger = logging.getLogger(__name__)

# Increase the chunk size to improve performance.
CHUNK_SIZE = 4096 * 10

# Token used by rdiff-backup
TOKEN = b'Processing changed file '

# PATH for executable lookup
PATH = path = os.path.dirname(sys.executable) + os.pathsep + os.environ['PATH']

# Define the default LANG environment variable to be passed to rdiff-backup
# restore command line to make sure the binary output stdout as utf8 otherwise
# we end up with \x encoded characters.
STDOUT_ENCODING = 'utf-8'
LANG = "en_US." + STDOUT_ENCODING


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


class _Tellable(object):
    """
    Provide tell method for zipfile.ZipFile when writing to HTTP
    response file object.

    This is a workaround to bug #23252
    """

    def __init__(self, fp):
        self.fp = fp
        self.offset = 0

    def __getattr__(self, key):
        return getattr(self.fp, key)

    def write(self, s):
        self.fp.write(s)
        self.offset += len(s)

    def tell(self):
        return self.offset


class NonSeekZipFile(ZipFile):
    """
    Fix to support non seek-able stream. Modification taken from python 3.5.
    This is a workaround to bug #23252
    """

    dereference = False  # If true, add content of linked file to the  tar file, else the link.

    def __init__(self, dest, *args, **kwargs):
        if not isinstance(dest, str):
            try:
                dest.tell()
            except (AttributeError, IOError):
                dest = _Tellable(dest)
        ZipFile.__init__(self, dest, *args, **kwargs)

    def write(self, filename, arcname=None, compress_type=None):
        """
        Fixed version of write supporting bitflag 0x08 to write crc and size
        at end of file.
        """
        if not self.fp:
            raise RuntimeError(
                "Attempt to write to ZIP archive that was already closed")

        st = os.stat(filename)
        isdir = stat.S_ISDIR(st.st_mode)
        mtime = time.localtime(st.st_mtime)
        date_time = mtime[0:6]
        # Create ZipInfo instance to store file information
        if arcname is None:
            arcname = filename
        arcname = os.path.normpath(os.path.splitdrive(arcname)[1])
        while arcname[0] in (os.sep, os.altsep):
            arcname = arcname[1:]
        if isdir:
            arcname += '/'
        zinfo = ZipInfo(arcname, date_time)
        zinfo.external_attr = (st[0] & 0xFFFF) << 16  # Unix attributes
        if isdir:
            zinfo.compress_type = ZIP_STORED
        elif compress_type is None:
            zinfo.compress_type = self.compression
        else:
            zinfo.compress_type = compress_type

        zinfo.file_size = st.st_size
        zinfo.flag_bits = 0x00
        zinfo.header_offset = self.fp.tell()  # Start of header bytes

        self._writecheck(zinfo)
        self._didModify = True

        if isdir:
            zinfo.file_size = 0
            zinfo.compress_size = 0
            zinfo.CRC = 0
            zinfo.external_attr |= 0x10  # MS-DOS directory flag
            self.filelist.append(zinfo)
            self.NameToInfo[zinfo.filename] = zinfo
            self.fp.write(zinfo.FileHeader())
            self.start_dir = self.fp.tell()
            return

        zinfo.flag_bits |= 0x08
        with open(filename, "rb") as fp:
            # Must overwrite CRC and sizes with correct data later
            zinfo.CRC = CRC = 0
            zinfo.compress_size = compress_size = 0
            try:
                # Python > 2.7.3
                # Compressed size can be larger than uncompressed size
                zip64 = self._allowZip64 and \
                    zinfo.file_size * 1.05 > ZIP64_LIMIT
                self.fp.write(zinfo.FileHeader(zip64))
            except TypeError:
                # Python <= 2.7.3
                zip64 = zinfo.file_size > ZIP64_LIMIT or compress_size > ZIP64_LIMIT
                self.fp.write(zinfo.FileHeader())
            if zinfo.compress_type == ZIP_DEFLATED:
                cmpr = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION,
                                        zlib.DEFLATED, -15)
            else:
                cmpr = None
            file_size = 0
            while 1:
                buf = fp.read(CHUNK_SIZE)
                if not buf:
                    break
                file_size = file_size + len(buf)
                CRC = crc32(buf, CRC) & 0xffffffff
                if cmpr:
                    buf = cmpr.compress(buf)
                    compress_size = compress_size + len(buf)
                self.fp.write(buf)
        if cmpr:
            buf = cmpr.flush()
            compress_size = compress_size + len(buf)
            self.fp.write(buf)
            zinfo.compress_size = compress_size
        else:
            zinfo.compress_size = file_size
        zinfo.CRC = CRC
        zinfo.file_size = file_size
        if not zip64 and self._allowZip64:
            if file_size > ZIP64_LIMIT:
                raise RuntimeError('File size has increased during compressing')
            if compress_size > ZIP64_LIMIT:
                raise RuntimeError('Compressed size larger than uncompressed size')
        # Write CRC and file sizes after the file data
        fmt = b'<LQQ' if zip64 else b'<LLL'
        self.fp.write(struct.pack(fmt, zinfo.CRC, zinfo.compress_size,
                                  zinfo.file_size))
        self.start_dir = self.fp.tell()
        self.filelist.append(zinfo)
        self.NameToInfo[zinfo.filename] = zinfo


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
    'tbz2': lambda dest, : TarArchiver(dest, 'bz2'),
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


def _readerthread(stderr):
    """
    Read stderr and pipe each line to logger.
    """
    for line in stderr:
        logger.info(line.decode(STDOUT_ENCODING, 'replace').strip('\n'))
    stderr.close()


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


def restore(restore, restore_as_of, kind, encoding, dest, log=logger.info):
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
    assert isinstance(tmp_output, bytes)
    log('restoring data into temporary folder: %r' % tmp_output)

    # Search full path location of rdiff-backup.
    # To work around issue related to different PATH
    rdiff_backup_path = spawn.find_executable('rdiff-backup')
    assert rdiff_backup_path, "can't find `rdiff-backup` executable in PATH: " + PATH
    rdiff_backup_path = os.fsencode(rdiff_backup_path)

    # Need to explicitly export some environment variable. Do not export
    # all of them otherwise it also export some python environment variable
    # and might brake rdiff-backup process.
    env = {
        'LANG': LANG,
    }
    if os.environ.get('TMPDIR'):
        env['TMPDIR'] = os.environ['TMPDIR']

    cmd = [rdiff_backup_path , b'-v', b'5', b'--restore-as-of=' + str(restore_as_of).encode('latin'), restore, tmp_output]
    log('executing %r with env %r' % (cmd, env))
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env)

    # Open an archive.
    archive = ARCHIVERS[kind](dest)
    try:
        # Read the output of rdiff-backup
        for line in process.stdout:
            line = line.rstrip(b'\n')
            log('rdiff-backup: %r' % line)
            if not line.startswith(TOKEN):
                continue
            # A new file or directory was processed. Extract the filename and
            # look for it on filesystem.
            value = line[len(TOKEN):]
            fullpath, arcname = _lookup_filename(tmp_output, line[len(TOKEN):])
            if not fullpath:
                log('error: file not found %r' % value)
                continue

            # Add the file to the archive.
            log('adding %r' % fullpath)
            try:
                archive.addfile(fullpath, arcname, encoding)
            except:
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
        # Kill the process during exception.
        process.kill()
        # Clean-up the directory.
        if os.path.isdir(tmp_output):
            shutil.rmtree(tmp_output, ignore_errors=True)
        elif os.path.isfile(tmp_output):
            os.remove(tmp_output)


def call_restore(path, restore_as_of, encoding, kind):
    """
    Used to call restore as a subprocess.
    """
    assert isinstance(restore_as_of, int), "restore_as_of must be a int"
    assert kind and kind in ARCHIVERS, "kind must be in " + ARCHIVERS
    assert encoding

    # Lookup the executable.
    cmd = spawn.find_executable('rdiffweb-restore', PATH)
    assert cmd, "can't find `rdiffweb-restore` executable in PATH: " + PATH
    cmd = os.fsencode(cmd)

    # Call the process.
    cmdline = [cmd, b'--restore-as-of', str(restore_as_of).encode('latin'), b'--encoding', encoding, b'--kind', kind, path, b'-']
    logger.info('executing: %r' % cmdline)
    process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Pipe stderr to logger
    t = threading.Thread(target=_readerthread, args=(process.stderr,))
    t.daemon = True
    t.start()

    # TODO We should wait half a second and check if the process failed.
    return process.stdout


def main():
    parser = argparse.ArgumentParser(description='Rdiffweb restore script.')
    parser.add_argument('--restore-as-of', type=int, required=True)
    parser.add_argument('--encoding', type=str, default='utf-8', help='Define the encoding of the repository.')
    parser.add_argument('--kind', type=str, choices=ARCHIVERS, default='zip', help='Define the type of archive to generate.')
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
    except:
        _print_stderr('error: failure to create the archive', exc_info=1)
        sys.exit(1)


if __name__ == "__main__":
    main()
