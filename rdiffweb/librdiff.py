#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
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

import bisect
import gzip
import logging
import os
import re
import subprocess
import tempfile

import rdw_helpers

from i18n import ugettext as _

# Define the logger
logger = logging.getLogger(__name__)

# Constant for the rdiff-backup-data folder name.
RDIFF_BACKUP_DATA = b"rdiff-backup-data"

# Constant for the increments folder name.
INCREMENTS = os.path.join(RDIFF_BACKUP_DATA, b"increments")

# Zip file extension
ZIP_SUFFIX = b".zip"

# Tar gz extension
TARGZ_SUFFIX = b".tar.gz"


class FileError:

    def __str__(self):
        return rdw_helpers.encode_s(unicode(self))

    def __unicode__(self):
        return _("An unknown error occurred.")


class AccessDeniedError(FileError):

    def __unicode__(self):
        return _("Access denied.")


class DoesNotExistError(FileError):

    def __unicode__(self):
        return _("The repository does not exist.")


class UnknownError(FileError):

    def __init__(self, error=None):
        if not error:
            error = _("An unknown error occurred.")
        assert isinstance(error, unicode)
        self.error = error

    def __unicode__(self):
        return self.error


# Interfaced objects #

class DirEntry:

    """Includes name, isDir, fileSize, exists, and dict (changeDates) of sorted
    local dates when backed up"""

    def __init__(self, repo_path, name, exists, increments):
        assert isinstance(repo_path, RdiffPath)
        assert isinstance(name, str)

        # Keep reference to the path and repo object.
        self._repo = repo_path.repo
        # Keep reference to this entry name.
        self.name = name
        # Relative path to the directory entry
        self.path = os.path.join(
            repo_path.path,
            name)
        # Absolute path to the directory
        self.full_path = os.path.join(
            self._repo.repo_root,
            repo_path.path,
            name)
        self.exists = exists
        self._increments = increments

    @property
    def display_name(self):
        """Return the most human readable filename. Without quote."""
        value = self._repo.unquote(self.name)
        return self._repo._decode(value)

    @property
    def isdir(self):
        """Lazy check if entry is a directory"""
        if not hasattr(self, '_isdir'):
            if self.exists:
                # If the entry exists, check if it's a directory
                self._isdir = os.path.isdir(self.full_path)
            else:
                # Check if increments is a directory
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
        if not hasattr(self, '_file_size'):
            self._file_size = 0
            if self.exists:
                self._file_size = os.lstat(self.full_path)[6]
            else:
                # The only viable place to get the filesize of a deleted entry
                # it to get it from file_statistics
                stats = self._repo.get_file_statistic(self.last_change_date)
                if stats:
                    # File stats uses unquoted name.
                    unquote_path = self._repo.unquote(self.path)
                    self._file_size = stats.get_source_size(unquote_path)

        return self._file_size

    @property
    def change_dates(self):
        """Return a list of dates when this item has changes. Represent the
        previous revision. From old to new."""
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

            if change_date not in self._change_dates:
                self._change_dates.append(change_date)

        # If the directory exists, add the last known backup date.
        if (self.exists
                and self._repo.last_backup_date not in self._change_dates):
            self._change_dates.append(self._repo.last_backup_date)

        # Sort the dates
        self._change_dates = sorted(self._change_dates)

        # Return the list of dates.
        return self._change_dates

    def _get_first_backup_after_date(self, date):
        """ Iterates the mirror_metadata files in the rdiff data dir """
        index = bisect.bisect_right(self._repo.backup_dates, date)
        return self._repo.backup_dates[index]

    @property
    def last_change_date(self):
        return self.change_dates[-1]


class HistoryEntry:

    def __init__(self, repo, date):
        assert isinstance(repo, RdiffRepo)
        assert isinstance(date, rdw_helpers.rdwTime)
        self._repo = repo
        self.date = date

    @property
    def size(self):
        try:
            return (self._repo._session_statistics[self.date]
                    .get_source_file_size())
        except KeyError:
            return 0

    @property
    def errors(self):
        """Return error messages."""
        try:
            self._repo._error_logs[self.date].read()
        except KeyError:
            return ""

    @property
    def increment_size(self):
        try:
            return (self._repo._session_statistics[self.date]
                    .get_increment_file_size())
        except KeyError:
            return 0


class IncrementEntry(object):

    """Instance of the class represent one increment at a specific date for one
    repository. The base repository is provided in the default constructor
    and the date is provided using an error_log.* file"""

    MISSING_SUFFIX = b".missing"

    SUFFIXES = [b".missing", b".snapshot.gz", b".snapshot",
                b".diff.gz", b".data.gz", b".data", b".dir", b".diff"]

    def __init__(self, repo_path, name):
        """Default constructor for an increment entry. User must provide the
            repository directory and an entry name. The entry name correspond
            to an error_log.* filename."""
        assert isinstance(repo_path, RdiffPath)
        assert isinstance(name, str)
        # Keep reference to the current path.
        self.repo_path = repo_path
        # Get reference to the repository location.
        self.repo = repo_path.repo
        # The given entry name may has quote charater, replace them
        self.name = name

    @property
    def date(self):
        # Remove suffix from filename
        filename = self._remove_suffix(self.name)
        # Remove prefix from filename
        date_string = filename.rsplit(b".", 1)[-1]
        return_time = rdw_helpers.rdwTime()
        try:
            return_time.initFromString(date_string)
            return return_time
        except ValueError:
            return None

    def _open(self):
        """Should be used to open the increment file. This method handle
        compressed vs not-compressed file."""
        if self._is_compressed:
            return gzip.open(os.path.join(self.repo.data_path, self.name), "r")
        return open(os.path.join(self.repo.data_path, self.name), "r")

    def read(self):
        """Read the error file and return it's content. Raise exception if the
        file can't be read."""
        return self._open().read()

    @property
    def filename(self):
        filename = self._remove_suffix(self.name)
        return filename.rsplit(b".", 1)[0]

    @property
    def has_suffix(self):
        for suffix in self.SUFFIXES:
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
        return (self.name.endswith(b".snapshot.gz")
                or self.name.endswith(b".snapshot"))

    def _remove_suffix(self, filename):
        """ returns None if there was no suffix to remove. """
        for suffix in self.SUFFIXES:
            if filename.endswith(suffix):
                return filename[:-len(suffix)]
        return filename

    def __str__(self):
        return self.name


class FileStatisticsEntry(IncrementEntry):

    """Represent a single file_statistics."""

    def __init__(self, repo_path, name):
        IncrementEntry.__init__(self, repo_path, name)
        # check to ensure we have a file_statistics entry
        assert self.name.startswith(b"file_statistics.")
        assert self.name.endswith(b".data") or self.name.endswith(b".data.gz")

    def _load(self):
        """This method is used to read the file_statistics and create the
        appropriate structure to quickly search it.

        File Statistics contains different information related to each file of
        the backup. This class provide a simple and easy way to access this
        data."""

        if hasattr(self, '_data'):
            return

        logger.debug("load file_statistics [%s]" %
                     self.repo._decode(self.name))
        self._data = {}
        with self._open() as f:
            for line in f:
                # Skip comments
                if line.startswith(b"#"):
                    continue
                # Read the line into array
                line = line.rstrip(b'\r\n')
                data_line = line.rsplit(b" ", 4)
                # Read line into tuple
                (filename, changed, source_size,
                 mirror_size, increment_size) = tuple(data_line)
                # From tuple create an entry
                self._data[filename] = {
                    "changed": changed,
                    "source_size": source_size,
                    "mirror_size": mirror_size,
                    "increment_size": increment_size}

    def get_mirror_size(self, path):
        """Return the value of MirrorSize for the given file.
        path is the relative path from repo root."""
        self._load()
        try:
            return self._data[path]["mirror_size"]
        except KeyError:
            logger.warn("mirror size not found for [%s]" %
                        self.repo._decode(path))
            return 0

    def get_source_size(self, path):
        """Return the value of SourceSize for the given file.
        path is the relative path from repo root."""
        self._load()
        try:
            return self._data[path]["source_size"]
        except KeyError:
            logger.warn("source size not found for [%s]" %
                        self.repo._decode(path))
            return 0


class SessionStatisticsEntry(IncrementEntry):

    """Represent a single session_statistics."""

    def __init__(self, repo_path, name):
        IncrementEntry.__init__(self, repo_path, name)
        # check to ensure we have a file_statistics entry
        assert self.name.startswith(b"session_statistics")
        assert self.name.endswith(b".data") or self.name.endswith(b".data.gz")

    def _load(self):
        """This method is used to read the session_statistics and create the
        appropriate structure to quickly get the data.

        File Statistics contains different information related to each file of
        the backup. This class provide a simple and easy way to access this
        data."""

        if hasattr(self, '_data'):
            return

        logger.debug("load session_statistics [%s]" %
                     self.repo._decode(self.name))
        self._data = {}
        with self._open() as f:
            for line in f:
                # Skip comments
                if line.startswith(b"#"):
                    continue
                # Read the line into array
                line = line.rstrip(b'\r\n')
                data_line = line.split(b" ", 2)
                # Read line into tuple
                (key, value) = tuple(data_line)[0:2]
                self._data[key] = value

    def get_increment_file_size(self):
        """Return the IncrementFileSize from this entry"""
        self._load()
        try:
            return int(self._data[b"IncrementFileSize"])
        except KeyError:
            return 0

    def get_source_file_size(self):
        """Return the SourceFileSize from this entry"""
        self._load()
        try:
            return int(self._data[b"SourceFileSize"])
        except KeyError:
            return 0


class RdiffRepo:

    """Represent one rdiff-backup repository."""

    def __init__(self, user_root, path):
        assert isinstance(user_root, str)
        assert isinstance(path, str)
        self.encoding = 'utf-8'
        self.user_root = user_root.rstrip(b"/")
        self.path = path.strip(b"/")
        self.repo_root = os.path.join(self.user_root, self.path)
        self.root_path = RdiffPath(self)

        # The location of rdiff-backup-data directory.
        self.data_path = os.path.join(self.repo_root, RDIFF_BACKUP_DATA)
        assert isinstance(self.data_path, str)

        # Check if the object is valid.
        self._check()

        # Check if the repository has hint for rdiffweb.
        self._load_hints()

    @property
    def backup_dates(self):
        """Return a list of dates when backup was executed. This list is
        sorted from old to new (ascending order). To identify dates,
        'mirror_metadata' file located in rdiff-backup-data are used."""
        if not hasattr(self, '_backup_dates'):
            logger.debug("get backup dates for [%s]" %
                         self._decode(self.repo_root))
            self._backup_dates = [
                IncrementEntry(self.root_path, x).date
                for x in filter(lambda x: x.startswith(b"mirror_metadata"),
                                self.data_entries)]
            self._backup_dates = sorted(self._backup_dates)
        return self._backup_dates

    def _check(self):
        """Check if the repository exists."""
        # Make sure repoRoot is a valid rdiff-backup repository
        if (not os.access(self.data_path, os.F_OK)
                or not os.path.isdir(self.data_path)):
            logger.error("repository [%s] doesn't exists" %
                         self._decode(self.repo_root))
            raise DoesNotExistError()

    @property
    def data_entries(self):
        """Return list of folder and file located directly in
        rdiff-backup-data folder. Each file represent a data entry."""

        # Get entries from increment data.
        return os.listdir(self.data_path)

    @property
    def display_name(self):
        """Return the most human representation of the repository name."""
        # NOTE : path may be empty, so return a simpel string.
        if not self.path:
            name_b = os.path.basename(self.user_root)
            return self._decode(name_b)
        return self._decode(self.path)

    def _decode(self, value):
        """Used to decode a repository path into unicode."""
        assert isinstance(value, str)
        return value.decode(self.encoding, 'replace')

    @property
    def _error_logs(self):
        """Return list of IncrementEntry to represent each file statistics."""
        if not hasattr(self, '_error_logs_data'):
            self._error_logs_data = {}
            for x in filter(lambda x: x.startswith(b"error_log."),
                            self.data_entries):
                entry = IncrementEntry(self.root_path, x)
                self._error_logs_data[entry.date] = entry
        return self._error_logs_data

    @property
    def _file_statistics(self):
        """Return list of IncrementEntry to represent each file statistics."""
        if not hasattr(self, '_file_statistics_data'):
            self._file_statistics_data = {}
            for x in filter(lambda x: x.startswith(b"file_statistics."),
                            self.data_entries):
                entry = FileStatisticsEntry(self.root_path, x)
                self._file_statistics_data[entry.date] = entry
        return self._file_statistics_data

    def get_file_statistic(self, date):
        """Return the file statistic for the given date.
        Try to search for the given file statistic and return an object to
        represent it."""
        # Get reference to the FileStatisticsEntry
        try:
            return self._file_statistics[date]
        except KeyError:
            return None

    def get_history_entries(self,
                            numLatestEntries=-1,
                            earliestDate=None,
                            latestDate=None):
        """Returns a list of HistoryEntry's
        earliestDate and latestDate are inclusive."""

        assert isinstance(numLatestEntries, int)
        assert (earliestDate is None
                or isinstance(earliestDate, rdw_helpers.rdwTime))
        assert (latestDate is None
                or isinstance(latestDate, rdw_helpers.rdwTime))

        logger.debug("get history entries for [%s]" %
                     self._decode(self.repo_root))

        entries = []
        for backup_date in self.backup_dates:
            # compare local times because of discrepency between client/server
            # time zones
            if earliestDate and backup_date < earliestDate:
                continue

            if latestDate and backup_date > latestDate:
                continue

            entries.append(HistoryEntry(self, backup_date))

            if numLatestEntries != -1 and len(entries) == numLatestEntries:
                return entries

        return entries

    def get_path(self, path):
        """Return a new instance of RdiffPath to represent the given path."""
        assert isinstance(path, str)
        # Get if the path request is the root path.
        if len(path.strip(b"/")) == 0:
            return self.root_path
        return RdiffPath(self, path)

    @property
    def in_progress(self):
        """Check if a backup is in progress for the current repo."""
        # Filter the files to keep current_mirror.* files
        mirrorMarkers = filter(lambda x: x.startswith(b"current_mirror."),
                               self.data_entries)
        return len(mirrorMarkers) > 1

    @property
    def last_backup_date(self):
        """Return the last known backup dates."""

        if len(self.backup_dates) > 0:
            return self.backup_dates[-1]
        return None

    def _load_hints(self):
        """For different purpose, a repository may contains an "rdiffweb" file
        to provide hint to rdiffweb related to locale. At first, it's used to
        define an encoding."""

        hint_file = os.path.join(self.data_path, b"rdiffweb")
        if not os.access(hint_file, os.F_OK) or os.path.isdir(hint_file):
            return

        logger.debug("reading hints for [%s]" % self._decode(self.repo_root))
        with open(hint_file, "r") as f:
            for line in f:
                line = line.rstrip(b"\r\n")
                parts = line.partition(b'=')
                if not len(parts) == 3:
                    logger.warn("invalid hints [%s]" % self._decode(line))
                    continue
                # Sets the encoding name (if valid)
                if b"encoding" == parts[0]:
                    try:
                        b"".encode(parts[2])
                        self.encoding = parts[2]
                    except LookupError:
                        logger.warn("wrong encoding name [%s]" %
                                    self._decode(parts[2]))

    @property
    def _session_statistics(self):
        """Return list of IncrementEntry to represent each sessions
        statistics."""
        if not hasattr(self, '_session_statistics_data'):
            self._session_statistics_data = {}
            for x in filter(lambda x: x.startswith(b"session_statistics."),
                            self.data_entries):
                entry = SessionStatisticsEntry(self.root_path, x)
                self._session_statistics_data[entry.date] = entry
        return self._session_statistics_data

    def unquote(self, name):
        """Remove quote from the given name."""
        assert isinstance(name, str)

        # This function just gives back the original text if it can decode it
        def unquoted_char(match):
            if not len(match.group()) == 4:
                return match.group
            try:
                return chr(int(match.group()[1:]))
            except ValueError:
                return match.group
        # Remove quote using regex
        return re.sub(b";[0-9]{3}", unquoted_char, name, re.S)


class RdiffPath:

    """Represent an rdiff-backup repository. Either a root, a path or a file."""

    def __init__(self, repo, path=b""):
        assert isinstance(repo, RdiffRepo)
        assert isinstance(path, str)
        self.repo = repo
        self.path = path.strip(b"/")

        # Check if the object is valid
        self._check()

    def _check(self):
        """Check if the path is valid within the a repository."""

        # Make sure it'S not a subdirectory of "rdiff-backup-data"
        if self.path.startswith(RDIFF_BACKUP_DATA):
            raise AccessDeniedError()

        # Make sure there are no symlinks in the path
        path_to_check = os.path.join(self.repo_root, self.path)
        while True:
            path_to_check = path_to_check.rstrip(b"/")
            if os.path.islink(path_to_check):
                raise AccessDeniedError()

            (path_to_check, filename) = os.path.split(path_to_check)
            if not filename:
                break

        # Make sure that the folder/file exists somewhere - either in the
        # current folder, or in the incrementsDir
        if not os.access(os.path.join(self.repo_root, self.path), os.F_OK):
            (parent_folder, filename) = os.path.split(
                os.path.join(self.repo_root, INCREMENTS, self.path))
            try:
                increments = os.listdir(parent_folder)
            except OSError:
                logger.exception("fail to list increments for [%s]" %
                                 self._decode(parent_folder))
                increments = []

            increments = filter(lambda x: x.startswith(filename), increments)
            if not increments:
                logger.error("repository [%s] doesn't exists" %
                             self._decode(self.path))
                raise DoesNotExistError()

    def _decode(self, value):
        """Used to decode a repostior ypath into unicode."""
        return self.repo._decode(value)

    @property
    def dir_entries(self):
        """Get directory entries for the current path. It is similar to
        listdir() but for rdiff-backup."""

        logger.debug("get directory entries for [%s]" %
                     self._decode(self.full_path))

        # Group increments by filename
        grouped_increment_entries = rdw_helpers.groupby(
            self._increment_entries, lambda x: x.filename)

        # Process each increment entries and combine this with the existing
        # entries
        entriesDict = {}
        for filename, increments in grouped_increment_entries.iteritems():
            # Check if filename exists
            exists = filename in self.existing_entries
            # Create DirEntry to represent the item
            new_entry = DirEntry(
                self,
                filename,
                exists,
                increments)
            entriesDict[filename] = new_entry

        # Then add existing entries
        for filename in self.existing_entries:
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
        return entriesDict.values()

    def _execute(self, command, *args):
        parms = [command]
        parms.extend(args)
        execution = subprocess.Popen(
            parms, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        results = {}
        results['exitCode'] = execution.wait()
        (results['stdout'], results['stderr']) = execution.communicate()
        return results

    @property
    def existing_entries(self):
        """Return the content of the directory using a simple listdir(). This
        represent the last known backup. Thus it return existing entries."""

        if not hasattr(self, '_existing_entries'):
            logger.debug("get existing entries for [%s]" %
                         self._decode(self.full_path))

            # Check if the directory exists. It may not exist if
            # it has been delete
            self._existing_entries = []
            if os.access(self.full_path, os.F_OK):
                # Get entries from directory structure
                self._existing_entries = os.listdir(self.full_path)

                # Remove "rdiff-backup-data" directory
                if self.path == "":
                    self._existing_entries.remove(RDIFF_BACKUP_DATA)

        return self._existing_entries

    @property
    def increments_path(self):
        """Get the increment path for the current path. This path is located
            under rdiff-backup-data/increments"""

        if not hasattr(self, '_increments_path'):
            self._increments_path = os.path.join(
                self.repo.repo_root,
                INCREMENTS,
                self.path)
        return self._increments_path

    @property
    def full_path(self):
        """return the canonical path to the current path. Basically,
            return absolute path"""
        return os.path.join(self.repo_root, self.path)

    @property
    def _increment_entries(self):
        """Return all the increment entries for this path.
            each entry represent a 'file' in the subdirectory structure under
            rdiff-backup-data/increments"""

        if not hasattr(self, '_increment_entries_data'):
            logger.debug(
                "get increments entries for [%s]" %
                self._decode(self.increments_path))

            # Check if increment directory exists. The path may not exists if
            # the folder always exists and never changed.
            self._increment_entries_data = []
            if os.access(self.increments_path, os.F_OK):
                # List content of the increment directory.
                # Ignore sub-directories.
                self._increment_entries_data = [
                    IncrementEntry(self, y) for y in filter(
                        lambda x: not os.path.isdir(
                            os.path.join(self.increments_path, x)),
                        os.listdir(self.increments_path))]

        return self._increment_entries_data

    @property
    def repo_root(self):
        """return the repository path"""
        return self.repo.repo_root

    def restore(self, name, restore_date, use_zip):
        """Used to restore the given file located in this path."""
        assert isinstance(name, str)
        assert isinstance(restore_date, rdw_helpers.rdwTime)
        name = name.lstrip(b"/")

        # Determine the file name to be restore (from rdiff-backup
        # point of view).
        file_to_restore = os.path.join(self.full_path, name)
        file_to_restore = self.repo.unquote(file_to_restore)

        # Convert the date into epoch.
        date_epoch = str(restore_date.getSeconds())

        # Define a location where to restore the data
        if name == b"" and self.path == b"":
            filename = b"root"
        if self.path != b"":
            filename = os.path.basename(self.path)
        if name != b"":
            filename = name
        # Generate a temporary location used to restore data.
        output = os.path.join(tempfile.mkdtemp(), filename)

        # Execute rdiff-backup to restore the data.
        logger.info(
            "execute rdiff-backup --restore-as-of=%s '%s' '%s'" % (
                date_epoch,
                rdw_helpers.decode_s(file_to_restore, 'replace'),
                rdw_helpers.decode_s(output, 'replace'),
                ))
        results = self._execute(
            b"rdiff-backup",
            b"--restore-as-of=" + date_epoch,
            file_to_restore,
            output)

        # Check the result
        if results['exitCode'] != 0 or not os.access(output, os.F_OK):
            error = results['stderr']
            if not error:
                error = '''rdiff-backup claimed success, but did not restore
                        anything. This indicates a bug in rdiffweb. Please
                        report this to a developer.'''
            raise UnknownError('unable to restore!\n' + error)

        # The path restored is a directory and need to be archived using zip
        # or tar
        if os.path.isdir(output):
            output_dir = output
            try:
                if use_zip:
                    output = output_dir + ZIP_SUFFIX
                    self._recursiveZipDir(output_dir, output)
                else:
                    output = output_dir + TARGZ_SUFFIX
                    self._recursiveTarDir(output_dir, output)
            finally:
                rdw_helpers.remove_dir(output_dir)

        # Return the location of the file to be restored
        return output

    @property
    def restore_dates(self):

        """Get list of date to be restored for current path. From old to
        new."""

        logger.debug("get restore dates for [%s]" %
                     self._decode(self.full_path))

        # If root directory return all dates.
        if self.path == b"":
            return self.repo.backup_dates

        # Get reference to parent path
        (parent_path, name) = os.path.split(self.path)
        repo_path = RdiffPath(self.repo, parent_path)

        # Get entries specific to the given name
        entries = repo_path.dir_entries
        entries = filter(lambda x: x.name == name, entries)
        if not entries:
            raise DoesNotExistError()
        entry = entries[0]

        # Retrieve all backup dates.
        backup_dates = self.repo.backup_dates

        # Don't allow restores before the dir existed
        backup_dates = filter(
            lambda x: x >= entry.change_dates[0], backup_dates)

        if not entry.exists:
            # If the dir has been deleted, don't allow restores after its
            # deletion
            backup_dates = filter(
                lambda x: x <= entry.change_dates[-1], backup_dates)

        return backup_dates

    def _recursiveTarDir(self, dirPath, tarFilename):
        """This function is used during to archive a restored directory. It will
            create a tar gz archive with the specified directory."""
        assert isinstance(dirPath, str)
        assert isinstance(tarFilename, str)
        assert os.path.isdir(dirPath)
        import tarfile

        dirPath = os.path.normpath(dirPath)

        # Create a tar.gz archive
        logger.info("creating a tar file [%s] from [%s]",
                    self._decode(tarFilename), self._decode(dirPath))
        tar = tarfile.open(tarFilename, "w:gz")

        # List content of the directory.
        files = os.listdir(dirPath)

        # Add files to the archive
        for filename in files:
            # Pass in file as name explicitly so we get relative paths
            tar.add(os.path.join(dirPath, filename), filename)

        # Close the archive
        tar.close()

    def _recursiveZipDir(self, dirPath, zipFilename):
        """This function is used during to archive a restored directory. It will
            create a zip archive with the specified directory."""
        assert isinstance(dirPath, str)
        assert isinstance(zipFilename, str)
        assert os.path.isdir(dirPath)
        import zipfile

        dirPath = os.path.normpath(dirPath)

        # Create the archive
        zipObj = zipfile.ZipFile(zipFilename, "w", zipfile.ZIP_DEFLATED)

        # Add files to archive
        for root, dirs, files in os.walk(dirPath, topdown=True):
            for name in files:
                fullPath = os.path.join(root, name)
                assert fullPath.startswith(dirPath)
                relPath = fullPath[len(dirPath) + 1:]
                zipObj.write(fullPath, relPath)

        zipObj.close()
