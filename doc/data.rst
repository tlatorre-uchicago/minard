Data Sources
============

Dispatch Stream
---------------

The dispatch stream is processed by the `minard_dispatch
<https://github.com/tlatorre-uchicago/minard/blob/master/scripts/minard_dispatch>`_
script. The dispatch stream is read out using ratzdab, and written to the redis
database.

To see how to set up a local dispatcher see :doc:`dispatch_local`.

For more details on how the stream is processed see the :ref:`API
<dispatch-api>`.

Orca Stream
-----------

