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

from __future__ import absolute_import
from __future__ import unicode_literals

import bisect
import calendar
from collections import OrderedDict
from datetime import timedelta
import encodings
import gzip
import io
import logging
import os
import re
from shutil import copyfileobj
import shutil
import sys
import tempfile
import threading
import time
import weakref
import zlib

from builtins import bytes
from builtins import map
from builtins import object
from builtins import str
from future.utils import iteritems
from future.utils import python_2_unicode_compatible
from future.utils.surrogateescape import encodefilename
from past.builtins import cmp
from past.utils import old_div
import psutil

from rdiffweb.core import rdw_helpers
from rdiffweb.core.archiver import archive, ARCHIVERS
from rdiffweb.core.i18n import ugettext as _

try:
    import subprocess32 as subprocess  # @UnresolvedImport @UnusedImport
except:
    import subprocess  # @Reimport

PY3 = sys.version_info[0] == 3

# Define the logger
logger = logging.getLogger(__name__)

# Constant for the rdiff-backup-data folder name.
RDIFF_BACKUP_DATA = b"rdiff-backup-data"

# Size to be read from gzip
CHUNK_SIZE = 1024 * 1024

# Increment folder name.
INCREMENTS = b"increments"

# Zip file extension
ZIP_SUFFIX = b".zip"

# Tar gz extension
TARGZ_SUFFIX = b".tar.gz"

FS_ENCODING = (sys.getfilesystemencoding() or 'utf-8').lower()


@python_2_unicode_compatible
class ExecuteError(Exception):
    pass


@python_2_unicode_compatible
class FileError(Exception):
    pass


class AccessDeniedError(FileError):
    pass


class DoesNotExistError(FileError):
    pass


class SymLinkAccessDeniedError(FileError):
    pass


class UnknownError(FileError):
    pass


@python_2_unicode_compatible
class RdiffTime(object):

    """Time information has two components: the local time, stored in GMT as
    seconds since Epoch, and the timezone, stored as a seconds offset. Since
    the server may not be in the same timezone as the user, we cannot rely on
    the built-in localtime() functions, but look at the rdiff-backup string
    for timezone information.  As a general rule, we always display the
    "local" time, but pass the timezone information on to rdiff-backup, so
    it can restore to the correct state"""

    def __init__(self, value=None, tz_offset=None):
        assert value is None or isinstance(value, int) or isinstance(value, str)
        if value is None:
            # Get GMT time.
            self._time_seconds = int(time.time())
            self._tz_offset = 0
        elif isinstance(value, int):
            self._time_seconds = value
            self._tz_offset = tz_offset or 0
        elif isinstance(RdiffTime, int):
            self._time_seconds = value._time_seconds
            self._tz_offset = value._tz_offset
        else:
            self._from_str(value)

    def _from_str(self, timeString):
        try:
            date, daytime = timeString[:19].split("T")
            year, month, day = list(map(int, date.split("-")))
            hour, minute, second = list(map(int, daytime.split(":")))
            assert 1900 < year < 2100, year
            assert 1 <= month <= 12
            assert 1 <= day <= 31
            assert 0 <= hour <= 23
            assert 0 <= minute <= 59
            assert 0 <= second <= 61  # leap seconds

            timetuple = (year, month, day, hour, minute, second, -1, -1, 0)
            self._time_seconds = calendar.timegm(timetuple)
            self._tz_offset = self._tzdtoseconds(timeString[19:])
            self._tz_str()  # to get assertions there

        except (TypeError, ValueError, AssertionError):
            raise ValueError(timeString)

    def get_local_day_since_epoch(self):
        return self._time_seconds // (24 * 60 * 60)

    def epoch(self):
        return self._time_seconds - self._tz_offset

    def _tz_str(self):
        if self._tz_offset:
            hours, minutes = divmod(old_div(abs(self._tz_offset), 60), 60)
            assert 0 <= hours <= 23
            assert 0 <= minutes <= 59
            if self._tz_offset > 0:
                plusMinus = "+"
            else:
                plusMinus = "-"
            return "%s%s:%s" % (plusMinus, "%02d" % hours, "%02d" % minutes)
        else:
            return "Z"

    def set_time(self, hour, minute, second):
        year = time.gmtime(self._time_seconds)[0]
        month = time.gmtime(self._time_seconds)[1]
        day = time.gmtime(self._time_seconds)[2]
        self._time_seconds = calendar.timegm(
            (year, month, day, hour, minute, second, -1, -1, 0))

    def strftime(self, dateformat):
        value = time.strftime(dateformat, time.gmtime(self._time_seconds))
        if isinstance(value, bytes):
            value = value.decode(encoding='latin1')
        return value

    def _tzdtoseconds(self, tzd):
        """Given w3 compliant TZD, converts it to number of seconds from UTC"""
        if tzd == "Z":
            return 0
        assert len(tzd) == 6  # only accept forms like +08:00 for now
        assert (tzd[0] == "-" or tzd[0] == "+") and tzd[3] == ":"

        if tzd[0] == "+":
            plusMinus = 1
        else:
            plusMinus = -1

        return plusMinus * 60 * (60 * int(tzd[1:3]) + int(tzd[4:]))

    def __add__(self, other):
        """Support plus (+) timedelta"""
        assert isinstance(other, timedelta)
        return RdiffTime(self._time_seconds + int(other.total_seconds()), self._tz_offset)

    def __sub__(self, other):
        """Support minus (-) timedelta"""
        assert isinstance(other, timedelta) or isinstance(other, RdiffTime)
        # Sub with timedelta, return RdiffTime
        if isinstance(other, timedelta):
            return RdiffTime(self._time_seconds - int(other.total_seconds()), self._tz_offset)

        # Sub with RdiffTime, return timedelta
        if isinstance(other, RdiffTime):
            return timedelta(seconds=self._time_seconds - other._time_seconds)

    def __int__(self):
        """Return this date as seconds since epoch."""
        return self.epoch()

    def __lt__(self, other):
        assert isinstance(other, RdiffTime)
        return self.epoch() < other.epoch()

    def __le__(self, other):
        assert isinstance(other, RdiffTime)
        return self.epoch() <= other.epoch()

    def __gt__(self, other):
        assert isinstance(other, RdiffTime)
        return self.epoch() > other.epoch()

    def __ge__(self, other):
        assert isinstance(other, RdiffTime)
        return self.epoch() >= other.epoch()

    def __cmp__(self, other):
        assert isinstance(other, RdiffTime)
        return cmp(self.epoch(), other.epoch())

    def __eq__(self, other):
        return (isinstance(other, RdiffTime) and
                self.epoch() == other.epoch())

    def __hash__(self):
        return hash(self.epoch())

    def __str__(self):
        """return utf-8 string"""
        value = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(self._time_seconds))
        if isinstance(value, bytes):
            value = value.decode(encoding='latin1')
        return value + self._tz_str()

    def __repr__(self):
        """return second since epoch"""
        return "RdiffTime('" + str(self) + "')"
    
    __json__ = __str__

# Interfaced objects #


class DirEntry(object):

    """Includes name, isDir, fileSize, exists, and dict (changeDates) of sorted
    local dates when backed up"""

    def __init__(self, parent, path, exists, increments):
        assert isinstance(parent, RdiffRepo) or isinstance(parent, DirEntry)
        assert isinstance(path, bytes)

        # Keep reference to the path and repo object.
        if isinstance(parent, RdiffRepo):
            self._repo = parent
            self.path = path
        else:
            self._repo = parent._repo
            # Relative path to the repository.
            self.path = os.path.join(parent.path, path)
        # Absolute path to the directory
        self.full_path = os.path.normpath(os.path.join(self._repo.full_path, self.path))
        # May need to compute our own state if not provided.
        self.exists = exists
        # Store the increments sorted by date.
        # See self.last_change_date()
        self._increments = sorted(increments, key=lambda x: x.date)

    @property
    def dir_entries(self):
        """Get directory entries for the current path. It is similar to
        listdir() but for rdiff-backup."""

        logger.debug("get directory entries for [%r]", self.full_path)

        # Group increments by filename
        grouped_increment_entries = rdw_helpers.groupby(
            self._repo._get_increment_entries(self.path), lambda x: x.filename)

        # Check if the directory exists. It may not exist if
        # it has been delete
        existing_entries = []
        if os.path.isdir(self.full_path) and os.access(self.full_path, os.F_OK):
            # Get entries from directory structure
            existing_entries = os.listdir(self.full_path)
            # Remove "rdiff-backup-data" directory
            if self.path == b'':
                existing_entries.remove(RDIFF_BACKUP_DATA)

        # Process each increment entries and combine this with the existing
        # entries
        entriesDict = {}
        for filename, increments in iteritems(grouped_increment_entries):
            # Check if filename exists
            exists = filename in existing_entries
            # Create DirEntry to represent the item
            new_entry = DirEntry(
                self,
                filename,
                exists,
                increments)
            entriesDict[filename] = new_entry

        # Then add existing entries
        for filename in existing_entries:
            # Check if the entry was created by increments entry
            if filename in entriesDict:
                continue
            # The entry doesn't exists (mostly because it ever change). So
            # create a DirEntry to represent it
            new_entry = DirEntry(
                self,
                filename,
                True,
                [])
            entriesDict[filename] = new_entry

        # Return the values (so the DirEntry objects)
        return list(entriesDict.values())

    @property
    def display_name(self):
        """Return the most human readable filename. Without quote."""
        value = self._repo.unquote(os.path.basename(self.path))
        return self._repo._decode(value)

    @property
    def isdir(self):
        """Lazy check if entry is a directory"""
        if hasattr(self, '_isdir'):
            return self._isdir
        if self.exists:
            # If the entry exists, check if it's a directory
            self._isdir = os.path.isdir(self.full_path)
        else:
            # Check if increments is a directory
            self._isdir = False
            for increment in self._increments:
                if increment.is_missing:
                    # Ignore missing increment...
                    continue
                self._isdir = increment.isdir
                break
        return self._isdir

    @property
    def file_size(self):
        """Return the file size in bytes."""
        if hasattr(self, '_file_size'):
            return self._file_size
        if self.exists:
            self._file_size = os.lstat(self.full_path).st_size
        else:
            # The only viable place to get the filesize of a deleted entry
            # it to get it from file_statistics
            stats = self._repo.get_file_statistic(self.last_change_date)
            if stats:
                # File stats uses unquoted name.
                unquote_path = self._repo.unquote(self.path)
                self._file_size = stats.get_source_size(unquote_path)
            else:
                logger.warning("cannot find file statistic [%s]", self.last_change_date)
                self._file_size = 0
        return self._file_size

    @property
    def change_dates(self):
        """
        Return a list of dates when this item has changes. Represent the
        previous revision. From old to new.
        """
        # Exception for root path, use backups dates.
        if self.path == b'':
            return self._repo.backup_dates

        # Return previous computed value
        if hasattr(self, '_change_dates'):
            return self._change_dates

        # Compute the dates
        self._change_dates = []
        for increment in self._increments:
            # Skip "invisible" increments
            if not increment.has_suffix:
                continue
            # Get date of the increment as reference
            change_date = increment.date
            # If the increment is a "missing" increment, need to get the date
            # before the folder was removed.
            if not increment.is_snapshot and increment.is_missing:
                change_date = self._get_first_backup_after_date(change_date)

            if change_date and change_date not in self._change_dates:
                self._change_dates.append(change_date)

        # If the directory exists, add the last known backup date.
        if (self.exists and
                self._repo.last_backup_date and
                self._repo.last_backup_date not in self._change_dates):
            self._change_dates.append(self._repo.last_backup_date)

        # No need to sort the change date since increments are already sorted.

        # Return the list of dates.
        return self._change_dates

    @property
    def first_change_date(self):
        """Return first change date or False."""
        return self.change_dates and self.change_dates[0]

    def _get_first_backup_after_date(self, date):
        """ Iterates the mirror_metadata files in the rdiff data dir """
        index = bisect.bisect_right(self._repo.backup_dates, date)
        # Check if index is in range.
        if index >= len(self._repo.backup_dates):
            return None
        return self._repo.backup_dates[index]

    @property
    def last_change_date(self):
        """Return last change date or False."""
        return self.change_dates and self.change_dates[-1]

    def restore(self, restore_date, kind='zip'):
        """
        Restore the file identified by this directory entry.
        """
        return self._repo.restore(self, restore_date, kind)


class HistoryEntry(object):

    def __init__(self, repo, date):
        assert isinstance(repo, RdiffRepo)
        assert isinstance(date, RdiffTime)
        self._repo = weakref.proxy(repo)
        self.date = date

    @property
    def size(self):
        try:
            return self._repo.session_statistics[self.date].sourcefilesize
        except KeyError:
            return 0

    @property
    def has_errors(self):
        """Check if the history has errors."""
        try:
            return not self._repo._error_logs[self.date].is_empty
        except KeyError:
            return False

    @property
    def errors(self):
        """Return error messages."""
        # Get error log entry
        try:
            entry = self._repo._error_logs[self.date]
        except KeyError:
            return ""
        # Read the error log entry.
        try:
            return self._repo._decode(entry.read())
        except:
            return "Error reading log file: " + self._repo._decode(entry.name)

    @property
    def increment_size(self):
        try:
            return self._repo.session_statistics[self.date].incrementfilesize
        except KeyError:
            return 0


class IncrementEntry(object):

    """Instance of the class represent one increment at a specific date for one
    repository. The base repository is provided in the default constructor
    and the date is provided using an error_log.* file"""

    MISSING_SUFFIX = b".missing"

    SUFFIXES = [b".missing", b".snapshot.gz", b".snapshot",
                b".diff.gz", b".data.gz", b".data", b".dir", b".diff"]

    def __init__(self, parent, name):
        """Default constructor for an increment entry. User must provide the
            repository directory and an entry name. The entry name correspond
            to an error_log.* filename."""
        assert isinstance(parent, DirEntry) or isinstance(parent, RdiffRepo)
        assert isinstance(name, bytes)
        # Keep reference to the current path.
        if isinstance(parent, RdiffRepo):
            self.repo = weakref.proxy(parent)
        else:
            self.repo = parent._repo
        # The given entry name may has quote character, replace them
        self.name = name
        # Calculate the date of the increment.
        self.date = self.repo._extract_date(self.name)

    def _open(self, mode='rb'):
        """Should be used to open the increment file. This method handle
        compressed vs not-compressed file."""
        if self._is_compressed:
            return gzip.open(os.path.join(self.repo._data_path, self.name), mode)
        return open(os.path.join(self.repo._data_path, self.name), mode)

    def read(self):
        """Read the error file and return it's content. Raise exception if the
        file can't be read."""
        # To avoid opening n empty file, check the file size first.
        if self.is_empty:
            return b''
        return self._open().read()

    @property
    def filename(self):
        filename = IncrementEntry._remove_suffix(self.name)
        return filename.rsplit(b".", 1)[0]

    @property
    def has_suffix(self):
        for suffix in IncrementEntry.SUFFIXES:
            if self.name.endswith(suffix):
                return True
        return False

    @property
    def _is_compressed(self):
        return self.name.endswith(b".gz")

    @property
    def isdir(self):
        return self.name.endswith(b".dir")

    @property
    def is_missing(self):
        """Check if the curent entry is a missing increment."""
        return self.name.endswith(self.MISSING_SUFFIX)

    @property
    def is_snapshot(self):
        """Check if the current entry is a snapshot increment."""
        return (self.name.endswith(b".snapshot.gz") or
                self.name.endswith(b".snapshot"))

    @staticmethod
    def _remove_suffix(filename):
        """ returns None if there was no suffix to remove. """
        for suffix in IncrementEntry.SUFFIXES:
            if filename.endswith(suffix):
                return filename[:-len(suffix)]
        return filename

    @property
    def is_empty(self):
        """
        Check if the increment entry is empty.
        """
        fn = os.path.join(self.repo._data_path, self.name)
        return os.path.getsize(fn) == 0

    def __str__(self):
        return self.name


class FileStatisticsEntry(IncrementEntry):

    """
    Represent a single file_statistics.

    File Statistics contains different information related to each file of
    the backup. This class provide a simple and easy way to access this
    data.
    """

    def __init__(self, repo_path, name):
        IncrementEntry.__init__(self, repo_path, name)
        # check to ensure we have a file_statistics entry
        assert self.name.startswith(b"file_statistics.")
        assert self.name.endswith(b".data") or self.name.endswith(b".data.gz")

    def get_mirror_size(self, path):
        """Return the value of MirrorSize for the given file.
        path is the relative path from repo root."""
        try:
            return int(self._search(path)["mirror_size"])
        except:
            logger.warning("mirror size not found for [%r]", path, exc_info=1)
            return 0

    def get_source_size(self, path):
        """Return the value of SourceSize for the given file.
        path is the relative path from repo root."""
        try:
            return int(self._search(path)["source_size"])
        except:
            logger.warning("source size not found for [%r]", path, exc_info=1)
            return 0

    def _search(self, path):
        """
        This function search for a file entry in the file_statistics compress
        file. Since python gzip.open() seams to be 2 time slower, we directly use
        zlib library on python2.
        """
        logger.debug("read file_statistics [%r]", self.name)

        path += b' '

        # Open file are compress.
        if not PY3 and self._is_compressed:
            line = None
            fullfn = os.path.join(self.repo._data_path, self.name)
            in_file = gzip.open(fullfn, 'r')
            decompress = zlib.decompressobj(-zlib.MAX_WBITS)
            try:
                in_file._read_gzip_header()

                while 1:
                    buf = in_file.fileobj.read(CHUNK_SIZE)
                    if not buf:
                        break
                    if not line:
                        d_buf = decompress.decompress(buf)
                    else:
                        d_buf = line + decompress.decompress(buf)

                    # Search beginning of a line matching our filename
                    for line in io.BytesIO(d_buf):
                        if line.startswith(path):
                            break
            finally:
                in_file.fileobj.close()
                decompress = None
        else:
            with self._open() as f:
                for line in f:
                    if not line.startswith(path):
                        continue
                    break

        # Split the line into array
        data = line.rstrip(b'\r\n').rsplit(b' ', 4)
        # From array create an entry
        return {
            'changed': data[1],
            'source_size': data[2],
            'mirror_size': data[3],
            'increment_size': data[4]}


class SessionStatisticsEntry(IncrementEntry):

    """Represent a single session_statistics."""

    def __init__(self, repo_path, name):
        # check to ensure we have a file_statistics entry
        assert name.startswith(b"session_statistics")
        assert name.endswith(b".data") or name.endswith(b".data.gz")
        IncrementEntry.__init__(self, repo_path, name)

    def _load(self):
        """This method is used to read the session_statistics and create the
        appropriate structure to quickly get the data.

        File Statistics contains different information related to each file of
        the backup. This class provide a simple and easy way to access this
        data."""

        with self._open('r') as f:
            for line in f.readlines():
                # Skip comments
                if line.startswith("#"):
                    continue
                # Read the line into array
                line = line.rstrip('\r\n')
                data_line = line.split(" ", 2)
                # Read line into tuple
                (key, value) = tuple(data_line)[0:2]
                if '.' in value:
                    value = float(value)
                else:
                    value = int(value)
                setattr(self, key.lower(), value)

    def __getattr__(self, name):
        """
        Intercept attribute getter to load the file.
        """
        if name in ['starttime', 'endtime', 'elapsedtime', 'sourcefiles', 'sourcefilesize',
                    'mirrorfiles', 'mirrorfilesize', 'newfiles', 'newfilesize', 'deletedfiles',
                    'deletedfilesize', 'changedfiles', 'changedsourcesize', 'changedmirrorsize',
                    'incrementfiles', 'incrementfilesize', 'totaldestinationsizechange', 'errors']:
            self._load()
        return self.__dict__[name]


@python_2_unicode_compatible
class RdiffRepo(object):

    """Represent one rdiff-backup repository."""

    def __init__(self, user_root, path, encoding=FS_ENCODING):
        if isinstance(user_root, str):
            user_root = encodefilename(user_root)
        if isinstance(path, str):
            path = encodefilename(path)
        assert isinstance(user_root, bytes)
        assert isinstance(path, bytes)
        self._encoding = encodings.search_function(encoding)
        assert self._encoding
        self.path = path.strip(b"/")
        self.full_path = os.path.realpath(os.path.join(user_root, self.path))

        # The location of rdiff-backup-data directory.
        self._data_path = os.path.join(self.full_path, RDIFF_BACKUP_DATA)
        assert isinstance(self._data_path, bytes)
        self._increment_path = os.path.join(self._data_path, INCREMENTS)

    @property
    def backup_dates(self):
        """Return a list of dates when backup was executed. This list is
        sorted from old to new (ascending order). To identify dates,
        'mirror_metadata' file located in rdiff-backup-data are used."""
        if not hasattr(self, '_backup_dates'):
            logger.debug("get backup dates for [%r]", self.full_path)
            self._backup_dates = sorted([
                self._extract_date(x)
                for x in self._data_entries
                if x.startswith(b"mirror_metadata")])
        return self._backup_dates

    @property
    def _data_entries(self):
        try:
            return os.listdir(self._data_path)
        except:
            # Return empty list when the directory can't be access.
            return []

    def delete(self):
        """Delete the repository permanently."""
        # Not sure if error should be ignored.
        shutil.rmtree(self.full_path)

    @property
    def display_name(self):
        """Return the most human representation of the repository name."""
        # NOTE : path may be empty, so return a simple string.
        if self.path:
            return self._decode(self.unquote(self.path))
        return self._decode(self.unquote(os.path.basename(self.full_path)))

    def _decode(self, value, errors='replace'):
        """Used to decode a repository path into unicode."""
        assert isinstance(value, bytes)
        return self._encoding.decode(value, errors)[0]

    @property
    def _error_logs(self):
        """Return dict of {date: IncrementEntry} to represent each file statistics."""
        if not hasattr(self, '_error_logs_data'):
            self._error_logs_data = {
                self._extract_date(x): IncrementEntry(self, x)
                for x in self._data_entries
                if x.startswith(b"error_log.")}
        return self._error_logs_data

    def execute(self, *args):
        """
        Execute rdiff-backup command.
        """
        assert all(isinstance(arg, bytes) for arg in args)
        # Need to explicitly export some environment variable. Do not export
        # all of them otherwise it also export some python environment variable
        # and might brake rdiff-backup execution.
        env = {}
        if os.environ.get('TMPDIR'):
            env['TMPDIR'] = os.environ['TMPDIR']

        parms = [b'rdiff-backup']
        parms.extend(args)
        execution = subprocess.Popen(
            parms, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env)

        results = {}
        output, error = execution.communicate()
        results['exitCode'] = execution.wait()
        if results['exitCode'] != 0:
            error = error.decode(encoding=sys.getdefaultencoding(), errors='replace')
            raise ExecuteError(error)

        return (output, error)

    def _extract_date(self, filename):
        """
        Extract date from rdiff-backup filenames.
        """
        # Remove suffix from filename
        filename = IncrementEntry._remove_suffix(filename)
        # Remove prefix from filename
        date_string = filename.rsplit(b".", 1)[-1]
        # Unquote string
        date_string = self.unquote(date_string)
        try:
            return RdiffTime(date_string.decode())
        except:
            logger.warn('fail to parse date [%r]', date_string, exc_info=1)
            return None

    @property
    def _file_statistics(self):
        """Return dict of {date: filename} to represent each file statistics."""
        if not hasattr(self, '_file_statistics_data'):
            self._file_statistics_data = {
                self._extract_date(x): x
                for x in self._data_entries
                if x.startswith(b"file_statistics.")}
        return self._file_statistics_data

    def get_file_statistic(self, date):
        """Return the file statistic for the given date.
        Try to search for the given file statistic and return an object to
        represent it.

        Try to be lazy as possible. To list file_statistics then only create
        object if required.
        """
        # Get reference to the FileStatisticsEntry
        try:
            value = self._file_statistics[date]
            if not isinstance(value, FileStatisticsEntry):
                entry = FileStatisticsEntry(self, value)
                self._file_statistics[date] = entry
                return entry
            return self._file_statistics[date]
        except KeyError:
            return None

    def get_history_entries(self,
                            numLatestEntries=-1,
                            earliestDate=None,
                            latestDate=None,
                            reverse=False):
        """Returns a list of HistoryEntry's
        earliestDate and latestDate are inclusive."""

        assert isinstance(numLatestEntries, int)
        assert (earliestDate is None or
                isinstance(earliestDate, RdiffTime))
        assert (latestDate is None or
                isinstance(latestDate, RdiffTime))

        logger.debug("get history entries for [%r]", self.full_path)

        entries = []
        # Take care of reverse
        backup_dates = reversed(self.backup_dates) if reverse else self.backup_dates
        # Loop to dates
        for backup_date in backup_dates:
            # compare local times because of discrepancy between client/server
            # time zones
            if earliestDate and backup_date < earliestDate:
                continue

            if latestDate and backup_date > latestDate:
                continue

            entries.append(HistoryEntry(self, backup_date))

            if numLatestEntries != -1 and len(entries) == numLatestEntries:
                return entries

        return entries

    def _get_increment_entries(self, path):
        """
        Get the increment entries for the current path. This path is located
        under rdiff-backup-data/increments.
        """
        # Compute increment directory location.
        p = os.path.join(self._increment_path, path.strip(b'/'))
        assert p.startswith(self.full_path)

        # Check if increment directory exists. The path may not exists if
        # the folder always exists and never changed.
        if not os.access(p, os.F_OK):
            return []

        # List content of the increment directory.
        # Ignore sub-directories.
        entries = [
            IncrementEntry(self, x)
            for x in os.listdir(p)
            if not os.path.isdir(os.path.join(p, x))]
        return entries

    def get_path(self, path):
        """Return a new instance of DirEntry to represent the given path."""
        assert isinstance(path, bytes)
        path = os.path.normpath(path.strip(b"/"))

        # Get if the path request is the root path.
        if path == b'.':
            return DirEntry(self, b'', True, [])

        # Remove access to rdiff-backup-data directory.
        if path.startswith(RDIFF_BACKUP_DATA):
            raise AccessDeniedError(path)

        # Make sure the normalized path is part of the repo.
        p = os.path.realpath(os.path.join(self.full_path, path))
        if not p.startswith(self.full_path):
            raise SymLinkAccessDeniedError(path)

        # Check if path exists or has increment. If not raise an exception.
        exists = os.path.exists(p)
        fn = os.path.basename(p)
        increments = [e for e in self._get_increment_entries(os.path.dirname(path))
                      if e.filename == fn]
        if not exists and not increments:
            logger.error("path [%r] doesn't exists", path)
            raise DoesNotExistError(path)

        # Create a directory entry.
        return DirEntry(self, path, exists, increments)

    @property
    def last_backup_date(self):
        """Return the last known backup dates."""
        if len(self.backup_dates) > 0:
            return self.backup_dates[-1]
        return None

    def restore(self, path, restore_date, kind='zip'):
        """Used to restore the given file located in this path."""
        assert isinstance(path, bytes) or isinstance(path, DirEntry)
        assert isinstance(restore_date, RdiffTime) or isinstance(restore_date, int)
        assert kind in ARCHIVERS

        # Get the info we need from DirEntry
        if isinstance(path, DirEntry):
            entry = path
            path = path.path
        else:
            path = path.strip(b"/")
            entry = None

        # Determine the file name to be restore (from rdiff-backup
        # point of view).
        file_to_restore = os.path.join(self.full_path, path)
        file_to_restore = self.unquote(file_to_restore)

        # Convert the date into epoch.
        if isinstance(restore_date, RdiffTime):
            restore_date = restore_date.epoch()

        # Define a nice filename for the archive or file to be created.
        if path == b"":
            filename = "%s.%s" % (self.display_name, kind)
        else:
            filename_b = os.path.basename(path)
            # Unquote the filename (remove ;090).
            filename_b = self.unquote(filename_b)
            # Decode string as repo encoding.
            filename = self._decode(filename_b)
            # Append archive extention if a directory
            entry = entry or self.get_path(path)
            if entry and entry.isdir:
                filename = filename + '.' + kind

        # Generate a temporary location used to restore data.
        output = tempfile.mkdtemp(prefix='rdiffweb_restore_')
        if isinstance(output, str):
            output = output.encode(encoding=FS_ENCODING)

        # Asynchronously create an archive if multiple file.
        def _async(fdst):
            try:
                # Change thread name
                threading.currentThread().name = 'Restore' + threading.currentThread().name

                # Execute rdiff-backup to restore the data.
                logger.info("execute rdiff-backup --restore-as-of=%s %r %r", restore_date, file_to_restore, output)
                try:
                    self.execute(
                        b"--restore-as-of=" + str(restore_date).encode(encoding='latin1'),
                        file_to_restore,
                        output)
                except ExecuteError:
                    raise UnknownError('unable to restore')
                logger.debug("restored locally completed")

                # Check the result
                if not os.access(output, os.F_OK):
                    error = '''rdiff-backup claimed success, but did not restore
                            anything. This indicates a bug in rdiffweb. Please
                            report this to a developer.'''
                    raise UnknownError(error)

                # Archive data or pipe data.
                if os.path.isdir(output):
                    archive(output, fdst, kind=kind, encoding=self._encoding.name)
                else:
                    # Pipe the content of the file.
                    with io.open(output, 'rb') as fsrc:
                        copyfileobj(fsrc, fdst)
                logger.debug("restore completed")
            except:
                logger.error('restore failed', exc_info=1)
            finally:
                # Make sure to close pipe.
                fdst.close()
                # Clean up temp file or dir.
                if os.path.isdir(output):
                    shutil.rmtree(output, ignore_errors=True)
                elif os.path.exists(output):
                    os.remove(output)

        # Start new thread.
        rfd, wfd = os.pipe()
        r = io.open(rfd, 'rb')
        w = io.open(wfd, 'wb')
        try:
            thread = threading.Thread(target=_async, args=(w,))
            thread.start()
            # Return one of a stream.
            return filename, r
        except Exception as e:
            # If creation of thread fail, close pipe.
            r.close()
            w.close()
            # Then re-raise issue
            logger.error('fail to create new thread', exc_info=1)
            raise e

    @property
    def status(self):
        """Check if a backup is in progress for the current repo."""

        # Check if the repository exists.
        # Make sure repoRoot is a valid rdiff-backup repository
        if (not os.access(self._data_path, os.F_OK) or
                not os.path.isdir(self._data_path)):
            return ('failed', _('The repository cannot be found or is badly damaged.'))
        
        # Filter the files to keep current_mirror.* files
        current_mirrors = [
            x
            for x in self._data_entries
            if x.startswith(b"current_mirror.")]

        pid_re = re.compile(b"^PID\s*([0-9]+)", re.I | re.M)

        def extract_pid(current_mirror):
            """Return process ID from a current mirror marker, if any"""
            entry = IncrementEntry(self, current_mirror)
            match = pid_re.search(entry.read())
            if not match:
                return None
            else:
                return int(match.group(1))

        # Read content of the file and check if pid still exists
        for current_mirror in current_mirrors:
            pid = extract_pid(current_mirror)
            try:
                p = psutil.Process(pid)
                if any('rdiff-backup' in c for c in p.cmdline()):
                    return ('in_progress', _('A backup is currently in progress to this repository.'))
            except psutil.NoSuchProcess:
                logger.debug('pid [%s] does not exists', pid)
                pass
        # If multiple current_mirror file exists and none of them are associated to a PID, this mean the last backup was interrupted.
        # Also, if the last backup date is undefined, this mean the first initial backup was interrupted.
        if len(current_mirrors) > 1 or not self.last_backup_date:
            return ('interrupted', _('The previous backup seams to have failed.'))

        return ('ok', '')

    @property
    def session_statistics(self):
        """Return list of IncrementEntry to represent each sessions
        statistics."""
        if not hasattr(self, '_session_statistics_data'):
            data = (
                SessionStatisticsEntry(self, x)
                for x in sorted(self._data_entries)
                if x.startswith(b"session_statistics."))
            self._session_statistics_data = OrderedDict([(x.date, x) for x in data])
        return self._session_statistics_data

    def unquote(self, name):
        """Remove quote from the given name."""
        assert isinstance(name, bytes)

        # This function just gives back the original text if it can decode it
        def unquoted_char(match):
            """For each ;000 return the corresponding byte."""
            if not len(match.group()) == 4:
                return match.group
            try:
                return bytes([int(match.group()[1:])])
            except:
                return match.group

        # Remove quote using regex
        return re.sub(b";[0-9]{3}", unquoted_char, name, re.S)

    def __str__(self):
        return "%r" % (self.full_path,)
