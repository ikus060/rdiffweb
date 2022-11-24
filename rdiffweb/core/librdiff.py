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

import bisect
import calendar
import encodings
import logging
import os
import re
import shutil
import subprocess
import sys
import threading
import time
from datetime import timedelta
from subprocess import CalledProcessError

import psutil
from cached_property import cached_property

from rdiffweb.tools.i18n import ugettext as _

# Define the logger
logger = logging.getLogger(__name__)

# Constant for the rdiff-backup-data folder name.
RDIFF_BACKUP_DATA = b"rdiff-backup-data"

# Increment folder name.
INCREMENTS = b"increments"

# Define the default LANG environment variable to be passed to rdiff-backup
# restore command line to make sure the binary output stdout as utf8 otherwise
# we end up with \x encoded characters.
STDOUT_ENCODING = 'utf-8'
LANG = "en_US." + STDOUT_ENCODING


def rdiff_backup_version():
    """
    Get rdiff-backup version
    """
    try:
        output = subprocess.check_output([find_rdiff_backup(), '--version'])
        m = re.search(b'([0-9]+).([0-9]+).([0-9]+)', output)
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))
    except Exception:
        return (0, 0, 0)


def find_rdiff_backup():
    """
    Lookup for `rdiff-backup` executable. Raise an exception if not found.
    """
    cmd = shutil.which('rdiff-backup')
    if not cmd:
        raise FileNotFoundError("can't find `rdiff-backup` executable in PATH: %s" % os.environ['PATH'])
    return os.fsencode(cmd)


def find_rdiff_backup_delete():
    """
    Lookup for `rdiff-backup-delete` executable. Raise an exception if not found.
    """
    cmd = shutil.which('rdiff-backup-delete')
    if not cmd:
        raise FileNotFoundError(
            "can't find `rdiff-backup-delete` executable in PATH: %s, make sure you have rdiff-backup >= 2.0.1 installed"
            % os.environ['PATH']
        )
    return os.fsencode(cmd)


def unquote(name):
    """Remove quote from the given name."""
    assert isinstance(name, bytes)

    # This function just gives back the original text if it can decode it
    def unquoted_char(match):
        """For each ;000 return the corresponding byte."""
        if len(match.group()) != 4:
            return match.group
        try:
            return bytes([int(match.group()[1:])])
        except ValueError:
            return match.group

    # Remove quote using regex
    return re.sub(b";[0-9]{3}", unquoted_char, name, re.S)


def popen(cmd, stderr=None, env=None):
    """
    Alternative to os.popen() to support a `cmd` with a list of arguments and
    return a file object that return bytes instead of string.

    `stderr` could be subprocess.STDOUT or subprocess.DEVNULL or a function.
    Otherwise, the error is redirect to logger.
    """
    # Check if stderr should be pipe.
    pipe_stderr = stderr == subprocess.PIPE or hasattr(stderr, '__call__') or stderr is None
    proc = subprocess.Popen(
        cmd,
        shell=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE if pipe_stderr else stderr,
        env=env,
    )
    if pipe_stderr:
        t = threading.Thread(target=_readerthread, args=(proc.stderr, stderr))
        t.daemon = True
        t.start()
    return _wrap_close(proc.stdout, proc)


# Helper for popen() to redirect stderr to a logger.


def _readerthread(stream, func):
    """
    Read stderr and pipe each line to logger.
    """
    func = func or logger.debug
    for line in stream:
        func(line.decode(STDOUT_ENCODING, 'replace').strip('\n'))
    stream.close()


# Helper for popen() to close process when the pipe is closed.


class _wrap_close:
    def __init__(self, stream, proc):
        self._stream = stream
        self._proc = proc

    def close(self):
        self._stream.close()
        returncode = self._proc.wait()
        if returncode == 0:
            return None
        return returncode

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def __getattr__(self, name):
        return getattr(self._stream, name)

    def __iter__(self):
        return iter(self._stream)


class AccessDeniedError(Exception):
    pass


class DoesNotExistError(Exception):
    pass


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
        else:
            self._from_str(value)

    def _from_str(self, time_string):
        if time_string[10] != 'T':
            raise ValueError('missing date time separator (T): ' + time_string)
        if time_string[19] not in ['-', '+', 'Z']:
            raise ValueError('missing timezone info (-, + or Z): ' + time_string)
        if time_string[4] != '-' or time_string[7] != '-':
            raise ValueError('missing date separator (-): ' + time_string)
        if not (time_string[13] in [':', '-'] and time_string[16] in [':', '-']):
            raise ValueError('missing date separator (-): ' + time_string)
        try:
            year = int(time_string[0:4])
            if not (1900 < year < 2200):
                raise ValueError('unexpected year value between 1900 and 2200: ' + str(year))
            month = int(time_string[5:7])
            if not (1 <= month <= 12):
                raise ValueError('unexpected month value between 1 and 12: ' + str(month))
            day = int(time_string[8:10])
            if not (1 <= day <= 31):
                raise ValueError('unexpected day value between 1 and 31: ' + str(day))
            hour = int(time_string[11:13])
            if not (0 <= hour <= 23):
                raise ValueError('unexpected hour value between 1 and 23: ' + str(hour))
            minute = int(time_string[14:16])
            if not (0 <= minute <= 60):
                raise ValueError('unexpected minute value between 1 and 60: ' + str(minute))
            second = int(time_string[17:19])
            if not (0 <= second <= 61):  # leap seconds
                raise ValueError('unexpected second value between 1 and 61: ' + str(second))
            timetuple = (year, month, day, hour, minute, second, -1, -1, 0)
            self._time_seconds = calendar.timegm(timetuple)
            self._tz_offset = self._tzdtoseconds(time_string[19:])
            self._tz_str()  # to get assertions there
        except (TypeError, ValueError, AssertionError):
            raise ValueError(time_string)

    def epoch(self):
        return self._time_seconds - self._tz_offset

    def _tz_str(self):
        if self._tz_offset:
            hours, minutes = divmod(abs(self._tz_offset) // 60, 60)
            assert 0 <= hours <= 23
            assert 0 <= minutes <= 59
            if self._tz_offset > 0:
                plus_minus = "+"
            else:
                plus_minus = "-"
            return "%s%s:%s" % (plus_minus, "%02d" % hours, "%02d" % minutes)
        else:
            return "Z"

    def set_time(self, hour, minute, second):
        year = time.gmtime(self._time_seconds)[0]
        month = time.gmtime(self._time_seconds)[1]
        day = time.gmtime(self._time_seconds)[2]
        _time_seconds = calendar.timegm((year, month, day, hour, minute, second, -1, -1, 0))
        return RdiffTime(_time_seconds, self._tz_offset)

    def _tzdtoseconds(self, tzd):
        """Given w3 compliant TZD, converts it to number of seconds from UTC"""
        if tzd == "Z":
            return 0
        assert len(tzd) == 6  # only accept forms like +08:00 or +08-00 for now
        assert (tzd[0] == "-" or tzd[0] == "+") and tzd[3] in [":", '-']
        if tzd[0] == "+":
            plus_minus = 1
        else:
            plus_minus = -1
        return plus_minus * 60 * (60 * int(tzd[1:3]) + int(tzd[4:]))

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

    def __eq__(self, other):
        return isinstance(other, RdiffTime) and self.epoch() == other.epoch()

    def __hash__(self):
        return hash(self.epoch())

    def __str__(self):
        """return utf-8 string"""
        value = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(self._time_seconds))
        return value + self._tz_str()

    def __repr__(self):
        """return second since epoch"""
        return "RdiffTime('" + str(self) + "')"


class RdiffDirEntry(object):
    """
    Includes name, isdir, file_size, exists, and dict (change_dates) of sorted
    local dates when backed up.
    """

    def __init__(self, repo, path, exists, increments):
        assert isinstance(repo, RdiffRepo)
        assert isinstance(path, bytes)
        # Keep reference to the path and repo object.
        self._repo = repo
        self.path = path
        # Absolute path to the directory
        if self.isroot:
            self.full_path = self._repo.full_path
        else:
            self.full_path = os.path.join(self._repo.full_path, self.path)
        # May need to compute our own state if not provided.
        self.exists = exists
        # Store the increments sorted by date.
        # See self.last_change_date()
        self._increments = sorted(increments, key=lambda x: x.date)

    @property
    def display_name(self):
        """Return the most human readable filename. Without quote."""
        return self._repo.get_display_name(self.path)

    @property
    def isroot(self):
        """
        Check if the directory entry represent the root of the repository.
        Return True when path is empty.
        """
        return self.path == b''

    @cached_property
    def isdir(self):
        """Lazy check if entry is a directory"""
        if self.exists:
            # If the entry exists, check if it's a directory
            return os.path.isdir(self.full_path)
        # Check if increments is a directory
        for increment in self._increments:
            if increment.is_missing:
                # Ignore missing increment...
                continue
            return increment.isdir

    @cached_property
    def file_size(self):
        """
        Return the current file size in bytes.
        Return negative value (-1) for folder and deleted files.
        """
        if self.isdir or not self.exists:
            return -1
        else:
            try:
                return os.lstat(self.full_path).st_size
            except Exception:
                logger.warning("cannot lstat on file [%s]", self.full_path, exc_info=1)
                return 0

    def get_file_size(self, date=None):
        # A viable place to get the filesize of a deleted entry
        # it to get it from file_statistics
        try:
            stats = self._repo.file_statistics[date]
            # File stats uses unquoted name.
            unquote_path = unquote(self.path)
            return stats.get_source_size(unquote_path)
        except Exception:
            logger.warning("cannot find file statistic [%s]", self.last_change_date, exc_info=1)
        return -1

    @cached_property
    def change_dates(self):
        """
        Return a list of dates when this item has changes. Represent the
        previous revision. From old to new.
        """
        # Exception for root path, use backups dates.
        if self.isroot:
            return self._repo.backup_dates

        # Compute the dates
        change_dates = set()
        for increment in self._increments:
            # Get date of the increment as reference
            change_date = increment.date
            # If the increment is a "missing" increment, need to get the date
            # before the folder was removed.
            if increment.is_missing:
                change_date = self._get_previous_backup_date(change_date)

            if change_date:
                change_dates.add(change_date)

        # If the directory exists, add the last known backup date.
        if self.exists and self._repo.last_backup_date:
            change_dates.add(self._repo.last_backup_date)

        # Return the list of dates.
        return sorted(change_dates)

    def _get_previous_backup_date(self, date):
        """Return the previous backup date."""
        index = bisect.bisect_left(self._repo.backup_dates, date)
        if index == 0:
            return None
        return self._repo.backup_dates[index - 1]

    @cached_property
    def last_change_date(self):
        """Return last change date or False."""
        return self.change_dates and self.change_dates[-1]


class AbstractEntry:
    SUFFIXES = None

    @classmethod
    def _extract_date(cls, filename, onerror=None):
        """
        Extract date from rdiff-backup filenames.
        """
        # Extract suffix
        suffix = None
        for s in cls.SUFFIXES:
            if filename.endswith(s):
                suffix = s
                break
        if not suffix:
            raise ValueError(filename)
        # Parse date
        filename_without_suffix = filename[: -len(suffix)]
        parts = filename_without_suffix.rsplit(b'.', 1)
        if len(parts) != 2:
            return onerror(ValueError(''))
        date_string = unquote(parts[1]).decode('ascii')
        try:
            return RdiffTime(date_string)
        except Exception as e:
            if onerror is None:
                raise
            return onerror(e)


class MetadataEntry(AbstractEntry):
    PREFIX = None
    SUFFIXES = None
    on_date_error = None

    def __init__(self, repo, name):
        assert isinstance(repo, RdiffRepo)
        assert isinstance(name, bytes)
        assert name.startswith(self.PREFIX)
        assert any(name.endswith(s) for s in self.SUFFIXES), 'name %s should ends with: %s' % (name, self.SUFFIXES)
        self.repo = repo
        self.name = name
        self.path = os.path.join(self.repo._data_path, self.name)
        self.date = self._extract_date(name, onerror=self.on_date_error)

    def _open(self):
        """
        Should be used to open the increment file. This method handle
        compressed vs not-compressed file.
        """
        if self._is_compressed:
            return popen(['zcat', self.path])
        return open(self.path, 'rb')

    @property
    def _is_compressed(self):
        return self.name.endswith(b".gz")


class MirrorMetadataEntry(MetadataEntry):
    PREFIX = b'mirror_metadata.'
    SUFFIXES = [
        b'.diff',
        b'.diff.gz',
        b".snapshot.gz",
        b".snapshot",
    ]


class IncrementEntry(AbstractEntry):

    """Instance of the class represent one increment at a specific date for one
    repository. The base repository is provided in the default constructor
    and the date is provided using an error_log.* file"""

    SUFFIXES = [
        b".missing",
        b".snapshot.gz",
        b".snapshot",
        b".diff",
        b".diff.gz",
        b".dir",
    ]

    def __init__(self, name):
        """Default constructor for an increment entry. User must provide the
        repository directory and an entry name. The entry name correspond
        to an error_log.* filename."""
        self.name, self.date, self.suffix = IncrementEntry._split(name)

    @property
    def isdir(self):
        return self.suffix == b".dir"

    @property
    def is_missing(self):
        """Check if the curent entry is a missing increment."""
        return self.suffix == b".missing"

    @property
    def is_snapshot(self):
        """Check if the current entry is a snapshot increment."""
        return self.suffix in [b".snapshot.gz", b".snapshot"]

    @classmethod
    def _split(cls, filename):
        """Return tuple with filename, date, suffix"""
        assert isinstance(filename, bytes)
        # Extract suffix
        suffix = None
        for s in cls.SUFFIXES:
            if filename.endswith(s):
                suffix = s
                break
        if not suffix:
            raise ValueError(filename)
        # Parse date and raise error on failure
        filename_without_suffix = filename[: -len(suffix)]
        name, date_string = filename_without_suffix.rsplit(b'.', 1)
        date_string = unquote(date_string).decode('ascii')
        date = RdiffTime(date_string)
        return (name, date, suffix)

    def __gt__(self, other):
        return self.date.__gt__(other.date)

    def __lt__(self, other):
        return self.date.__lt__(other.date)


class FileStatisticsEntry(MetadataEntry):

    """
    Represent a single file_statistics.

    File Statistics contains different information related to each file of
    the backup. This class provide a simple and easy way to access this
    data.
    """

    PREFIX = b'file_statistics.'
    SUFFIXES = [b'.data', b'.data.gz']

    def get_mirror_size(self, path):
        """Return the value of MirrorSize for the given file.
        path is the relative path from repo root."""
        try:
            return int(self._search(path)["mirror_size"])
        except ValueError:
            logger.warning("mirror size not found for [%r]", path, exc_info=1)
            return 0

    def get_source_size(self, path):
        """Return the value of SourceSize for the given file.
        path is the relative path from repo root."""
        try:
            return int(self._search(path)["source_size"])
        except ValueError:
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

        with self._open() as f:
            for line in f:
                if not line.startswith(path):
                    continue
                break

        # Split the line into array
        data = line.rstrip(b'\r\n').rsplit(b' ', 4)
        # From array create an entry
        return {'changed': data[1], 'source_size': data[2], 'mirror_size': data[3], 'increment_size': data[4]}


class SessionStatisticsEntry(MetadataEntry):
    """Represent a single session_statistics."""

    PREFIX = b'session_statistics.'
    SUFFIXES = [b'.data', b'.data.gz']

    ATTRS = [
        'starttime',
        'endtime',
        'elapsedtime',
        'sourcefiles',
        'sourcefilesize',
        'mirrorfiles',
        'mirrorfilesize',
        'newfiles',
        'newfilesize',
        'deletedfiles',
        'deletedfilesize',
        'changedfiles',
        'changedsourcesize',
        'changedmirrorsize',
        'incrementfiles',
        'incrementfilesize',
        'totaldestinationsizechange',
        'errors',
    ]

    def _load(self):
        """This method is used to read the session_statistics and create the
        appropriate structure to quickly get the data.

        File Statistics contains different information related to each file of
        the backup. This class provide a simple and easy way to access this
        data."""

        with self._open() as f:
            for line in f.readlines():
                # Read the line into array
                line = line.rstrip(b'\r\n')
                data_line = line.split(b" ", 2)
                # Read line into tuple
                (key, value) = tuple(data_line)[0:2]
                if b'.' in value:
                    value = float(value)
                else:
                    value = int(value)
                setattr(self, key.lower().decode('ascii'), value)

    def __getattr__(self, name):
        """
        Intercept attribute getter to load the file.
        """
        if name in self.ATTRS:
            self._load()
        return self.__dict__[name]


class CurrentMirrorEntry(MetadataEntry):
    PID_RE = re.compile(b"^PID\\s*([0-9]+)", re.I | re.M)

    PREFIX = b'current_mirror.'
    SUFFIXES = [b'.data']

    def extract_pid(self):
        """
        Return process ID from a current mirror marker, if any
        """
        with open(self.path, 'rb') as f:
            match = self.PID_RE.search(f.read())
        if not match:
            return None
        return int(match.group(1))


class LogEntry(MetadataEntry):
    PREFIX = b'error_log.'
    SUFFIXES = [b'.data', b'.data.gz']

    @cached_property
    def is_empty(self):
        """
        Check if the increment entry is empty.
        """
        return os.path.getsize(self.path) == 0

    def read(self):
        """Read the error file and return it's content. Raise exception if the
        file can't be read."""
        # To avoid opening empty file, check the file size first.
        if self.is_empty:
            return ""
        encoding = self.repo._encoding.name
        if self._is_compressed:
            return subprocess.check_output(
                ['zcat', self.path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                encoding=encoding,
                errors='replace',
            )
        with open(self.path, 'r', encoding=encoding, errors='replace') as f:
            return f.read()

    def tail(self, num=2000):
        """
        Tail content of the file. This is used for logs.
        """
        # To avoid opening empty file, check the file size first.
        if self.is_empty:
            return b''
        encoding = self.repo._encoding.name
        if self._is_compressed:
            zcat = subprocess.Popen([b'zcat', self.path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            return subprocess.check_output(
                ['tail', '-n', str(num)],
                stdin=zcat.stdout,
                stderr=subprocess.STDOUT,
                encoding=encoding,
                errors='replace',
            )
        return subprocess.check_output(
            ['tail', '-n', str(num), self.path], stderr=subprocess.STDOUT, encoding=encoding, errors='replace'
        )


class RestoreLogEntry(LogEntry):
    PREFIX = b'restore.'
    SUFFIXES = [b'.log']

    @staticmethod
    def on_date_error(e):
        return None


class BackupLogEntry(LogEntry):
    PREFIX = b'backup.'
    SUFFIXES = [b'.log']

    @staticmethod
    def on_date_error(e):
        return None


class MetadataKeys:
    """
    Provide a view on metadata dict keys. See MetadataDict#keys()
    """

    def __init__(self, function, sequence):
        self._f = function
        self._sequence = sequence

    def __iter__(self):
        return map(self._f, self._sequence)

    def __getitem__(self, i):
        if isinstance(i, slice):
            return list(map(self._f, self._sequence[i]))
        else:
            return self._f(self._sequence[i])

    def __len__(self):
        return len(self._sequence)


class MetadataDict(object):
    """
    This is used to access repository metadata quickly in a pythonic way. It
    make an abstraction to access a range of increment entries using index and
    date while also supporting slice to get a range of entries.
    """

    def __init__(self, repo, cls):
        assert isinstance(repo, RdiffRepo)
        assert hasattr(cls, '__call__')
        self._repo = repo
        assert cls.PREFIX
        self._prefix = cls.PREFIX
        self._cls = cls

    @cached_property
    def _entries(self):
        return [e for e in self._repo._entries if e.startswith(self._prefix)]

    def __getitem__(self, key):
        if isinstance(key, RdiffTime):
            idx = bisect.bisect_left(self.keys(), key)
            if idx < len(self._entries):
                item = self._cls(self._repo, self._entries[idx])
                if item.date == key:
                    return item
            raise KeyError(key)
        elif isinstance(key, slice):
            if isinstance(key.start, RdiffTime):
                idx = bisect.bisect_left(self.keys(), key.start)
                key = slice(idx, key.stop, key.step)
            if isinstance(key.stop, RdiffTime):
                idx = bisect.bisect_right(self.keys(), key.stop)
                key = slice(key.start, idx, key.step)
            return [self._cls(self._repo, e) for e in self._entries[key]]
        elif isinstance(key, int):
            try:
                return self._cls(self._repo, self._entries[key])
            except IndexError:
                raise KeyError(key)
        else:
            raise KeyError(key)

    def __iter__(self):
        for e in self._entries:
            yield self._cls(self._repo, e)

    def __len__(self):
        return len(self._entries)

    def keys(self):
        return MetadataKeys(lambda e: self._cls._extract_date(e), self._entries)


class RdiffRepo(object):

    """Represent one rdiff-backup repository."""

    def __init__(self, full_path, encoding):
        assert encoding, 'encoding is required'
        self._encoding = encodings.search_function(encoding)
        assert self._encoding, 'encoding must be a valid charset'

        # Validate and sanitize the full_path
        assert full_path, 'full path is required'
        self.full_path = os.fsencode(full_path) if isinstance(full_path, str) else full_path
        assert os.path.isabs(self.full_path), 'full_path must be absolute path'
        self.full_path = os.path.normpath(self.full_path)

        # The location of rdiff-backup-data directory.
        self._data_path = os.path.join(self.full_path, RDIFF_BACKUP_DATA)
        assert isinstance(self._data_path, bytes)
        self._increment_path = os.path.join(self._data_path, INCREMENTS)
        self.current_mirror = MetadataDict(self, CurrentMirrorEntry)
        self.error_log = MetadataDict(self, LogEntry)
        self.mirror_metadata = MetadataDict(self, MirrorMetadataEntry)
        self.file_statistics = MetadataDict(self, FileStatisticsEntry)
        self.session_statistics = MetadataDict(self, SessionStatisticsEntry)

    @property
    def backup_dates(self):
        """Return a list of dates when backup was executed. This list is
        sorted from old to new (ascending order). To identify dates,
        'mirror_metadata' file located in rdiff-backup-data are used."""
        return self.mirror_metadata.keys()

    @property
    def backup_log(self):
        """
        Return the location of the backup log.
        """
        return BackupLogEntry(self, b'backup.log')

    def delete(self, path):
        """
        Delete this entry from the repository history using rdiff-backup-delete.
        """
        path_obj = self.fstat(path)
        if path_obj.isroot:
            return self.delete_repo()

        rdiff_backup_delete = find_rdiff_backup_delete()
        cmdline = [rdiff_backup_delete, path_obj.full_path]
        logger.info('executing: %r' % cmdline)
        process = subprocess.Popen(cmdline, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env={'LANG': LANG})
        for line in process.stdout:
            line = line.rstrip(b'\n').decode('utf-8', errors='replace')
            logger.info('rdiff-backup-delete: %s' % line)
        retcode = process.wait()
        if retcode:
            raise CalledProcessError(retcode, cmdline)

    def delete_repo(self):
        """Delete the repository permanently."""
        # Try to change the permissions of the file or directory to delete
        # them.
        def handle_error(func, path, exc_info):
            if exc_info[0] == PermissionError:
                # Parent directory must allow rwx
                if not os.access(os.path.dirname(path), os.W_OK | os.R_OK | os.X_OK):
                    os.chmod(os.path.dirname(path), 0o0700)
                if not os.access(path, os.W_OK | os.R_OK):
                    os.chmod(path, 0o0600)
                if os.path.isdir(path):
                    return shutil.rmtree(path, onerror=handle_error)
                else:
                    return os.unlink(path)
            raise

        try:
            shutil.rmtree(self.full_path, onerror=handle_error)
        except Exception:
            logger.warning('fail to delete repo', exc_info=1)

    @property
    def display_name(self):
        """Return the most human representation of the repository name."""
        return self.get_display_name(b'')

    def _decode(self, value, errors='replace'):
        """Used to decode a repository path into unicode."""
        assert isinstance(value, bytes)
        return self._encoding.decode(value, errors)[0]

    @cached_property
    def _entries(self):
        return sorted(os.listdir(self._data_path))

    def expire(self):
        """
        Clear the cache to refresh metadata.
        """
        cached_properties = [
            (self, '_entries'),
            (self, 'status'),
            (self.current_mirror, '_entries'),
            (self.error_log, '_entries'),
            (self.mirror_metadata, '_entries'),
            (self.file_statistics, '_entries'),
            (self.session_statistics, '_entries'),
        ]
        for obj, attr in cached_properties:
            if attr in obj.__dict__:
                del obj.__dict__[attr]

    def listdir(self, path):
        """
        Return a list of RdiffDirEntry each representing a file or a folder in the given path.
        """
        # Compute increment directory location.
        full_path = os.path.realpath(os.path.join(self.full_path, path.strip(b'/')))
        relative_path = os.path.relpath(full_path, self.full_path)
        if relative_path.startswith(RDIFF_BACKUP_DATA):
            raise DoesNotExistError(path)
        increment_path = os.path.normpath(os.path.join(self._increment_path, relative_path))
        if not full_path.startswith(self.full_path) or not increment_path.startswith(self.full_path):
            raise AccessDeniedError('%s make reference outside the repository' % self._decode(path))

        # Get list of all increments and existing file and folder
        try:
            existing_items = os.listdir(full_path)
            if relative_path == b'.':
                existing_items.remove(RDIFF_BACKUP_DATA)
        except (NotADirectoryError, FileNotFoundError):
            existing_items = None
        except OSError:
            raise AccessDeniedError(path)
        try:
            increment_items = os.listdir(increment_path)
        except (NotADirectoryError, FileNotFoundError):
            increment_items = None
        except OSError:
            raise AccessDeniedError(path)
        # Raise error if nothing is found
        if existing_items is None and increment_items is None:
            raise DoesNotExistError(path)

        # Merge information from both location
        # Regroup all information into RdiffDirEntry
        entries = {}
        for name in existing_items or []:
            entries[name] = RdiffDirEntry(
                self,
                os.path.normpath(os.path.join(relative_path, name)),
                exists=True,
                increments=[],
            )
        for item in increment_items or []:
            try:
                increment = IncrementEntry(item)
            except ValueError:
                # Ignore any increment that cannot be parsed
                continue
            entry = entries.get(increment.name, None)
            if not entry:
                # Create a new Direntry
                entry = entries[increment.name] = RdiffDirEntry(
                    self,
                    os.path.normpath(os.path.join(relative_path, increment.name)),
                    exists=False,
                    increments=[increment] if increment else [],
                )
            else:
                # Add increment to dir entry
                bisect.insort_left(entry._increments, increment)
        return sorted(list(entries.values()), key=lambda e: e.path)

    def fstat(self, path):
        """Return a new instance of DirEntry to represent the given path."""
        # Compute increment directory location.
        assert isinstance(path, bytes)
        full_path = os.path.normpath(os.path.join(self.full_path, path.strip(b'/')))
        increment_path = os.path.normpath(os.path.join(self._increment_path, path.strip(b'/'), b'..'))
        if not full_path.startswith(self.full_path) or not increment_path.startswith(self.full_path):
            raise AccessDeniedError('%s make reference outside the repository' % self._decode(path))
        relative_path = os.path.relpath(full_path, self.full_path)
        if relative_path.startswith(RDIFF_BACKUP_DATA):
            raise DoesNotExistError(path)
        # Get if the path request is the root path.
        if relative_path == b'.':
            return RdiffDirEntry(self, b'', True, [])

        # Check if path exists
        try:
            os.lstat(full_path)
            exists = True
        except (OSError, ValueError):
            exists = False

        # Get incrmement data
        increment_items = os.listdir(increment_path)

        # Create dir entry
        prefix = os.path.basename(full_path)
        entry = RdiffDirEntry(self, relative_path, exists, [])
        for item in increment_items:
            if not item.startswith(prefix):
                # Ignore increment not matching our path
                continue
            try:
                increment = IncrementEntry(item)
            except ValueError:
                # Ignore any increment that cannot be parsed
                continue
            if increment.name != prefix:
                # Ignore increment not matching our path
                continue
            # Add increment to dir entry
            bisect.insort_left(entry._increments, increment)

        # Check if path exists or has increment. If not raise an exception.
        if not exists and not entry._increments:
            logger.error("path [%r] doesn't exists", path)
            raise DoesNotExistError(path)

        # Create a directory entry.
        return entry

    @property
    def last_backup_date(self):
        """Return the last known backup dates."""
        try:
            if len(self.current_mirror) > 0:
                return self.current_mirror[-1].date
            return None
        except (PermissionError, FileNotFoundError):
            return None

    def get_display_name(self, path):
        """
        Return proper display name of the given path according to repository encoding and quoted characters.
        """
        assert isinstance(path, bytes)
        path = path.strip(b'/')
        if path in [b'.', b'']:
            # For repository the directory base name
            return self._decode(unquote(os.path.basename(self.full_path)))
        else:
            # For path, we use the dir name
            return self._decode(unquote(os.path.basename(path)))

    def remove_older(self, remove_older_than):
        assert type(remove_older_than) is int, 'invalid remove_older_than, expect an integer: ' + remove_older_than
        logger.info(
            "execute rdiff-backup --force --remove-older-than=%sD %r",
            remove_older_than,
            self.full_path.decode(sys.getfilesystemencoding(), 'replace'),
        )
        subprocess.check_output(
            [
                b'rdiff-backup',
                b'--force',
                b'--remove-older-than=' + str(remove_older_than).encode(encoding='latin1') + b'D',
                self.full_path,
            ]
        )
        self.expire()

    def restore(self, path, restore_as_of, kind=None):
        """
        Restore the current directory entry into a fileobj containing the
        file content of the directory compressed into an archive.

        `kind` must be one of the supported archive type or none to use `zip` for folder and `raw` for file.

        Return a filename and a fileobj.
        """
        assert isinstance(path, bytes)
        assert restore_as_of, "restore_as_of must be defined"
        assert kind in ['tar', 'tar.bz2', 'tar.gz', 'tbz2', 'tgz', 'zip', 'raw', None]

        # Define proper kind according to path type.
        path_obj = self.fstat(path)
        if path_obj.isdir:
            if kind == 'raw':
                raise ValueError('raw type not supported for directory')
            kind = kind or 'zip'
        else:
            kind = kind or 'raw'

        # Define proper filename according to the path
        if kind == 'raw':
            filename = path_obj.display_name
        else:
            filename = "%s.%s" % (path_obj.display_name, kind)

        # Call external process to offload processing.
        # python -m rdiffweb.core.restore --restore-as-of 123456 --encoding utf-8 --kind zip -
        cmdline = [
            os.fsencode(sys.executable),
            b'-m',
            b'rdiffweb.core.restore',
            b'--restore-as-of',
            str(restore_as_of).encode('latin'),
            b'--encoding',
            self._encoding.name.encode('latin'),
            b'--kind',
            kind.encode('latin'),
            os.path.join(self.full_path, unquote(path_obj.path)),
            b'-',
        ]
        proc = subprocess.Popen(
            cmdline,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=None,
        )
        # Check if the restore process is properly starting
        # Read the first 100 line until "Processing changed file"
        max_line = 100
        output = b''
        success = False
        line = proc.stderr.readline()
        while max_line > 0 and line:
            max_line -= 1
            output += line
            if b'Processing changed file' in line:
                success = True
                break
            line = proc.stderr.readline()
        if not success:
            raise CalledProcessError(1, cmdline, output)
        # Start a Thread to pipe the rest of the stream to the log
        t = threading.Thread(target=_readerthread, args=(proc.stderr, logger.debug))
        t.daemon = True
        t.start()
        return filename, _wrap_close(proc.stdout, proc)

    @property
    def restore_log(self):
        """
        Return the location of the restore log.
        """
        return RestoreLogEntry(self, b'restore.log')

    @cached_property
    def status(self):
        """Check if a backup is in progress for the current repo."""

        # Read content of the file and check if pid still exists
        try:
            # Make sure repoRoot is a valid rdiff-backup repository
            for current_mirror in self.current_mirror:
                pid = current_mirror.extract_pid()
                try:
                    p = psutil.Process(pid)
                    if any('rdiff-backup' in c for c in p.cmdline()):
                        return ('in_progress', _('A backup is currently in progress to this repository.'))
                except psutil.NoSuchProcess:
                    logger.debug('pid [%s] does not exists', pid)

            # If multiple current_mirror file exists and none of them are associated to a PID, this mean the last backup was interrupted.
            # Also, if the last backup date is undefined, this mean the first
            # initial backup was interrupted.
            if len(self.current_mirror) > 1 or len(self.current_mirror) == 0:
                return ('interrupted', _('The previous backup seams to have failed.'))
        except FileNotFoundError:
            self._entries = []
            return ('failed', _('The repository cannot be found or is badly damaged.'))
        except PermissionError:
            self._entries = []
            logger.warning('error reading current_mirror files', exc_info=1)
            return ('failed', _("Permissions denied. Contact administrator to check repository's permissions."))

        return ('ok', '')
