Dispatching Locally
===================

Installation
^^^^^^^^^^^^

Installing the Dispatcher
*************************

::

    $ cd $VIRTUAL_ENV/src
    $ git clone git@github.com:tlatorre-uchicago/disp.git
    $ cd disp
    $ make

To read events from the dispatch stream using the python module
`dispatch.py`, add the following line to your `.bashrc` or 
virtualenv `activate` script::

    export PYTHONPATH=[/path/to/disp]/python:$PYTHONPATH

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

    >>> import dispatch
    >>> d = dispatch.Dispatch('localhost')
    >>> event_record = d.next()
    >>> event_record.RunNumber
    6587L
    >>> event_record.NPmtHit
    28
    >>> event_record.TriggerCardData.BcGT # gtid
    2865675L
