#!/usr/bin/env python
from distutils.core import setup

setup(name='Minard',
      version='0.1',
      description='Web App Monitoring Tools',
      author='Anthony LaTorre',
      author_email='tlatorre@uchicago.edu',
      url='',
      install_requires=['flask','flask-login','gunicorn','sqlalchemy','numpy','pyzmq','redis']
      )
