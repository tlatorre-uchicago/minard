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

