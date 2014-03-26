.. minard documentation master file, created by
   sphinx-quickstart on Wed Mar 26 11:23:31 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to minard's documentation!
==================================

Overview
--------

The SNO+ monitoring package minard is made up of two main parts: the web server
and a set of scripts used to fetch information about the detector.

The web server is a `flask <http://flask.pocoo.org>`_ app that runs on a
`gunicorn <http://gunicorn.org>`_ server which actually **serves** the monitoring
webpage. This server displays information from a `redis <http://redis.io>`_ and
MYSQL database running on snotpenn01.

The scripts run independently of the server and *write* to the redis database.

=============== ======== ==================================================== 
script          database job                                                  
=============== ======== ==================================================== 
minard_dispatch redis    reads from the dispatch stream                       
minard_builder  redis    tails the builder log                                
orca_producer   redis    reads data from the ORCA stream                      
                         and pushes CMOS and base current                     
                         packets to local sockets
orca_consumer   redis    processes CMOS and base current                       
                         data from local sockets
=============== ======== ====================================================

Contents:

.. toctree::
   :maxdepth: 2

   install

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

