Dispatching Locally
===================

Installation
^^^^^^^^^^^^

Installing the Dispatcher
*************************

::

    $ cd $VIRTUAL_ENV/src
    $ git clone git@github.com:snoplus/disp.git
    $ cd disp
    $ make

To read events from the dispatch stream using the python module
`dispatch.py`, add the following line to your `.bashrc` or 
virtualenv `activate` script::

    export PYTHONPATH=[/path/to/disp]/python:$PYTHONPATH
    export LD_LIBRARY_PATH=[/path/to/disp]/lib:$LD_LIBRARY_PATH

Installing the Redispatcher
***************************

The redispatcher is bundled with xsnoed. So we should install xsnoed::

    $ cd $VIRTUAL_ENV/src
    $ git clone git@github.com:snoplus/xsnoed.git
    $ cd xsnoed
    $ make redispatch

Testing
^^^^^^^

Now we can dispatch events from a zdab file::

    $ cd $VIRTUAL_ENV/src/disp/bin
    $ ./dispatch &
    $ cd $VIRTUAL_ENV/src/xsnoed
    $ ./redispatch -d 127.0.0.1 [path/to/zdab]/SNOP_0000006510_000.zdab

Now, we can read the events from python::

    >>> from dispatch import *
    >>> d = Dispatch('localhost')
    >>> record = d.recv()
    >>> id, record = unpack_header(record)
    >>> id == RECORD_IDS['PMT_RECORD']
    True
    >>> pmt_record_gen = unpack_pmt_record(record)
    >>> pmt_event_record = next(pmt_record_gen)
    >>> pmt_event_record.NPmtHit
    20
    >>> for uncal_pmt in pmt_record_gen:
    ...     print uncal_pmt.BoardID
    ... 
    11
    3

