from minard import app
from flask import render_template

PROJECT_NAME = 'Minard'

@app.context_processor
def project_name():
    return {'project_name': PROJECT_NAME}

@app.route('/')
def index():
    return render_template('layout.html',message='Hello World!')

sidebar=[{'href': '/', 'name': 'test', 'group': 'Hello'}]
nav = [{'href': '/', 'name': 'test'}]
containers = [{'name': 'test'}]*4 + [{'name': 'histogram', 'type': 'histogram'}]


@app.route('/fluid')
def fluid():
    return render_template('fluid.html',sidebar=sidebar,nav=nav,containers=containers)
