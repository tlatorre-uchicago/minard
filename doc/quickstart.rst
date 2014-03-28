QuickStart
==========

Hello World
-----------

The simplest thing we can do is add a new url to the web app which returns a
string. Edit the file `views.py` in the minard source directory and add the
following function::

    @app.route('/hello_world')
    def hello_world():
        return 'Hello World!'

That's it! Now, just reinstall the minard package and restart the server::

    $ cd $VIRTUAL_ENV/src
    $ pip uninstall minard
    $ pip install ./minard
    $ gunicorn -b 127.0.0.1:5000 minard:app

and navigate your browser to `http://localhost:5000/hello_world <http://localhost:5000/hello_world>`_. To learn more about how this example worked see the `Flask Quickstart <http://flask.pocoo.org/docs/quickstart/>`_
