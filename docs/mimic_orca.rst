Mimicking the ORCA Data Stream
==============================

To mimic the ORCA data stream, minard comes with a script that will push an ORCA file over a socket connection. To run it, you just need an ORCA run file, and then you can push it over a socket on port 44666 (the default ORCA port) by running the following commands::

    $ source [path/to/virtual-env]/bin/activate
    $ orca_server [path/to/orca/run/file]
