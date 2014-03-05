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
                    ('/opt/minard/www/static/css',    glob('minard/static/css/*')),
                    ('/opt/minard/www/static/js',     glob('minard/static/js/*')),
                    ('/opt/minard/www/static/fonts',  glob('minard/static/fonts/*')),
                    ('/opt/minard/www/static/images', glob('minard/static/images/*')),
                    ('/opt/minard/www/templates',     glob('minard/templates/*'))],
      install_requires=['flask',
                        'gunicorn',
                        'sqlalchemy',
                        'numpy',
                        'pyzmq',
                        'redis',
                        'argparse',
                        'MySQL-python']
      )
