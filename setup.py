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

from __future__ import print_function

import sys
PY2 = sys.version_info[0] == 2

# Check running python version.
if not PY2 and not sys.version_info >= (3, 4):
    print('python version 3.4 is required.')
    sys.exit(1)

if PY2 and not sys.version_info >= (2, 7):
    print('python version 2.7 is required.')
    sys.exit(1)

from distutils.cmd import Command
from distutils.command.build import build as build_
from distutils.dist import DistributionMetadata
from distutils.log import error, info
from distutils.util import split_quoted
from setuptools.command.test import test as TestCommand
import os
from string import Template
import subprocess

try:
    from setuptools import setup
except ImportError:
    import ez_setup
    ez_setup.use_setuptools()
    from setuptools import setup

DistributionMetadata.templates = None


class fill_template(Command):
    """
    Custom distutils command to fill text templates with release meta data.
    """

    description = "Fill placeholders in documentation text file templates"

    user_options = [
        ('templates=', None, "Template text files to fill")
    ]

    def initialize_options(self):
        self.templates = ''
        self.template_ext = '.in'

    def finalize_options(self):
        if isinstance(self.templates, str):
            self.templates = split_quoted(self.templates)

        self.templates += getattr(self.distribution.metadata, 'templates', None) or []

        for tmpl in self.templates:
            if not tmpl.endswith(self.template_ext):
                raise ValueError(
                    "Template file '%s' does not have expected " +
                    "extension '%s'." % (tmpl, self.template_ext))

    def run(self):
        metadata = self.get_metadata()

        for infilename in self.templates:
            try:
                info("Reading template '%s'...", infilename)
                with open(infilename) as infile:
                    tmpl = Template(infile.read())
                    outfilename = infilename.rstrip(self.template_ext)

                    info("Writing filled template to '%s'.", outfilename)
                    with open(outfilename, 'w') as outfile:
                        outfile.write(tmpl.safe_substitute(metadata))
            except:
                error("Could not open template '%s'.", infilename)

    def get_metadata(self):
        data = dict()
        for attr in self.distribution.metadata.__dict__:
            if not callable(attr):
                data[attr] = getattr(self.distribution.metadata, attr)

        return data


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
        self.locales = list(map(str.strip, self.locales.split(',')))

    def run(self):
        from babel.messages.frontend import compile_catalog
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


class build_less(Command):
    """
    Command to build less file with lessc.
    """

    description = 'compile *.less files with lessc command.'
    user_options = [
        ('files=', 'f',
         "List of less files to compile. Separated by `;`."),
        ('include-path=', None,
         'Set include paths. Separated by `;`'),
        ('compress', 'x',
         'Compress output by removing some whitespaces.'),
        ('output-dir', None,
         'Output directory where to generate the .less files. Default to current.'),
    ]
    boolean_options = ['compress']

    def initialize_options(self):
        self.files = None
        self.include_path = None
        self.compress = False
        self.output_dir = False

    def finalize_options(self):
        self.files = self.files.split(';')

    def run(self):
        """
        Run `lessc` for each file.
        """
        if not self.files:
            return
        # lessc --include-path=/home/ikus060/workspace/Minarca/rdiffweb.git/rdiffweb/static/less minarca_brand/main.less
        for f in self.files:
            args = ['lessc']
            if self.include_path:
                args.append('--include-path=' + self.include_path)
            if self.compress:
                args.append('--compress')
            # Source
            args.append(f)
            # Destination
            destination = f.replace('.less', '.css')
            if self.output_dir:
                destination = os.path.join(self.output_dir, os.path.basename(destination))
            args.append(destination)
            # Execute command line.
            subprocess.call(args)


class build(build_):
    """
    This is modification of build command, compile_all_catalogs
    is added as last/first command
    """

    sub_commands = build_.sub_commands[:]
    sub_commands.insert(0, ('compile_all_catalogs', None))


class tox(TestCommand):
    user_options = [('tox-args=', 'a', "Arguments to pass to tox")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.tox_args = None

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import tox
        import shlex
        args = self.tox_args
        if args:
            args = shlex.split(self.tox_args)
        errno = tox.cmdline(args=args)
        sys.exit(errno)

# Compute requirements
install_requires = [
    "CherryPy>=3.2.2",
    "Jinja2>=2.6",
    "babel>=0.9.6",
    "future>=0.15.2",
]
if PY2:
    install_requires.extend(["pysqlite>=2.6.3"])

setup(
    name='rdiffweb',
    version='0.9.5',
    description='A web interface to rdiff-backup repositories',
    author='Patrik Dufresne',
    author_email='info@patrikdufresne.com',
    url='http://www.patrikdufresne.com/en/rdiffweb/',
    license="GPLv3",
    packages=['rdiffweb'],
    include_package_data=True,
    entry_points={
        "console_scripts": ["rdiffweb = rdiffweb.main:start"],
        "rdiffweb.plugins": [
            "EmailNotification = rdiffweb.plugins.notification",
            "SQLite = rdiffweb.plugins.db_sqlite",
            "Ldap = rdiffweb.plugins.ldap_auth",
            "UserPrefsGeneral = rdiffweb.plugins.prefs_general",
            "UserPrefsSSHKeys = rdiffweb.plugins.prefs_sshkeys",
            "UpdateRepos = rdiffweb.plugins.update_repos",
            "Graphs = rdiffweb.plugins.graphs",
            "DeleteRepo = rdiffweb.plugins.delete_repo",
            "RemoveOlder = rdiffweb.plugins.remove_older",
            "SetEncoding = rdiffweb.plugins.set_encoding",
        ]
    },
    # new commands added and build command modified
    cmdclass={
        'build': build,
        'compile_all_catalogs': compile_all_catalogs,
        'filltmpl': fill_template,
        'build_less': build_less,
        'tox': tox,
    },
    templates=['sonar-project.properties.in'],
    install_requires=install_requires,
    # required packages for build process
    setup_requires=[
        "babel>=0.9.6",
    ],
    # requirement for testing
    tests_require=[
        "tox",
        "mock>=1.3.0",
        "coverage>=4.0.1",
        "mockldap>=0.2.6",
        "pycrypto>=2.6.1",
    ]
)
