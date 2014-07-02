Data Sources
============

Dispatch Stream
---------------

The dispatch stream is processed by the `minard_dispatch
<https://github.com/tlatorre-uchicago/minard/blob/master/scripts/minard_dispatch>`_
script and written to the redis database.

To run the dispatch processor as a daemon::

    $ source [/path/to/virtual-env]/bin/activate
    $ minard_dispatch --host [dispatcher ip]

To see how to set up a local dispatcher see :doc:`dispatch_local`.

Orca Stream
-----------

The ORCA stream is processed directly from a socket connection to ORCA. The
stream is processed by two scripts:

orca_producer
    This script receives the raw data from ORCA and pushes it to different
    sockets depending on the type of data. Currently it sends CMOS packets to
    port 5557 and base current packets to port 5558.

orca_consumer
    This script processes the data packets pushed by the `orca_producer` script.

For more information on the ORCA file formats see `Data File Format
<http://orca.physics.unc.edu/~markhowe/Data_Format_Viewing/Data_Format.html>`_.

To mimic the ORCA data stream see :doc:`mimic_orca`.

Builder Log
-----------

The `minard_builder` script monitors the builder log::

    $ source /opt/minard/bin/activate
    $ minard_builder [path/to/builder/ssh/key]
