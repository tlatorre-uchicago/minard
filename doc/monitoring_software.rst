List of Monitoring Software
===========================

minard_dispatch_push
--------------------

* **Command**: `minard_dispatch push [--host HOST]`
* **Ports**: 5560
* **Started by**: supervisord
* **Log File**: `/var/log/minard_dispatch_push.log`
* **Description**: Reads events from the dispatch stream and pushes them to a ZMQ push/pull socket for processing.

minard_dispatch_pull
--------------------

* **Command**: `minard_dispatch pull`
* **Ports**: 5560
* **Started by**: supervisord
* **Log File**: `/var/log/minard_dispatch_pull.log`
* **Description**: Reads events from a ZMQ push/pull socket, and writes info to a redis database.

redis
-----

* **Command**: `redis`
* **Ports**: 6379
* **Started by**: `/etc/init.d/redis_6379`
* **Log File**: `/var/log/redis.log`
* **Description**: redis database.

gunicorn
--------

* **Command**: `gunicorn -b 0.0.0.0:8080 minard:app --user=gunicorn`
* **Run as** : root (drops to gunicorn)
* **Ports**: 8080
* **Started by**: `/etc/init.d/gunicorn`
* **Log File**: `/var/log/gunicorn.log`
* **Description**: Gunicorn web server which serves the main site.

gunicorn (logging server)
-------------------------

* **Command**: `gunicorn -b 0.0.0.0:8081 snoplus_log:app --user=gunicorn`
* **Run as** : root (drops to gunicorn)
* **Ports**: 8081
* **Started by**: supervisord
* **Log File**: `/var/log/snoplus_log.log`
* **Description**: Gunicorn web server for logging.

nginx
-----

* **Command**: `nginx -c /etc/nginx/nginx.conf`
* **Run as** : root (drops to nginx)
* **Ports**: 50000
* **Started by**: `/etc/init.d/nginx`
* **Log File**: `/var/log/nginx.log`
* **Description**: nginx web server which serves static files and slow clients for the main site.

