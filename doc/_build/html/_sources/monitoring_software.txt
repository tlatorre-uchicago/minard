List of Monitoring Software
===========================

minard_dispatch_push
--------------------

* **Command**: ``minard_dispatch push [--host HOST]``
* **Runs as**: snoplusmon
* **Ports**: 5560
* **Started by**: supervisord
* **Log File**: ``/var/log/minard_dispatch_push.log``
* **Description**: Reads events from the dispatch stream and pushes them to a ZMQ push/pull socket for processing.

minard_dispatch_pull
--------------------

* **Command**: ``minard_dispatch pull``
* **Runs as**: snoplusmon
* **Ports**: 5560
* **Started by**: supervisord
* **Log File**: ``/var/log/minard_dispatch_pull.log``
* **Description**: Reads events from a ZMQ push/pull socket, and writes info to a redis database.

redis
-----

* **Command**: ``redis``
* **Runs as**: root
* **Snapshot**: ``/opt/redis/dump.rdb``
* **Configuration file**: ``/etc/redis/6379.conf``
* **Ports**: 6379
* **Started by**: ``/etc/init.d/redis_6379``
* **Log File**: ``/var/log/redis.log``
* **Description**: redis database.

gunicorn
--------

* **Command**: ``gunicorn -b 0.0.0.0:8080 minard:app --user=gunicorn``
* **Run as** : root (drops to gunicorn)
* **Ports**: 8080
* **Started by**: ``/etc/init.d/gunicorn``
* **Log File**: ``/tmp/minard.log`` and ``/var/log/gunicorn.log``
* **Description**: Gunicorn web server which serves the main site.

gunicorn (logging server)
-------------------------

* **Command**: ``gunicorn -b 0.0.0.0:8081 snoplus_log:app --user=gunicorn``
* **Run as** : root (drops to gunicorn)
* **Ports**: 8081
* **Started by**: supervisord
* **Log File**: ``/tmp/snoplus_log.log`` and ``/var/log/gunicorn_log.log``
* **Description**: Gunicorn web server for logging.

nginx
-----

* **Command**: ``nginx -c /etc/nginx/nginx.conf``
* **Run as** : root (drops to nginx)
* **Configuration file**: ``/etc/nginx/nginx.conf``
* **Ports**: 50000
* **Started by**: ``/etc/init.d/nginx``
* **Log File**: ``/var/log/nginx/error.log`` and ``/var/log/nginx/access.log``
* **Description**: nginx web server which serves static files and slow clients for the main site.

orca_producer
-------------

* **Command**: ``orca_producer [--host HOST] [--port PORT]``
* **Run as**: snoplusmon
* **Ports**: 5557, 5558
* **Started by**: supervisord
* **Log File**: ``/var/log/orca_producer.log``
* **Description**: Reads CMOS rates and base current records from the ORCA data stream and pushes them to ZMQ push/pull sockets for processing.

orca_consumer_cmos
------------------

* **Command**: ``orca_consumer 5557``
* **Run as**: snoplusmon
* **Ports**: 5557
* **Started by**: supervisord
* **Log File**: ``/var/log/orca_consumer_cmos.log``
* **Description**: Reads CMOS rates from a ZMQ push/pull socket and writes to the redis database.

orca_consumer_base
------------------

* **Command**: ``orca_consumer 5558``
* **Run as**: snoplusmon
* **Ports**: 5558
* **Started by**: supervisord
* **Log File**: ``/var/log/orca_consumer_base.log``
* **Description**: Reads base currents from a ZMQ push/pull socket and writes to the redis database.

supervisord
-----------

* **Command**: ``supervisord -c /etc/supervisord.conf``
* **Run as**: root
* **Configuration file**: ``/etc/supervisord.conf``
* **Ports**: 9001
* **Started by**: ``/etc/init.d/supervisord``
* **Log File**: ``/var/log/supervisord.log``
* **Description**: Starts and manages many of the monitoring processes.

