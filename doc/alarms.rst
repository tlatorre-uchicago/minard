Alarms
======

To issue an alarm, send a POST request to `snopl.us/monitoring/set_alarm`, with
the alarm level and message as the POST data. For example::

    $ curl --data "level=1&message=info" -u "username:password" snopl.us/monitoring/set_alarm

There are four levels of alarm.

=====    ========     ===================================================================
Level    Name         Description
=====    ========     ===================================================================
0        Success      Notify the operator that something has successfully completed.
1        Info         General information (e.g. new run).
2        Warning      Alert the operator about something to look into.
3        Danger       Notify the operator of something that requires immediate attention.
=====    ========     ===================================================================


