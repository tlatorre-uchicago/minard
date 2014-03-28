Installation
============

The easiest way to install minard is to use a virtual environment with
`virtualenv <http://virtualenv.org>`_::

    $ virtualenv minard
    $ cd minard
    $ source bin/activate
    $ mkdir src
    $ cd src
    $ git clone https://github.com/tlatorre-uchicago/minard
    $ pip install ./minard

Installing Redis
----------------

To install redis, you can run these commands::

    $ cd $VIRTUAL_ENV/src
    $ curl -O http://download.redis.io/redis-stable.tar.gz
    $ tar -xzvf redis-stable.tar.gz
    $ cd redis-stable
    $ make
    $ ln src/redis-server $VIRTUAL_ENV/bin/redis-server

You can now run redis within your virtual environment by running `redis-server`.

For more information on installing redis, and how to set it up to run as a
daemon see `redis quickstart <http://redis.io/topics/quickstart>`_.

Running the Web Server
----------------------

You should now be able to run the web server. After activating your virtual
environment, run::

    $ gunicorn -b 0.0.0.0:50000 minard:app

and navigate your web browser to `http://localhost:50000 <http://localhost:50000>`_.
