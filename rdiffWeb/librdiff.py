#!/usr/bin/python
# rdiffWeb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffWeb contributors
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

"""All functions throw on error."""

import os
import bisect
import gzip
import re
from rdw_helpers import joinPaths, removeDir
import rdw_helpers
import logging
import tempfile

RDIFF_BACKUP_DATA = "rdiff-backup-data"
# Constant for the rdiff-backup-data folder name.

INCREMENTS = joinPaths(RDIFF_BACKUP_DATA, "increments")
# Constant for the increments folder name.

ZIP_SUFFIX = ".zip"
# Zip file extension

TARGZ_SUFFIX = ".tar.gz"
# Tar gz extension

class FileError:
   def getErrorString(self):
      return self.error
   def __str__(self):
      return self.getErrorString()

class AccessDeniedError(FileError):
   def __init__(self):
      self.error = "Access is denied."

class DoesNotExistError(FileError):
   def __init__(self):
      self.error = "The backup location does not exist."

class UnknownError(FileError):
   def __init__(self, error=None):
      self.error = error
      if not self.error:
         self.error = "An unknown error occurred."

##### Helper Functions #####
def rsplit(string, sep, count=-1):
    L = [part[::-1] for part in string[::-1].split(sep[::-1], count)]
    L.reverse()
    return L

##### Interfaced objects #####
class DirEntry:
   """Includes name, isDir, fileSize, exists, and dict (changeDates) of sorted local dates when backed up"""
   def __init__(self, name, quoter, isDir, fileSize, exists, changeDates):
      self.name = quoter.getUnquotedPath(name)
      self.isDir = isDir
      self.fileSize = fileSize
      self.exists = exists
      self.changeDates = changeDates

class BackupHistoryEntry:
   def __init__(self):
      self.date = None
      self.size = None
      self.errors = None
      self.incrementSize = None
      self.inProgress = None
   pass

class BackupHistoryEntries:
   """Instance of this class represent a collection of backup entry for a
      single repository. Roughtly their is one entry for each
      'current_mirror.*' files."""
      
   def __init__(self, repoRoot):
      checkRepoPath(repoRoot, "")
      self.repoRoot = repoRoot
      
      # List all the files within the rdiff-backup-data
      self.dirEntries = os.listdir(os.path.join(repoRoot, RDIFF_BACKUP_DATA))
      self.dirEntries.sort()

   def getBackupHistory(self, numLatestEntries=-1, earliestDate=None, latestDate=None, includeInProgress=True):
      """Returns a list of backupHistoryEntry's
         earliestDate and latestDate are inclusive."""
   
      # Get a listing of error log files, and use that to build backup history
      curEntries = filter(lambda x: x.startswith("error_log."), self.dirEntries)
      curEntries.reverse()
   
      entries = []
      for entryFile in curEntries:
         entry = IncrementEntry(self.repoRoot, entryFile)
         # compare local times because of discrepency between client/server time zones
         if earliestDate and entry.getDate().getLocalSeconds() < earliestDate.getLocalSeconds():
            continue
   
         if latestDate and entry.getDate().getLocalSeconds() > latestDate.getLocalSeconds():
            continue
   
         try:
            errors = entry.getErrors()
         except IOError:
            logging.exception("Can't retrieved errors.")
            errors = "[Unable to read errors file.]"
         try:
            fileSize = entry.getSourceFileSize()
            incrementSize = entry.getIncrementFileSize()
         except IOError:
            logging.exception("Can't get session stats.")
            fileSize = 0
            incrementSize = 0
         
         # Create the backup history entry using data from the increment entry
         newEntry = BackupHistoryEntry()
         newEntry.date = entry.getDate()
         newEntry.inProgress = self._backupIsInProgress(entry.getDate())
         if not includeInProgress and newEntry.inProgress:
            continue
   
         if newEntry.inProgress:
            newEntry.errors = ""
         else:
            newEntry.errors = errors
         newEntry.size = int(fileSize) if fileSize else 0
         newEntry.incrementSize = int(incrementSize) if incrementSize else 0
         entries.insert(0, newEntry)
         
         if numLatestEntries != -1 and len(entries) == numLatestEntries:
            return entries
   
      return entries

   def _backupIsInProgress(self, date):
      # Filter the files to keep current_mirror.* files
      mirrorMarkers = filter(lambda x: x.startswith("current_mirror."), self.dirEntries)
      if not mirrorMarkers:
         return True
      for marker in mirrorMarkers[1:]:
         if IncrementEntry(self.repoRoot, marker).getDate().getSeconds() == date.getSeconds():
            return True
      return False

class IncrementEntry:
   """Instance of the class represent one increment at a specific date for one
      repository. The base repository is provided in the default constructor
      and the date is provided using an error_log.* file"""
   
   MISSING_SUFFIX = ".missing"
   
   SUFFIXES = [".missing", ".snapshot.gz", ".snapshot", ".diff.gz", ".data.gz", ".data", ".dir", ".diff"];

   def __init__(self, repoRoot, entryName):
      """Default constructor for an increment entry. User must provide the
         repository directory and an entry name. The entry name correspond to
         an error_log.* filename."""
      # Keep reference to the repository location
      self.repoRoot = repoRoot
      
      # The given entry name may has quote charater, replace them
      self.entryName = RdiffQuotedPath(repoRoot).getQuotedPath(entryName)
      
   def getDate(self):
      timeString = self.getDateString()
      returnTime = rdw_helpers.rdwTime()
      try:
         returnTime.initFromString(timeString)
         return returnTime
      except ValueError:
         return None

   def getDateString(self):
      filename = self._removeSuffix(self.entryName)
      return rsplit(filename, ".", 1)[1]

   def getDateStringNoTZ(self, tzOffset=0):
      filename = self._removeSuffix(self.entryName)
      incrDate = self.getDate()
      if not incrDate:
         print "Warning: unintelligible date string! Filename:", self.entryName, " Filetitle:", filename, " Date String:", self.getDateString()
         return ""  # avoid crashing on invalid date strings

      incrDate.timeInSeconds += tzOffset
      return incrDate.getUrlStringNoTZ()

   def getErrors(self):
      """Read the error file and return it's content. Raise exception if the
         file can't be read."""
         
      if self.isCompressed():
         return gzip.open(os.path.join(self.repoRoot, RDIFF_BACKUP_DATA, self.entryName), "r").read()
      
      return open(os.path.join(self.repoRoot, RDIFF_BACKUP_DATA, self.entryName), "r").read()

   def getFilename(self):
      filename = self._removeSuffix(self.entryName)
      return rsplit(filename, ".", 1)[0]

   def getIncrementFileSize(self):
      """This function return the value of the IncrementFileSize define in the
         session_statistics.* file for the current increment or None if the
         file can't be found."""
      
      stats = self._getSessionStatistics()
      if not stats:
         return None
          
      return re.compile("IncrementFileSize ([0-9]+) ").findall(stats)[0]

   def _getSessionStatsFile(self):
      """Return the filepath of the sessions statistics file for a given backup
         entry. This function search for file 'session_statistics.*'"""
      # Get the date of the current entry
      entryDate = self.getDate()

      # List all the session_statistics file foir the current repository
      statFiles = filter(lambda x: x.startswith("session_statistics."), os.listdir(os.path.join(self.repoRoot, RDIFF_BACKUP_DATA)))
      
      # For each file, check if the date matches.
      for file in statFiles:
          time = self._parseDate(file)
          if time == entryDate:
              return os.path.join(self.repoRoot, RDIFF_BACKUP_DATA, file)
          
      # Can't find the file
      return None

   def _getSessionStatistics(self):
      """Return the content of the session_statistics.* file for the current
         increment."""
      if hasattr(self, "statistics"):
         return self.statistics
      
      filename = self._getSessionStatsFile()
      if not filename:
         self.statistics = None
         return None
      
      self.statistics = open(filename, 'r').read()
      return self.statistics

   def getSize(self):
      return 0  # TODO: use gzip to figure out increment size for snapshot increments


   def getSourceFileSize(self):
      """This function return the value of the SourceFileSize define in the
         session_statistics.* file for the current increment or None if the
         file can't be found."""
      
      stats = self._getSessionStatistics()
      if not stats:
         return None
          
      return re.compile("SourceFileSize ([0-9]+) ").findall(stats)[0]

   def hasIncrementSuffix(self, filename):
      for suffix in self.SUFFIXES:
         if filename.endswith(suffix):
            return True
      return False
 
   def isCompressed(self):
      return self.entryName.endswith(".gz")

   def isMissingIncrement(self):
      return self.entryName.endswith(self.MISSING_SUFFIX)

   def isSnapshotIncrement(self):
      return self.entryName.endswith(".snapshot.gz") or self.entryName.endswith(".snapshot")

   def shouldShowIncrement(self):
      return self.hasIncrementSuffix(self.entryName) and not self.isMissingIncrement()

   def _parseDate(self, filename):
      """Return a date object from a filename."""
      # Parse the date of the file
      filename = self._removeSuffix(filename)
      filename = rsplit(filename, ".", 1)[1]
      time = rdw_helpers.rdwTime()
      try:
         time.initFromString(filename)
         return time
      except ValueError:
         return None

   def _removeSuffix(self, filename):
      """ returns None if there was no suffix to remove. """
      for suffix in self.SUFFIXES:
         if filename.endswith(suffix):
            return filename[:-len(suffix)]
      return filename

class RdiffQuotedPath:
   """This class may be used to convert quoted file name. Ridff-backup may
      convert special charater using the following pattern ;000. This is used
      to ensure compatibility between filesystem."""
   def __init__(self, repoRoot):
      self.unquoteRegex = re.compile(";[0-9]{3}", re.S)
      
      charsToQuotePath = joinPaths(repoRoot, RDIFF_BACKUP_DATA, "chars_to_quote")
      if os.path.exists(charsToQuotePath):
         charsToQuoteStr = open(charsToQuotePath).read()
         if charsToQuoteStr:
            self.quoteRegex = re.compile("[^/%s]|;" % charsToQuoteStr, re.S)
      
   def getUnquotedPath(self, quotedPath):
      return self.unquoteRegex.sub(self.getUnquotedChar, quotedPath)
   
   def getQuotedPath(self, unQuotedPath):
      if not hasattr(self, "quoteRegex"): return unQuotedPath
      return self.quoteRegex.sub(self.getQuotedChar, unQuotedPath)
   
   # This function just gives back the original text if it can decode it
   def getUnquotedChar(self, match):
      if not len(match.group()) == 4:
         return match.group
      try:
         return chr(int(match.group()[1:]))
      except ValueError:
         return match.group
   
   def getQuotedChar(self, match):
      return ";%03d" % (ord(match.group()))

class RdiffDirEntries:
   """This class is responsible for building a listing of directory entries.
      All knowledge of how increments work is contained in this class."""
      
   # dirPath must be quoted!
   def __init__(self, repo, dirPath):
      # Var assignment and validation
      self.pathQuoter = RdiffQuotedPath(repo)
      
      self.repo = repo
      self.dirPath = dirPath
      self.completePath = joinPaths(repo, dirPath)
      dataPath = joinPaths(repo, RDIFF_BACKUP_DATA)

      # cache dir listings
      self.entries = []
      if os.access(self.completePath, os.F_OK):
         self.entries = os.listdir(self.completePath)  # the directory may not exist if it has been deleted
      self.dataDirEntries = os.listdir(dataPath)
      incrementsDir = joinPaths(repo, INCREMENTS, dirPath)
      self.incrementEntries = []
      if os.access(incrementsDir, os.F_OK):  # the increments may not exist if the folder has existed forever and never been changed
         self.incrementEntries = filter(lambda x: not os.path.isdir(joinPaths(incrementsDir, x)), os.listdir(incrementsDir))  # ignore directories

      self.groupedIncrementEntries = rdw_helpers.groupby(self.incrementEntries, lambda x: IncrementEntry(repo, x).getFilename())
      self.backupTimes = [ IncrementEntry(repo, x).getDate() for x in filter(lambda x: x.startswith("mirror_metadata"), self.dataDirEntries) ]
      self.backupTimes.sort()

   def getDirEntries(self):
      """ returns dictionary of dir entries, keyed by dir name """
      entriesDict = {}

      # First, we grab a dir listing of the target, setting entry attributes
      for entryName in self.entries:
         if entryName == RDIFF_BACKUP_DATA: continue
         entryPath = joinPaths(self.repo, self.dirPath, entryName)
         newEntry = DirEntry(entryName, self.pathQuoter, os.path.isdir(entryPath), os.lstat(entryPath)[6], True,
                             [self._getLastChangedBackupTime(entryName)])
         entriesDict[newEntry.name] = newEntry

      # Go through the increments dir.  If we find any files that didn't exist in dirPath (i.e. have been deleted), add them
      for entryFile in self.incrementEntries:
         entry = IncrementEntry(self.repo, entryFile)
         entryName = entry.getFilename()
         if entry.shouldShowIncrement() or entry.isMissingIncrement():
            entryDate = entry.getDate()
            if not entry.isSnapshotIncrement():
               if entry.isMissingIncrement():
                  entryDate = self._getFirstBackupAfterDate(entry.getDate())
               else:
                  entryDate = entry.getDate()
            if not entryName in entriesDict.keys():
               entryPath = joinPaths(self.repo, INCREMENTS, self.dirPath, entryName)
               newEntry = DirEntry(entryName, self.pathQuoter, os.path.isdir(entryPath), 0, False, [entryDate])
               entriesDict[entryName] = newEntry
            else:
               if not entryDate in entriesDict[entryName].changeDates:
                  bisect.insort_left(entriesDict[entryName].changeDates, entryDate)

      return entriesDict

   def _getFirstBackupAfterDate(self, date):
      """ Iterates the mirror_metadata files in the rdiff data dir """
      if not date:
         return self.backupTimes[0]
      return self.backupTimes[bisect.bisect_right(self.backupTimes, date)]

   def _getLastChangedBackupTime(self, filename):
      files = self.groupedIncrementEntries.get(filename, [])
      if os.path.isdir(joinPaths(self.completePath, filename)):
         files = filter(lambda x: x.endswith(".dir") or x.endswith(".missing"), files)
      files.sort()
      if not files:
         return self._getFirstBackupAfterDate(None)
      return self._getFirstBackupAfterDate(IncrementEntry(self.repo, files[-1]).getDate())


def checkRepoPath(repoRoot, filePath):
   """Check if the file path specified is valid within the a repository."""
   
   # Make sure repoRoot is a valid rdiff-backup repository
   dataPath = joinPaths(repoRoot, RDIFF_BACKUP_DATA)
   if not os.access(dataPath, os.F_OK) or not os.path.isdir(dataPath):
      raise DoesNotExistError()

   # Make sure there are no symlinks in the path
   pathToCheck = joinPaths(repoRoot, filePath)
   while True:
      pathToCheck = pathToCheck.rstrip("/")
      if os.path.islink(pathToCheck):
         raise AccessDeniedError()

      (pathToCheck, file) = os.path.split(pathToCheck)
      if not file:
         break

   # Make sure that the folder/file exists somewhere - either in the current folder, or in the incrementsDir
   if not os.access(joinPaths(repoRoot, filePath), os.F_OK):
      (parentFolder, filename) = os.path.split(joinPaths(repoRoot, INCREMENTS, filePath))
      try:
         increments = os.listdir(parentFolder)
      except OSError:
         increments = []
      increments = filter(lambda x: x.startswith(filename), increments)
      if not increments:
         raise DoesNotExistError()


##### Interfaced Functions #####
def getDirEntries(repoRoot, dirPath):
   """Returns list of rdiffDirEntry objects for the directory path specified within a repository."""
   dirPath = RdiffQuotedPath(repoRoot).getQuotedPath(dirPath)
   checkRepoPath(repoRoot, dirPath)

   entryLister = RdiffDirEntries(repoRoot, dirPath)
   entries = entryLister.getDirEntries()
   entriesList = entries.values()

   def sortDirEntries(entry1, entry2):
      if entry1.isDir and not entry2.isDir: return -1
      if not entry1.isDir and entry2.isDir: return 1
      return cmp(entry1.name.upper(), entry2.name.upper())
   entriesList.sort(sortDirEntries)
   return entriesList

def restoreFileOrDir(repoRoot, dirPath, filename, restoreDate, useZip):
   """This function is used to restore a directory tree or a file from the
      given respository. Users may specified the restore date and the
      archive format."""
   
   # Format the specified file name / repository path for validation
   dirPath = dirPath.encode('utf-8')
   filename = filename.encode('utf-8')
   filePath = joinPaths(dirPath, filename)
   filePath = RdiffQuotedPath(repoRoot).getQuotedPath(filePath)
   checkRepoPath(repoRoot, filePath)

   restoredFilename = filename
   if restoredFilename == "/":
      restoredFilename = "(root)"

   fileToRestore = joinPaths(repoRoot, dirPath, filename)
   dateString = str(restoreDate.getSeconds())
   rdiffOutputFile = joinPaths(tempfile.mkdtemp(), restoredFilename)  # TODO: make so this includes the username
   
   # Use rdiff-backup executable to restore the data into a specified location
   results = rdw_helpers.execute("rdiff-backup", "--restore-as-of=" + dateString, fileToRestore, rdiffOutputFile)
   
   # Check the result
   if results['exitCode'] != 0 or not os.access(rdiffOutputFile, os.F_OK):
      error = results['stderr']
      if not error:
         error = 'rdiff-backup claimed success, but did not restore anything. This indicates a bug in rdiffWeb. Please report this to a developer.'
      raise UnknownError('Unable to restore! rdiff-backup output:\n' + error)

   
   # The path restored is a directory and need to be archived using zip or tar
   if os.path.isdir(rdiffOutputFile):
      rdiffOutputDirectory = rdiffOutputFile
      try:
         if useZip:
            rdiffOutputFile = rdiffOutputFile + ZIP_SUFFIX
            _recursiveZipDir(rdiffOutputDirectory, rdiffOutputFile)
         else:
            rdiffOutputFile = rdiffOutputFile + TARGZ_SUFFIX
            _recursiveTarDir(rdiffOutputDirectory, rdiffOutputFile)
      finally:
         rdw_helpers.removeDir(rdiffOutputDirectory)
         
   return rdiffOutputFile

def backupIsInProgressForRepo(repo):
   rdiffDir = joinPaths(repo, RDIFF_BACKUP_DATA)
   mirrorMarkers = os.listdir(rdiffDir)
   mirrorMarkers = filter(lambda x: x.startswith("current_mirror."), mirrorMarkers)
   return not mirrorMarkers or len(mirrorMarkers) > 1

def getBackupHistory(repoRoot):
   """Return a list of BackupHistoryEntry for the respository specified."""
   historyEntries = BackupHistoryEntries(repoRoot)
   return historyEntries.getBackupHistory()

def getLastBackupHistoryEntry(repoRoot, includeInProgress=True):
   """Return the most recent instance of BackupHistoryEntry for the repository
      specified."""
   historyEntries = BackupHistoryEntries(repoRoot)
   history = historyEntries.getBackupHistory(1, None, None, includeInProgress)
   if not history:
      # We may not have any backup entries if the first backup
      # for the repository is in progress
      raise FileError
   return history[0]

def getBackupHistoryForDay(repoRoot, date):
   historyEntries = BackupHistoryEntries(repoRoot)
   return historyEntries.getBackupHistory(-1, date)

def getBackupHistorySinceDate(repoRoot, date):
   historyEntries = BackupHistoryEntries(repoRoot)
   return historyEntries.getBackupHistory(-1, date)

def getBackupHistoryForDateRange(repoRoot, earliestDate, latestDate):
   historyEntries = BackupHistoryEntries(repoRoot)
   return historyEntries.getBackupHistory(-1, earliestDate, latestDate, False)

def getDirRestoreDates(repo, path):
   backupHistory = [ x.date for x in getBackupHistory(repo) ]

   if path != "/":
      (parentPath, dirName) = os.path.split(path)
      dirListing = getDirEntries(repo, parentPath)
      entries = filter(lambda x: x.name == dirName, dirListing)
      if not entries:
         raise DoesNotExistError
      entry = entries[0]

      # Don't allow restores before the dir existed
      backupHistory = filter(lambda x: x >= entry.changeDates[0], backupHistory)

      if not entry.exists:
         # If the dir has been deleted, don't allow restores after its deletion
         backupHistory = filter(lambda x: x <= entry.changeDates[-1], backupHistory)

   return backupHistory


def _recursiveTarDir(dirPath, tarFilename):
   """This function is used during to archive a restored directory. It will
      create a tar gz archive with the specified directory."""
   dirPath = dirPath.encode('utf-8')
   tarFilename = tarFilename.encode('utf-8')
   assert os.path.isdir(dirPath)
   import tarfile

   dirPath = os.path.normpath(dirPath)
   
   # Create a tar.gz archive
   tar = tarfile.open(tarFilename, "w:gz")
   files = os.listdir(dirPath)
   
   # Add files to the archive
   for file in files:
      tar.add(joinPaths(dirPath, file), file)  # Pass in file as name explicitly so we get relative paths
   
   # Close the archive 
   tar.close()
   
def _recursiveZipDir(dirPath, zipFilename):
   """This function is used during to archive a restored directory. It will
      create a zip archive with the specified directory."""
   dirPath = dirPath.encode('utf-8')
   assert os.path.isdir(dirPath)
   import zipfile

   dirPath = os.path.normpath(dirPath)

   # Create the archive
   zipObj = zipfile.ZipFile(zipFilename, "w", zipfile.ZIP_DEFLATED)
   
   # Add files to archive
   for root, dirs, files in os.walk(dirPath, topdown=True):
      for name in files:
         fullPath = joinPaths(root, name)
         assert fullPath.startswith(dirPath)
         relPath = fullPath[len(dirPath) + 1:]
         zipObj.write(fullPath, relPath)

   zipObj.close()

##################### Unit Tests #########################

def runRdiff(src, dest, time):
   # Force a null TZ for backups, to keep rdiff-backup from mangling the times
   environ = os.environ;
   environ['TZ'] = ""
   os.spawnlp(os.P_WAIT, "rdiff-backup", "rdiff-backup", "--no-compare-inode", "--current-time=" + str(time.getSeconds()), src, dest)

def getMatchingDirEntry(entries, filename):
#    for entry in entries:
#       print entry.name
   matchingEntries = filter(lambda x: x.name == filename, entries)
   assert len(matchingEntries) == 1, entries
   return matchingEntries[0]

import unittest, time
class LibRdiffTest(unittest.TestCase):
   # The dirs containing source data for automated tests are set up in the following format:
   # one folder for each test, named to describe the test
      # one folder for each state in the backup, named using the rdiff-backup time format (e.g. "2006-01-04T01:49:50Z")
         # folder contents at given state.  Subdirs are not really handled

   # The setUp function is responsible for backing up data for each backup test case and test case state, rooted at self.destRoot

   def setUp(self):
      # The temp dir on Mac OS X is a symlink; expand it because of validation against symlinks in paths
      self.destRoot = joinPaths(os.path.realpath(tempfile.gettempdir()), "rdiffWeb")
      self.masterDirPath = joinPaths("..", "tests")  # TODO: do this right, including tying tests into "python setup.py test"
      self.tearDown()

      os.makedirs(self.destRoot)

      # Set up each scenario
      tests = self.getBackupTests()
      for testDir in tests:
         # Iterate through the backup states
         origStateDir = joinPaths(self.masterDirPath, testDir)
         backupStates = self.getBackupStates(origStateDir)
         backupStates.sort(lambda x, y: cmp(x, y))
         for backupState in backupStates:
            # Try to parse the folder name as a date.  If we can't, raise
            backupTime = rdw_helpers.rdwTime()
            backupTime.initFromString(backupState)

            # Backup the data as it should be at that state
            # print "   State", backupState
            runRdiff(joinPaths(origStateDir, backupState), joinPaths(self.destRoot, testDir), backupTime)

   def tearDown(self):
      if (os.access(self.destRoot, os.F_OK)):
         removeDir(self.destRoot)

   def getBackupTests(self):
      return filter(lambda x: not x.startswith("."), os.listdir(self.masterDirPath))

   def getBackupStates(self, backupTestDir):
      return filter(lambda x: not x.startswith(".") and x != "results", os.listdir(backupTestDir))
   
   def hasDirEntriesResults(self, testname):
      return os.access(joinPaths(self.masterDirPath, testname, "results", "dir_entries.txt"), os.F_OK)
   
   def hasDirRestoreDates(self, testname):
      return os.access(joinPaths(self.masterDirPath, testname, "results", "dir_restore_dates.txt"), os.F_OK)
   
   def getExpectedDirRestoreDates(self, testName):
      return open(joinPaths(self.masterDirPath, testName, "results", "dir_restore_dates.txt")).read()

   def getExpectedDirEntriesResults(self, testName):
      return open(joinPaths(self.masterDirPath, testName, "results", "dir_entries.txt")).read()

   ################  Start actual tests ###################
   def testGetDirEntries(self):
      tests = self.getBackupTests()
      for testDir in tests:
         if self.hasDirEntriesResults(testDir):
            # Get a list of backup entries for the root folder
            rdiffDestDir = joinPaths(self.destRoot, testDir)
            entries = getDirEntries(rdiffDestDir, "/")
   
            statusText = ""
            for entry in entries:
               if entry.name != ".svn":
                  for changeDate in entry.changeDates:
                     size = entry.fileSize
                     if entry.isDir: size = 0
                     statusText = statusText + entry.name + "\t" + str(entry.isDir) + "\t" + str(size) + "\t" + str(entry.exists) + "\t" + changeDate.getUrlString() + "\n"
               
            assert statusText.replace("\n", "") == self.getExpectedDirEntriesResults(testDir).replace("\n", ""), "Got: " + statusText + "\nExpected:" + self.getExpectedDirEntriesResults(testDir)

   def testGetDirRestoreDates(self):
      tests = self.getBackupTests()
      for testDir in tests:
         if self.hasDirRestoreDates(testDir):
            rdiffDestDir = joinPaths(self.destRoot, testDir)
            
            # print rdiffDestDir
            dates = getDirRestoreDates(rdiffDestDir, "/testdir2")
            statusText = ""
            for date in dates:
               statusText = statusText + date.getUrlString() + "\n"
            
            assert statusText.replace("\n", "") == self.getExpectedDirRestoreDates(testDir).replace("\n", ""), "Got: " + statusText + "\nExpected:" + self.getExpectedDirRestoreDates(testDir)

   def testGetBackupHistory(self):
      tests = self.getBackupTests()
      for testDir in tests:
         # Get a list of backup entries for the root folder
         origBackupDir = joinPaths(self.masterDirPath, testDir)
         backupStates = self.getBackupStates(origBackupDir)
         backupStates.sort(lambda x, y: cmp(x, y))

         rdiffDestDir = joinPaths(self.destRoot, testDir)
         entries = getBackupHistory(rdiffDestDir)
         assert len(entries) == len(backupStates)

         backupNum = 0
         for backup in backupStates:
            origBackupStateDir = joinPaths(origBackupDir, backup)
            totalBackupSize = 0
            for file in os.listdir(origBackupStateDir):
               totalBackupSize = totalBackupSize + os.lstat(joinPaths(origBackupStateDir, file))[6]

            # TODO: fix this to handle subdirs
            # assert totalBackupSize == entries[backupNum].size, "Calculated: "+str(totalBackupSize)+" Reported: "+str(entries[backupNum].size)+" State: "+str(backupNum)
            backupNum = backupNum + 1

         # Test that the last backup entry works correctly
         lastEntry = getLastBackupHistoryEntry(rdiffDestDir)

         lastBackupTime = rdw_helpers.rdwTime()
         lastBackupTime.initFromString(backupStates[-1])
         assert lastEntry.date == lastBackupTime

         # Test that timezone differences are ignored
         historyAsOf = lastEntry.date.getUrlString()

         lastBackupTime = rdw_helpers.rdwTime()
         lastBackupTime.initFromString(historyAsOf)
         entries = getBackupHistorySinceDate(rdiffDestDir, lastBackupTime)
         assert len(entries) == 1

         # Test that no backups are returned one second after the last backup
         historyAsOf = historyAsOf[:18] + "1" + historyAsOf[19:]
         postBackupTime = rdw_helpers.rdwTime()
         postBackupTime.initFromString(historyAsOf)
         assert lastBackupTime.getLocalSeconds() + 1 == postBackupTime.getLocalSeconds()
         entries = getBackupHistorySinceDate(rdiffDestDir, postBackupTime)
         assert len(entries) == 0

   def testRestoreFile(self):
      tests = self.getBackupTests()
      for testDir in tests:
         # Get a list of backup entries for the root folder
         rdiffDestDir = joinPaths(self.destRoot, testDir)
         entries = getDirEntries(rdiffDestDir, "/")

         # Go back through all backup states and make sure that the backup entries match the files that exist
         origStateDir = joinPaths(self.masterDirPath, testDir)
         backupStates = self.getBackupStates(origStateDir)
         backupStates.sort(lambda x, y: cmp(x, y))
         for backupState in backupStates:
            backupTime = rdw_helpers.rdwTime()
            backupTime.initFromString(backupState)

            # Go through each file, and make sure that the restored file looks the same as the orig file
            origStateDir = joinPaths(self.masterDirPath, testDir, backupState)
            files = self.getBackupStates(origStateDir)
            for file in files:
               origFilePath = joinPaths(origStateDir, file)
               if not os.path.isdir(origFilePath):
                  restoredFilePath = restoreFileOrDir(rdiffDestDir, "/", file, backupTime)
                  assert open(restoredFilePath, "r").read() == open(origFilePath, "r").read()
                  os.remove(restoredFilePath)

if __name__ == "__main__":
   print "Called as standalone program; running unit tests..."

   testSuite = unittest.makeSuite(LibRdiffTest, 'test')
   testRunner = unittest.TextTestRunner()
   testRunner.run(testSuite)
#    import profile
#    profile.run("getDirEntries('/', '/')", "results.txt")
