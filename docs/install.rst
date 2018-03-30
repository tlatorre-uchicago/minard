Installation
============

Installing minard
-----------------

The easiest way to install minard is to use a virtual environment with
`virtualenv <http://virtualenv.org>`_::

    $ virtualenv minard
    $ cd minard
    $ source bin/activate
    $ mkdir src
    $ cd src
    $ git clone https://github.com/snoplus/minard
    $ pip install ./minard

On Mac OSX you may need to add the following line to your bash_profile::

    export ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future

Installing Redis
----------------

To install redis, you can run these commands::

    $ curl -O http://download.redis.io/redis-stable.tar.gz
    $ tar -xzvf redis-stable.tar.gz
    $ cd redis-stable
    $ make
    $ sudo make install

You can now run the redis server with the `redis-server` command.

For more information on installing redis, and how to set it up to run as a
daemon see `redis quickstart <http://redis.io/topics/quickstart>`_.

Running the Web Server
----------------------

You should now be able to run the web server. After activating your virtual
environment, run::

    $ gunicorn -b 127.0.0.1:5000 minard:app

and navigate your web browser to `http://localhost:5000 <http://localhost:5000>`_.
