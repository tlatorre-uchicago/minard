Logging and Alarms
==================

Heartbeat
---------

Heartbeat signals should be sent as a POST request to `snopl.us/monitoring/heartbeat`
every five seconds with the name of the program and its status. For example::

    $ curl --data "name=builder&status=ok" -u snoplus snopl.us/monitoring/heartbeat

Logging
-------

Logging messages should be sent as a POST request to `snopl.us/monitoring/log`
with the name of the program, the level of the message, and the message. For
example::

    $ curl --data "name=builder&level=20&message=info" -u snoplus snopl.us/monitoring/log

An optional argument `notify` will cause the message to appear as an alert on
the monitoring page. For example::

    $ curl --data "name=builder&level=20&message=info&notify" -u snoplus snopl.us/monitoring/log

Alarm levels >= 40 will automatically trigger an alarm.

Logging Levels
^^^^^^^^^^^^^^

=====    ========     ================================================================================
Level    Name         Description
=====    ========     ================================================================================
10       Debug        Messages that the operator doesn't need to see, but may be useful for debugging.
20       Info         General information (e.g. new run).
21       Success      Notify the operator that something has successfully completed.
30       Warning      Alert the operator about something to look into.
40       Danger       Notify the operator of something that requires immediate attention.
=====    ========     ================================================================================


