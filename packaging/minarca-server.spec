# -*- mode: python ; coding: utf-8 -*-
#
# Copyright (C) 2025 IKUS Software. All rights reserved.
# IKUS Software inc. PROPRIETARY/CONFIDENTIAL.
# Use is subject to license terms.
#
# This script is used by pyinstaller to freeze the python code into an
# executable for linux.
#
import shutil
from email import message_from_string
from importlib.metadata import distribution as get_distribution
from importlib.resources import files
from os.path import join

from debbuild import debbuild
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, copy_metadata

#
# Common values
#
minarca_server_pkg = files('minarca_server')
# Read package info
pkg = get_distribution('minarca_server')
version = pkg.version
# Get License file's data
license = pkg.read_text('LICENSE')
pkg_info = message_from_string(pkg.read_text('PKG-INFO') or pkg.read_text('METADATA'))
block_cipher = None

# Include cheroot SSL for https support
hiddenimports=[]
hiddenimports.extend(collect_submodules('cheroot.ssl'))

# Include theme resources and locales
datas = []
datas.extend(collect_data_files('rdiffweb'))
datas.extend(collect_data_files('minarca_server'))

# Exclude Tests folders
datas = [(src, dest) for src, dest in datas if '/tests/' not in src]

exes = []
analyses = []
executables = [("minarca-server", minarca_server_pkg / 'main.py'), ("minarca-shell", minarca_server_pkg / 'shell.py')]

for exe_name, script in executables:
    a = Analysis(
        [script],
        hiddenimports=hiddenimports,
        datas=datas,
        win_no_prefer_redirects=False,
        win_private_assemblies=False,
        cipher=block_cipher,
        noarchive=True,
    )
    # To avoid issue on Linux with mixed version, make sure to exclude libstdc++ to use the one provided by the system.
    a.binaries = [entry for entry in a.binaries if 'libstdc++' not in entry[0]]
    pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name=exe_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=False,
        console=True,
    )
    analyses.append(a)
    exes.append(exe)

coll = COLLECT(
    *exes,
    *[a.binaries for a in analyses],
    *[a.zipfiles for a in analyses],
    *[a.datas for a in analyses],
    strip=False,
    upx=False,
    upx_exclude=[],
    name='minarca-server',
)

# Get Project URL
project_url = [v.split(', ')[1] for k, v in pkg_info.items() if k == 'Project-URL' and v.startswith('Homepage, ')][0]

# Also create a Debian package
debbuild(
    name='minarca-server',
    version=version,
    architecture='amd64',
    data_src=[
        ('/etc/minarca/minarca-server.conf', join(SPECPATH, 'minarca-server.conf')),
        ('/etc/minarca/conf.d/placeholder', join(SPECPATH, 'placeholder')),
        ('/etc/sysctl.d/10-minarca-server-userns.conf', join(SPECPATH, '10-minarca-server-userns.conf')),
        ('/lib/systemd/system/minarca-server.service', join(SPECPATH, 'minarca-server.service')),
        ('/opt/minarca-server/share/minarca.ico', join(minarca_server_pkg, 'minarca.ico')),
        ('/opt/minarca-server/share/minarca_logo.svg', join(minarca_server_pkg, 'minarca_logo.svg')),
        ('/opt/minarca-server', join(DISTPATH, 'minarca-server')),
        ('/usr/share/man/man1/minarca-server.1', join(SPECPATH, 'minarca-server.1')),
    ],
    description=pkg_info['Summary'],
    long_description="""Minarca Client is the **client-side component** of Minarca, a **free and open-source backup solution** designed for small businesses and service providers. It offers a simple, self-hosted way to manage backups with an intuitive **web interface** for browsing and restoring files.""",
    url=project_url,
    maintainer=pkg_info['Author-email'],
    output=DISTPATH,
    postinst=join(SPECPATH, "minarca-server.postinst"),
    prerm=join(SPECPATH, "minarca-server.prerm"),
    postrm=join(SPECPATH, "minarca-server.postrm"),
    symlink=[
        ("/opt/minarca-server/rdiff-backup-delete", "/opt/rdiff-backup-2.2/rdiff-backup-delete"),
        ("/opt/minarca-server/rdiff-backup", "/opt/rdiff-backup-2.2/rdiff-backup"),
    ],
    depends=[
        'adduser',
        'rdiff-backup-1.2',
        'rdiff-backup-2.0',
        'rdiff-backup-2.2',
        'openssh-client',
        'openssh-server',
        'libc6',
        'libstdc++6',
    ],
)
