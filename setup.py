#!/usr/bin/env python
from setuptools import setup
from glob import glob

setup(name='minard',
      version='1.0',
      description='Web App Monitoring Tools',
      author='Anthony LaTorre',
      author_email='tlatorre@uchicago.edu',
      url='snopl.us',
      packages=['minard','snoplus_log'],
      include_package_data=True,
      scripts=glob('bin/*'),
      data_files = [# static files
                    ('www/static/css',    glob('minard/static/css/*')),
                    ('www/static/js',     glob('minard/static/js/*')),
                    ('www/static/fonts',  glob('minard/static/fonts/*')),
                    ('www/static/images', glob('minard/static/images/*')),
                    ('www/static/audio',  glob('minard/static/audio/*')),
                    ('www/templates',     glob('minard/templates/*'))],
      install_requires=['flask',
                        'gunicorn',
                        'numpy',
                        'pyzmq',
                        'redis>=2.10',
                        'argparse',
                        'sphinx',
                        'requests',
                        'alabaster']
      )
