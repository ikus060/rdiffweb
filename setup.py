#!/usr/bin/env python

from distutils.core import setup, Command
import glob, sys

# < Python 2.4 does not have the package_data setup keyword, so it is unsupported
pythonVersion = sys.version_info[0]+sys.version_info[1]/10.0
if pythonVersion < 2.4:
   print 'Python version 2.3 and lower is not supported.'
   sys.exit(1)
   
setup(name='rdiffWeb',
   version='0.6.3',
   description='A web interface to rdiff-backup repositories',
   author='Josh Nisly',
   author_email='rdiffweb@joshnisly.com',
   url='http://www.rdiffweb.org',
   packages=['rdiffWeb'],
   package_data={'rdiffWeb': ['templates/*.html', 'templates/*.xml', 'templates/*.txt', 'static/*.png', 'static/*.js', 'static/*.css', 'static/images/*']},
   data_files=[('/etc/rdiffweb', ['rdw.conf.sample']),
               ('/etc/init.d', ['init/rdiff-web']),
               ('/usr/bin', ['rdiff-web']), # Manually place rdiff-web in /usr/bin, so the init script can find it
               ],
   scripts=['rdiff-web-config']
)
