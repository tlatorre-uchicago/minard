from minard import app
from flask import render_template

@app.route('/')
def index():
    return render_template('layout.html',message='Hello World!')

links=[{'href':'/', 'name': 'test', 'group': 'Hello'}]

@app.route('/fluid')
def fluid():
    return render_template('fluid.html',links=links)
