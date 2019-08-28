#!/usr/bin/python
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
Module responsible to archive repository data in a transparent way. This module
is greatly inspired from Mercurial archival module.
"""

from __future__ import unicode_literals

import codecs
from future.builtins import bytes
from future.builtins import str
from itertools import chain
import logging
import os
import stat
import struct
import sys
import tarfile
import time
from zipfile import ZipFile, ZipInfo, ZIP_STORED, ZIP64_LIMIT, crc32, zlib, \
    ZIP_DEFLATED


logger = logging.getLogger(__name__)

# Detect python version.
PY3 = sys.version_info[0] == 3

# Increase the chunk size to improve performance.
CHUNK_SIZE = 4096 * 10


class TarArchiver(object):
    """
    Archiver to create tar archive (with compression).
    """

    def __init__(self, dest, compression=''):
        assert compression in ['', 'gz', 'bz2']
        mode = "w|" + compression

        # Open the tar archive with the right method.
        if isinstance(dest, str):
            self.z = tarfile.open(name=dest, mode=mode, encoding='UTF8')
            self.fileobj = None
        else:
            self.z = tarfile.open(fileobj=dest, mode=mode, encoding='UTF8')
            self.fileobj = dest

    def addfile(self, filename, arcname):
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
        if sys.version_info < (3, 5):
            self.z = NonSeekZipFile(dest, 'w', compress)
        else:
            self.z = ZipFile(dest, 'w', compress)

    def addfile(self, filename, arcname):
        # Python as of today doesn't support symlink or pipe in zipfile.
        # Skip them. See bug #26269 and #18595
        if os.path.islink(filename) or not (os.path.isfile(filename) or os.path.isdir(filename)):
            return
        self.z.write(filename, arcname)

    def close(self):
        self.z.close()


ARCHIVERS = {
    'tar': TarArchiver,
    'tbz2': lambda dest, : TarArchiver(dest, 'bz2'),
    'tar.bz2': lambda dest: TarArchiver(dest, 'bz2'),
    'tar.gz': lambda dest: TarArchiver(dest, 'gz'),
    'tgz': lambda dest: TarArchiver(dest, 'gz'),
    'zip': ZipArchiver,
}


def archive(path, dest, encoding, kind='zip', callback=None):
    """
    Used to archive the given `path`.

    `dest` define the destination of archive. Either a filename or fileobj.

    `encoding` the encoding of path.

    `kind` define the archive type to be created.

    `callback` a function to be called after processing each file.
    """
    assert isinstance(path, bytes)
    assert dest
    assert encoding
    assert kind in ARCHIVERS

    # Get the right decode function.
    decoder = codecs.getdecoder(encoding)
    assert decoder
    if PY3 and kind != 'zip':
        def decode(val):
            return decoder(val, 'surrogateescape')[0]
    else:
        def decode(val):
            return decoder(val, 'replace')[0]

    # Norm the path (remove ../, ./)
    path = os.path.normpath(path)

    # Create a tar.gz archive
    logger.info("creating archive from [%r]", path)
    archiver = ARCHIVERS[kind](dest)

    # Add files to the archive
    for root, dirs, files in os.walk(path, topdown=True, followlinks=False):
        for name in chain(dirs, files):
            filename = os.path.join(root, name)
            assert filename.startswith(path)
            arcname = filename[len(path) + 1:]
            if PY3:
                # Py3, doesn't support bytes file path. So we need
                # to use surrogate escape to escape invalid unicode char.
                filename = filename.decode('ascii', 'surrogateescape')
            # Always need to decode the arcname as unicode to support non-ascii.
            arcname = decode(arcname)
            assert isinstance(arcname, str)

            # Add the file to the archive.
            logger.debug("adding file [%r] to archive", filename)
            archiver.addfile(filename, arcname)
            logger.debug("file [%r] added to archive", filename)

            # Make a call to callback function
            if callback:
                callback(filename)

    # Close the archive
    archiver.close()


def main():
    """
    Main function called when start from command line.
    """

    # Read arguments
    args = sys.argv[1:]
    dest = args[0]
    src = args[1]
    if isinstance(src, str):
        src = src.encode('utf-8')

    # Determine the archive kind.
    kind = 'zip'
    if dest.endswith('.tar'):
        kind = 'tar'
    elif dest.endswith('.tar.gz') or dest.endswith('.tgz'):
        kind = 'tar.gz'
    elif dest.endswith('.tar.bz2') or dest.endswith('.tbz2'):
        kind = 'tar.bz2'

    # Run archiver
    with open(dest, 'wb') as f:
        archive(src, f, decode=lambda name: name.decode('utf8', 'replace'), kind=kind)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    main()
