#!/usr/bin/env python
from distutils.core import setup
from glob import glob

setup(name='minard',
      version='0.2',
      description='Web App Monitoring Tools',
      author='Anthony LaTorre',
      author_email='tlatorre@uchicago.edu',
      url='snopl.us',
      packages=['minard','snoplus_log'],
      scripts=glob('scripts/*'),
      data_files = [# static files
                    ('www/static/css',    glob('minard/static/css/*')),
                    ('www/static/js',     glob('minard/static/js/*')),
                    ('www/static/fonts',  glob('minard/static/fonts/*')),
                    ('www/static/images', glob('minard/static/images/*')),
                    ('www/static/gen', glob('minard/static/gen/*')),
                    ('www/static/audio',  glob('minard/static/audio/*')),
                    ('www/templates',     glob('minard/templates/*'))],
      install_requires=['flask',
                        'gunicorn',
                        'numpy',
                        'pyzmq',
                        'redis',
                        'argparse',
                        'sphinx',
                        'requests',
                        'alabaster']
      )
