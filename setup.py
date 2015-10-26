#!/usr/bin/env python
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

try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup

import sys
import os

from distutils.command.build import build as build_
from babel.messages.frontend import compile_catalog, extract_messages, update_catalog, init_catalog
from distutils.cmd import Command
from string import strip

# < Python 2.4 does not have the package_data setup keyword, so it is unsupported
pythonVersion = sys.version_info[0] + sys.version_info[1] / 10.0
if pythonVersion < 2.4:
    print 'Python version 2.3 and lower is not supported.'
    sys.exit(1)


class compile_all_catalogs(Command):
    """
    This is implementation of command which complies all catalogs
    (dictionaries).
    """

    description = 'compile message catalogs for all languages to binary MO files'
    user_options = [
        ('domain=', 'D',
         "domain of PO file (default 'messages')"),
        ('directory=', 'd',
         'path to base directory containing the catalogs'),
        ('locales=', 'l',
         'locale of the catalogs to compile'),
        ('use-fuzzy', 'f',
         'also include fuzzy translations'),
        ('statistics', None,
         'print statistics about translations')
    ]
    boolean_options = ['use-fuzzy', 'statistics']

    def initialize_options(self):
        self.domain = None
        self.directory = None
        self.locales = None
        self.use_fuzzy = False
        self.statistics = False

    def finalize_options(self):
        self.locales = map(strip, self.locales.split(','))

    def run(self):
        for locale in self.locales:
            compiler = compile_catalog(self.distribution)
            compiler.initialize_options()
            compiler.domain = self.domain
            compiler.directory = self.directory
            compiler.locale = locale
            compiler.use_fuzzy = self.use_fuzzy
            compiler.statistics = self.statistics
            compiler.finalize_options()
            compiler.run()


class build(build_):
    """
    This is modification of build command, compile_all_catalogs
    is added as last/first command
    """

    sub_commands = build_.sub_commands[:]
    sub_commands.insert(0, ('compile_all_catalogs', None))

setup(
    name='rdiffweb',
    version='0.8.0',
    description='A web interface to rdiff-backup repositories',
    author='Patrik Dufresne',
    author_email='info@patrikdufresne.com',
    url='http://www.patrikdufresne.com/en/rdiffweb/',
    license="GPLv3",
    packages=['rdiffweb'],
    include_package_data=True,
    entry_points={"console_scripts": ["rdiffweb = rdiffweb.main:start"]},
    # new commands added and build command modified
    cmdclass={
        'build': build,
        'compile_catalog': compile_catalog,
        'extract_messages': extract_messages,
        'update_catalog': update_catalog,
        'init_catalog': init_catalog,
        'compile_all_catalogs': compile_all_catalogs,
    },
    install_requires=[
        "CherryPy>=3.2.2",
        "pysqlite>=2.6.3",
        "Jinja2>=2.6",
        "yapsy>=1.10.423",
        "babel>=0.9",
    ],
    # required packages for build process
    setup_requires=[
        "babel>=0.9",
    ],
    # requirement for testing
    tests_require=[
        "mockldap>=0.2.6",
        "python-ldap>=2.4.21",
    ]
)
