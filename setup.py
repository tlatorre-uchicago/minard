#!/usr/bin/env python
from distutils.core import setup
from glob import glob

setup(name='Minard',
      version='0.1',
      description='Web App Monitoring Tools',
      author='Anthony LaTorre',
      author_email='tlatorre@uchicago.edu',
      url='snopl.us',
      scripts=['scripts/workers'],
      data_files = [# init scripts
                    ('/etc/init.d', ['utils/gunicorn','utils/snoplusmon']),
                    # static files
                    ('/var/www/minard/static/css',   [glob('minard/static/css/*')]),
                    ('/var/www/minard/static/js',    [glob('minard/static/js/*')]),
                    ('/var/www/minard/static/fonts', [glob('minard/static/fonts/*')])],
      install_requires=['flask','gunicorn','sqlalchemy','numpy','pyzmq','redis']
      )
