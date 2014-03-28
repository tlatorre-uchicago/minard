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

Creating a Template
-------------------

The next step is to create a template so that we can return a real HTML page from our `hello_world` function. Create a file that looks like this::

    {% extends "layout.html" %}
    {% block title %}Hello World{% endblock %}
    {% block head %}
        {{ super() }}
    {% endblock %}
    {% block body %}
        {{ super() }}
        <h1>Hello World!</h1>
    {% endblock %}

and save it as `hello_world.html` in the `minard/templates` directory.

Now edit `views.py` again and change the `hello_world` function to look like this::

    @app.route('/hello_world')
    def hello_world():
        return render_template('hello_world.html')

Now, reinstall minard, and restart the web server and navigate to `http://localhost:5000/hello_world <http://localhost:5000/hello_world>`_ again, and you should see `Hello World` displayed below the navigation bar.

Adding a Histogram
------------------

Our page is pretty boring, so let's add a histogram! Edit `hello_world.html` to look like this::

    {% extends "layout.html" %}
    {% block title %}Hello World{% endblock %}
    {% block head %}
        {{ super() }}
        <link href="{{ url_for('static', filename='css/bar-chart.css') }}" rel="stylesheet">
        <script src="{{ url_for('static', filename='js/d3.js') }} />
        <script src="{{ url_for('static', filename='js/bar-chart.js') }} />
    {% endblock %}
    {% block body %}
        {{ super() }}
        <div class="container">
            <h1>Hello World!</h1>
            <div id="hist" />
        </div>
        <script>
            var chart = bar_chart().layout(d3.layout.histogram());

            setInterval(function() {
                $.getJSON($SCRIPT_ROOT + '/hello_world_hist', function(reply) {
                    d3.select('#hist').datum(reply.value).call(chart);
                });
            },1000);
        </script>
    {% endblock %}

Now we need to edit `views.py` again and add a function which will return the histogram data::

    import random

    @app.route('/hello_world_hist')
    def hello_world_hist():
        return jsonify(value=[random.gauss(0,1) for i in range(100)])

Reinstall minard, restart the web server and navigate to `http://localhost:5000/hello_world <http://localhost:5000/hello_world>`_, and you should see your beautiful histogram updating every second.
