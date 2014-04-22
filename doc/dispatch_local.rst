Dispatching Locally
===================

Installation
^^^^^^^^^^^^

Installing ratzdab
******************

Follow the instructions to `install RAT
<http://snopl.us/docs/rat/installation.html>`_. You can install ratzdab by
running the following commands::

    $ source [path/to/virtual-env]/bin/activate
    $ cd $VIRTUAL_ENV/src
    $ git clone git@github.com:tlatorre-uchicago/rat-tools.git
    $ cd rat-tools/ratzdab
    $ make
    $ echo "source $VIRTUAL_ENV/src/rat-tools/ratzdab/env.sh" >> $VIRTUAL_ENV/bin/activate

You can test that everything has worked by trying to import `ratzdab` in
python::

    $ python
    ...
    >>> import ratzdab
    RAT: Libraries loaded.

Installing the Dispatcher
*************************

::

    $ cd $VIRTUAL_ENV/src
    $ git clone git@github.com:tlatorre-uchicago/disp.git
    $ cd disp/src
    $ make

Installing the Redispatcher
***************************

The redispatcher is bundled with xsnoed. So we should install xsnoed::

    $ cd $VIRTUAL_ENV/src
    $ git clone git@github.com:snoplus/xsnoed.git
    $ cd xsnoed
    $ make

Testing
^^^^^^^

Now we can dispatch events from a zdab file::

    $ cd $VIRTUAL_ENV/src/disp/bin
    $ ./dispatch &
    $ cd $VIRTUAL_ENV/src/xsnoed
    $ ./redispatch -d 127.0.0.1 [path/to/zdab]/SNOP_0000006510_000.zdab

Now, we can read the events from python::

    $ source [/path/to/virtual-env]/bin/activate
    $ python
    Python 2.6.6 (r266:84292, Nov 21 2013, 12:39:37) 
    [GCC 4.4.7 20120313 (Red Hat 4.4.7-3)] on linux2
    Type "help", "copyright", "credits" or "license" for more information.
    >>> import ratzdab
    RAT: Libraries loaded.
    TClass::TClass:0: RuntimeWarning: no dictionary for class
    simple_ptr_nocopy<RAT::DBTable> is available
    >>> dispatch = ratzdab.dispatch('127.0.0.1')
    >>> o = dispatch.next(False)
    >>> ev = o.GetEV(0)
    >>> ev.eventID
    639783
