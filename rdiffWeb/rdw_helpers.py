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

import calendar
import datetime
import os
import re
import time
import urllib
import zipfile
import tarfile
import subprocess


def encodePath(path):
    if isinstance(path, unicode):
        return path.encode('utf-8')
    return path


def joinPaths(parentPath, *args):
    parentPath = encodePath(parentPath)
    args = [x.lstrip("/") for x in args]
    return os.path.join(parentPath, *args)


def getStaticRootPath():
    return os.path.abspath(os.path.dirname(__file__))


class accessDeniedError:

    def __str__(self):
        return "Access is denied."


def encodeUrl(url, safeChars=""):
    if not url:
        return url
    url = encodePath(url)
    return urllib.quote_plus(url, safeChars)


def decodeUrl(encodedUrl):
    if not encodedUrl:
        return encodedUrl
    return urllib.unquote_plus(encodedUrl)


def removeDir(dir):
    for root, dirs, files in os.walk(dir, topdown=False):
        for name in files:
            filePath = os.path.join(root, name)
            if os.path.islink(filePath):
                os.unlink(filePath)
            else:
                os.remove(filePath)
        for name in dirs:
            dirPath = os.path.join(root, name)
            if os.path.islink(dirPath):
                os.unlink(dirPath)
            else:
                os.rmdir(dirPath)
    os.rmdir(dir)


def formatNumStr(num, maxDecimals):
    numStr = "%.*f" % (maxDecimals, num)

    def replaceFunc(match):
        if match.group(1):
            return "." + match.group(1)
        return ""
    return re.compile("\.([^0]*)[0]+$").sub(replaceFunc, numStr)


class rdwTime:

    """Time information has two components: the local time, stored in GMT as seconds since Epoch,
    and the timezone, stored as a seconds offset.  Since the server may not be in the same timezone
    as the user, we cannot rely on the built-in localtime() functions, but look at the rdiff-backup string
    for timezone information.  As a general rule, we always display the "local" time, but pass the timezone
    information on to rdiff-backup, so it can restore to the correct state"""

    def __init__(self):
        self.timeInSeconds = 0
        self.tzOffset = 0

    def initFromCurrentUTC(self):
        self.timeInSeconds = time.time()
        self.tzOffset = 0

    def initFromMidnightUTC(self, daysFromToday):
        self.timeInSeconds = time.time()
        self.timeInSeconds -= self.timeInSeconds % (24 * 60 * 60)
        self.timeInSeconds += daysFromToday * 24 * 60 * 60
        self.tzOffset = 0

    def initFromString(self, timeString):
        try:
            date, daytime = timeString[:19].split("T")
            year, month, day = map(int, date.split("-"))
            hour, minute, second = map(int, daytime.split(":"))
            assert 1900 < year < 2100, year
            assert 1 <= month <= 12
            assert 1 <= day <= 31
            assert 0 <= hour <= 23
            assert 0 <= minute <= 59
            assert 0 <= second <= 61  # leap seconds

            timetuple = (year, month, day, hour, minute, second, -1, -1, 0)
            self.timeInSeconds = calendar.timegm(timetuple)
            self.tzOffset = self._tzdtoseconds(timeString[19:])
            self.getTimeZoneString()  # to get assertions there

        except (TypeError, ValueError, AssertionError):
            raise ValueError(timeString)

    def getLocalDaysSinceEpoch(self):
        return self.getLocalSeconds() // (24 * 60 * 60)

    def getDaysSinceEpoch(self):
        return self.getSeconds() // (24 * 60 * 60)

    def getLocalSeconds(self):
        return self.timeInSeconds

    def getSeconds(self):
        return self.timeInSeconds - self.tzOffset

    def getDateDisplayString(self):
        return time.strftime("%Y-%m-%d", time.gmtime(self.timeInSeconds))

    def getDisplayString(self):
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.getLocalSeconds()))

    def getUrlString(self):
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(self.getLocalSeconds())) + self.getTimeZoneString()

    def getUrlStringNoTZ(self):
        return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(self.getSeconds())) + "Z"

    def getTimeZoneString(self):
        if self.tzOffset:
            tzinfo = self._getTimeZoneDisplayInfo()
            return tzinfo["plusMinus"] + tzinfo["hours"] + ":" + tzinfo["minutes"]
        else:
            return "Z"

    def setTime(self, hour, minute, second):
        year = time.gmtime(self.timeInSeconds)[0]
        month = time.gmtime(self.timeInSeconds)[1]
        day = time.gmtime(self.timeInSeconds)[2]
        self.timeInSeconds = calendar.timegm(
            (year, month, day, hour, minute, second, -1, -1, 0))

    def _getTimeZoneDisplayInfo(self):
        hours, minutes = divmod(abs(self.tzOffset) / 60, 60)
        assert 0 <= hours <= 23
        assert 0 <= minutes <= 59

        if self.tzOffset > 0:
            plusMinus = "+"
        else:
            plusMinus = "-"
        return {"plusMinus": plusMinus, "hours": "%02d" % hours, "minutes": "%02d" % minutes}

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

    def __cmp__(self, other):
        return cmp(self.getSeconds(), other.getSeconds())

# Taken from ASPN:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/259173


class groupby(dict):

    def __init__(self, seq, key=lambda x: x):
        for value in seq:
            k = key(value)
            self.setdefault(k, []).append(value)
    __iter__ = dict.iteritems


# Taken from ASPN:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/278731
def daemonize():
    """Detach a process from the controlling terminal and run it in the
    background as a daemon. """
    if (hasattr(os, "devnull")):
        REDIRECT_TO = os.devnull
    else:
        REDIRECT_TO = "/dev/null"
    MAXFD = 1024
    UMASK = 0

    try:
        pid = os.fork()
    except OSError as e:
        raise Exception("%s [%d]" % (e.strerror, e.errno))

    if (pid == 0):  # The first child.
        os.setsid()
        try:
            pid = os.fork()  # Fork a second child.
        except OSError as e:
            raise Exception("%s [%d]" % (e.strerror, e.errno))

        if (pid == 0):  # The second child.
            os.umask(UMASK)
        else:
            os._exit(0)  # Exit parent (the first child) of the second child.
    else:
        os._exit(0)  # Exit parent of the first child.

# Redirecting output to /dev/null fails when called from a script, for some reason...
# import resource        # Resource usage information.
#     maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
#     if (maxfd == resource.RLIM_INFINITY):
#         maxfd = MAXFD
#     for fd in range(0, maxfd):
#         try:
#             os.close(fd)
# except OSError:    # ERROR, fd wasn't open to begin with (ignored)
#             pass
# os.open(REDIRECT_TO, os.O_RDWR)  # standard input (0)
# os.dup2(0, 1)          # standard output (1)
# os.dup2(0, 2)          # standard error (2)
    return(0)


def execute(command, *args):
    parms = [command]
    parms.extend(args)
    execution = subprocess.Popen(
        parms, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    results = {}
    results['exitCode'] = execution.wait()
    (results['stdout'], results['stderr']) = execution.communicate()
    return results


import unittest


class helpersTest(unittest.TestCase):

    def testJoinPaths(self):
        assert(joinPaths("/", "/test", "/temp.txt") == "/test/temp.txt")
        assert(joinPaths("/", "test", "/temp.txt") == "/test/temp.txt")
        assert(joinPaths("/", "/test", "temp.txt") == "/test/temp.txt")
        assert(joinPaths("/", "//test", "/temp.txt") == "/test/temp.txt")
        assert(joinPaths("/", "", "/temp.txt") == "/temp.txt")
        assert(joinPaths("test", "", "/temp.txt") == "test/temp.txt")

    def testRdwTime(self):
        # Test initialization
        myTime = rdwTime()
        assert myTime.getSeconds() == 0
        goodTimeString = "2005-12-25T23:34:15-05:00"
        goodTimeStringNoTZ = "2005-12-26T04:34:15Z"
        myTime.initFromString(goodTimeString)

        myTimeNoTZ = rdwTime()
        myTimeNoTZ.initFromString(goodTimeStringNoTZ)
        assert myTimeNoTZ.getSeconds() == myTimeNoTZ.getLocalSeconds()
        assert myTime.getSeconds() == myTimeNoTZ.getSeconds()

        # Test correct load and retrieval
        assert myTime.getUrlString() == goodTimeString
        assert myTime.getUrlStringNoTZ() == goodTimeStringNoTZ
        assert myTime.getDisplayString() == "2005-12-25 23:34:15"
        assert myTime.getRSSPubDateString(
        ) == "Sun, 25 Dec 2005 23:34:15 -0500"

        assert myTime.getDateDisplayString() == "2005-12-25"
        assert myTime.getLocalSeconds() < myTime.getSeconds()
        assert myTime.getLocalSeconds() == 1135571655 - 5 * 60 * 60
        assert myTime.getSeconds() == 1135571655
        assert myTime.getLocalDaysSinceEpoch() <= myTime.getDaysSinceEpoch()
        assert myTime.getLocalDaysSinceEpoch() == 13142
        assert myTime.getDaysSinceEpoch() == 13143

        goodTimeString = "2005-12-25T23:04:15-05:30"
        myTime.initFromString(goodTimeString)
        assert myTime.getUrlString() == goodTimeString
        assert myTime.getUrlStringNoTZ() == goodTimeStringNoTZ

        goodTimeString = "2005-12-26T09:34:15+05:00"
        myTime.initFromString(goodTimeString)
        assert myTime.getUrlString() == goodTimeString
        assert myTime.getUrlStringNoTZ() == goodTimeStringNoTZ

        goodTimeString = "2005-12-26T10:04:15+05:30"
        myTime.initFromString(goodTimeString)
        assert myTime.getUrlString() == goodTimeString
        assert myTime.getUrlStringNoTZ() == goodTimeStringNoTZ

        # Test boundaries on days since epoch
        myTime.initFromString("2005-12-31T18:59:59-05:00")
        assert myTime.getUrlStringNoTZ() == "2005-12-31T23:59:59Z"
        assert myTime.getDaysSinceEpoch() == 13148
        assert myTime.getLocalDaysSinceEpoch() == 13148

        myTime.initFromString("2005-12-31T19:00:00-05:00")
        assert myTime.getUrlStringNoTZ() == "2006-01-01T00:00:00Z"
        assert myTime.getDaysSinceEpoch() == 13149
        assert myTime.getLocalDaysSinceEpoch() == 13148

        # Test UTC
        myTime.initFromCurrentUTC()
        assert myTime.getSeconds() == myTime.getLocalSeconds()
        todayAsString = myTime.getDateDisplayString()

        # Test midnight UTC
        myTime.initFromMidnightUTC(0)
        assert myTime.getSeconds() == myTime.getLocalSeconds()
        assert myTime.getUrlString().find("T00:00:00Z") != -1
        assert myTime.getDateDisplayString() == todayAsString

        myTime.initFromCurrentUTC()
        midnightTime = rdwTime()
        midnightTime.initFromMidnightUTC(0)
        assert myTime.getSeconds() != midnightTime.getSeconds()
        myTime.setTime(0, 0, 0)
        assert myTime.getSeconds() == midnightTime.getSeconds()

        # Make sure it rejects bad strings with the appropriate exceptions
        badTimeStrings = ["2005-12X25T23:34:15-05:00",
                          "20005-12-25T23:34:15-05:00", "2005-12-25", "2005-12-25 23:34:15"]
        for badTime in badTimeStrings:
            try:
                myTime.initFromString(badTime)
            except ValueError:
                pass
            else:
                assert False

    def testGroupBy(self):
        numbers = [1, 2, 3, 4, 5, 6, 0, 0, 5, 5]
        groupedNumbers = groupby(numbers)
        assert groupedNumbers == {
            0: [0, 0], 1: [1], 2: [2], 3: [3], 4: [4], 5: [5, 5, 5], 6: [6]}

        projects = [
            {"name": "rdiffWeb", "language": "python"}, {
                "name": "CherryPy", "language": "python"},
            {"name": "librsync", "language": "C"}]
        projectsByLanguage = groupby(projects, lambda x: x["language"])
        assert projectsByLanguage == {
            "C": [{"name": "librsync", "language": "C"}],
            "python": [{"name": "rdiffWeb", "language": "python"}, {"name": "CherryPy", "language": "python"}]}
