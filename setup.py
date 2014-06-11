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
                    ('www/static/css',    glob('minard/static/css/*')),
                    ('www/static/js',     glob('minard/static/js/*')),
                    ('www/static/fonts',  glob('minard/static/fonts/*')),
                    ('www/static/images', glob('minard/static/images/*')),
                    ('www/templates',     glob('minard/templates/*'))],
      install_requires=['flask',
                        'gunicorn',
                        'sqlalchemy',
                        'numpy',
                        'pyzmq',
                        'redis',
                        'argparse',
                        'sphinx',
                        'alabaster',
                        'python-daemon',
                        'MySQL-python']
      )
