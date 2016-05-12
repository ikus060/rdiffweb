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

from __future__ import division
from __future__ import unicode_literals

from builtins import bytes
from builtins import map
from builtins import object
from builtins import str
import calendar
from future.utils import iteritems
from future.utils import python_2_unicode_compatible
from past.builtins import cmp
from past.utils import old_div
import time
from datetime import timedelta, datetime


try:
    from urllib.parse import quote, unquote
except ImportError:
    # Python 2
    from urllib import quote, unquote


# TODO: Move this into page_main
def quote_url(url, safe='/'):
    """
    Receive either str or bytes. Always return str.
    """
    # If URL is None, return None
    if not url:
        return ''
    # Convert everything to bytes
    if not isinstance(url, bytes):
        url = url.encode(encoding='latin1')
    if not isinstance(safe, bytes):
        safe = safe.encode(encoding='latin1')

    # URL encode
    val = quote(url, safe)
    if isinstance(val, bytes):
        val = val.decode(encoding='latin1')
    return val


# TODO: Move this into page_main
def unquote_url(url):
    """
    Receive either str or bytes. Always return bytes
    """
    if not url:
        return url
    # Convert everything to str
    if isinstance(url, bytes):
        url = url.decode(encoding='latin1')
    # Unquote
    val = unquote(url)
    # Make sure to return bytes.
    if isinstance(val, str):
        val = val.encode(encoding='latin1')
    return val


@python_2_unicode_compatible
class rdwTime(object):

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
            self.timeInSeconds = int(time.time())
            self.tzOffset = tz_offset or 0
        elif isinstance(value, int):
            self.timeInSeconds = value
            self.tzOffset = tz_offset or 0
        else:
            self._initFromString(value)

    def initFromMidnightUTC(self, daysFromToday):
        self.timeInSeconds = time.time()
        self.timeInSeconds -= self.timeInSeconds % (24 * 60 * 60)
        self.timeInSeconds += daysFromToday * 24 * 60 * 60
        self.tzOffset = 0

    def _initFromString(self, timeString):
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
            self.timeInSeconds = calendar.timegm(timetuple)
            self.tzOffset = self._tzdtoseconds(timeString[19:])
            self.getTimeZoneString()  # to get assertions there

        except (TypeError, ValueError, AssertionError):
            raise ValueError(timeString)

    def getLocalDaysSinceEpoch(self):
        return self.getLocalSeconds() // (24 * 60 * 60)

    def getLocalSeconds(self):
        return self.timeInSeconds

    def getSeconds(self):
        return self.timeInSeconds - self.tzOffset

    def getDisplayString(self):
        value = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.getLocalSeconds()))
        if isinstance(value, bytes):
            value = value.decode(encoding='latin1')
        return value

    def getTimeZoneString(self):
        if self.tzOffset:
            tzinfo = self._getTimeZoneDisplayInfo()
            return "%s%s:%s" % (tzinfo["plusMinus"], tzinfo["hours"], tzinfo["minutes"])
        else:
            return "Z"

    def setTime(self, hour, minute, second):
        year = time.gmtime(self.timeInSeconds)[0]
        month = time.gmtime(self.timeInSeconds)[1]
        day = time.gmtime(self.timeInSeconds)[2]
        self.timeInSeconds = calendar.timegm(
            (year, month, day, hour, minute, second, -1, -1, 0))

    def _getTimeZoneDisplayInfo(self):
        hours, minutes = divmod(old_div(abs(self.tzOffset), 60), 60)
        assert 0 <= hours <= 23
        assert 0 <= minutes <= 59

        if self.tzOffset > 0:
            plusMinus = "+"
        else:
            plusMinus = "-"
        return {"plusMinus": plusMinus,
                "hours": "%02d" % hours,
                "minutes": "%02d" % minutes}

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
        return rdwTime(self.timeInSeconds + int(other.total_seconds()), self.tzOffset)

    def __sub__(self, other):
        """Support minus (-) timedelta"""
        assert isinstance(other, timedelta) or isinstance(other, rdwTime)
        # Sub with timedelta, return rdwTime
        if isinstance(other, timedelta):
            return rdwTime(self.timeInSeconds - int(other.total_seconds()), self.tzOffset)

        # Sub with rdwTime, return timedelta
        if isinstance(other, rdwTime):
            return timedelta(seconds=self.timeInSeconds - other.timeInSeconds)

    def __int__(self):
        """Return this date as seconds since epoch."""
        return self.timeInSeconds

    def __lt__(self, other):
        assert isinstance(other, rdwTime)
        return self.getSeconds() < other.getSeconds()

    def __le__(self, other):
        assert isinstance(other, rdwTime)
        return self.getSeconds() <= other.getSeconds()

    def __gt__(self, other):
        assert isinstance(other, rdwTime)
        return self.getSeconds() > other.getSeconds()

    def __ge__(self, other):
        assert isinstance(other, rdwTime)
        return self.getSeconds() >= other.getSeconds()

    def __cmp__(self, other):
        assert isinstance(other, rdwTime)
        return cmp(self.getSeconds(), other.getSeconds())

    def __eq__(self, other):
        return (isinstance(other, rdwTime) and
                self.getSeconds() == other.getSeconds())

    def __hash__(self):
        return hash(self.getSeconds())

    def __str__(self):
        """return utf-8 string"""
        return self.getDisplayString()

    def __repr__(self):
        """return second since epoch"""
        return str(self.getSeconds())

# Taken from ASPN:
# http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/259173


class groupby(dict):

    def __init__(self, seq, key=lambda x: x):
        for value in seq:
            k = key(value)
            self.setdefault(k, []).append(value)
    __iter__ = iteritems
