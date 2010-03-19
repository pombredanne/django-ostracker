#!/usr/bin/env python

from distutils.core import setup

setup(name='django-ostracker',
      version='0.2.0-dev',
      description='Django project for tracking Open Source projects',
      author='James Turk',
      author_email='jturk@sunlightfoundation.com',
      license='BSD',
      url='http://github.com/sunlightlabs/django-ostracker/',
      packages=['ostracker', 'ostracker.management', 'ostracker.management.commands',],
      package_data={'ostracker': ['templates/ostracker/*.html']},
)
