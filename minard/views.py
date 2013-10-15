from minard import app
from flask import render_template, jsonify

PROJECT_NAME = 'Minard'

@app.context_processor
def project_name():
    return {'project_name': PROJECT_NAME}

import random

@app.route('/get')
def get():
    return jsonify(values=[random.gauss(5,1) for i in range(100)])

@app.route('/')
def index():
    return render_template('layout.html',message='Hello World!')

sidebar=[{'href': '/', 'name': 'test', 'group': 'Hello'}]
nav = [{'href': '/', 'name': 'test'}]
containers = [{'name': 'Histogram %i' % i, 'type': 'histogram'} for i in range(2)]


@app.route('/fluid')
def fluid():
    return render_template('fluid.html',sidebar=sidebar,nav=nav,containers=containers)
