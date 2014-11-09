#!/usr/bin/env python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012 rdiffweb contributors
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

try:
    from setuptools import setup, find_packages, Extension
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup, find_packages, Extension

import sys

# < Python 2.4 does not have the package_data setup keyword, so it is unsupported
pythonVersion = sys.version_info[0] + sys.version_info[1] / 10.0
if pythonVersion < 2.4:
    print 'Python version 2.3 and lower is not supported.'
    sys.exit(1)

setup(name='rdiffweb',
      version='0.6.5',
      description='A web interface to rdiff-backup repositories',
      author='Patrik Dufresne',
      author_email='info@patrikdufresne.com',
      url='http://www.patrikdufresne.com/en/rdiffweb/',
      packages=['rdiffweb'],
      package_data={'rdiffweb': ['templates/*.html', 'templates/*.xml',
                                 'templates/*.txt', 'static/*.png',
                                 'static/js/scripts.min.js',
                                 'static/js/vendor/*.js',
                                 'static/css/*.css', 'static/fonts/*']},
      data_files=[('/etc/rdiffweb', ['rdw.conf.sample']),
                  ('/etc/init.d', ['init-script/rdiffweb'])
                  ],
      scripts=['rdiffweb-config'],
      entry_points={"console_scripts": ["rdiffweb = rdiffweb.main:start"]},
      install_requires=["CherryPy>=3.2.2",
      		            "pysqlite>=2.6.3",
                        "Jinja2>=2.6"]
      )