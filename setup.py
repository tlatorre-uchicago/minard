#!/usr/bin/env python
from distutils.core import setup
from glob import glob

setup(name='minard',
      version='0.1',
      description='Web App Monitoring Tools',
      author='Anthony LaTorre',
      author_email='tlatorre@uchicago.edu',
      url='snopl.us',
      packages=['minard'],
      scripts=glob('scripts/*'),
      data_files = [# static files
                    ('/opt/minard/www/minard/static/css',    glob('minard/static/css/*')),
                    ('/opt/minard/www/minard/static/js',     glob('minard/static/js/*')),
                    ('/opt/minard/www/minard/static/fonts',  glob('minard/static/fonts/*')),
                    ('/opt/minard/www/minard/static/images', glob('minard/static/images/*')),
                    ('/opt/minard/www/minard/templates',     glob('minard/templates/*'))],
      install_requires=['flask',
                        'gunicorn',
                        'sqlalchemy',
                        'numpy',
                        'pyzmq',
                        'redis',
                        'argparse',
                        'MySQL-python']
      )
