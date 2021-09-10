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

from distutils.cmd import Command
from distutils.dist import DistributionMetadata
from distutils.errors import DistutilsExecError
from io import open
from setuptools import setup
import os
import subprocess
import sys


# Check running python version.
if not sys.version_info >= (3, 6):
    print('python version 3.6 is required.')
    sys.exit(1)

DistributionMetadata.templates = None

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

# Compute requirements
tests_require = [
    "mock>=1.3.0",
    "coverage>=4.0.1",
    "mockldap>=0.2.6",
    "pytest<5.0.0",
]
extras_require = {'tox': tests_require}

long_description = None
with open(os.path.join(os.path.dirname(__file__), 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='rdiffweb',
    use_scm_version=True,
    description='A web interface to rdiff-backup repositories',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Patrik Dufresne',
    author_email='patrik@ikus-soft.com',
    url='https://rdiffweb.org/',
    license="GPLv3",
    packages=['rdiffweb'],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "rdiffweb = rdiffweb.main:main",
            "rdiffweb-restore = rdiffweb.core.restore:main",
        ],
        "rdiffweb.plugins": []
    },
    # new commands added and build command modified
    cmdclass={
        'compile_all_catalogs': compile_all_catalogs,
    },
    install_requires=[
        "CherryPy>=8.9.1",
        "Jinja2>=2.10,<3",
        "psutil>=2.1.1",
        "babel>=0.9.6",
        "python-ldap",
        "WTForms<3.0.0",
        "distro",
        "humanfriendly",
        "configargparse",
        "sqlalchemy",
        "apscheduler",
        "chartkick",
    ],
    # required packages for build process
    setup_requires=[
        "babel>=0.9.6",
        "setuptools_scm",
    ],
    # requirement for testing
    tests_require=tests_require,
    extras_require=extras_require,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Framework :: CherryPy',
    ],
    python_requires='!=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, !=3.5.*, <4',
)
