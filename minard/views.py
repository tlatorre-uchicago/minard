from minard import app
from flask import render_template, jsonify, request

PROJECT_NAME = 'Minard'

@app.context_processor
def project_name():
    return {'project_name': PROJECT_NAME}

import random
import json

@app.route('/timeseries')
def timeseries():
    name = request.args.get('name','',type=str)
    last = request.args.get('last','',type=int)
    if last:
        npoints = request.args.get('npoints','',type=int)
        print 'returning %i points' % npoints
        data = jsonify(data=[random.gauss(5,1) for i in range(npoints)])
        print data
        return data
    else:
        print 'returning latest'
        return jsonify(value=random.gauss(5,1))

@app.route('/get')
def get():
    name = request.args.get('name','',type=str)
    print name
    if name == 'sphere':
        print 'returning id and values'
        id = []
        values = []
        for i in range(100):
            id.append(random.randint(0,9000))
            values.append(random.randint(0,10))
        return jsonify(id=id,values2=values)
    return jsonify(values=[random.gauss(5,1) for i in range(100)])

@app.route('/')
def index():
    return render_template('layout.html',message='Hello World!')

with open('/home/tlatorre/monitor/proj/pmt.js') as f:
    pmtinfo = json.load(f)

import math

coords = []
count = 0
for x, y, z in zip(pmtinfo['x'],pmtinfo['y'],pmtinfo['z']):
    r = math.sqrt(x**2 + y**2 + z**2)
    if r <= 0:
        count += 1
        coords.append([0,0])
        continue

    t = math.acos(z/r)*180.0/math.pi - 90.0
    p = math.atan2(y,x)*180.0/math.pi
    coords.append([p,t]);

print 'count = ', count

sidebar=[{'href': '/', 'name': 'test', 'group': 'Hello'}]
nav = [{'href': '/', 'name': 'test'}]
containers = [{'name': 'Histogram %i' % i, 'type': 'histogram', 'bins': random.choice([10,20,30])} for i in range(1)]


@app.route('/fluid')
def fluid():
    return render_template('fluid.html',sidebar=sidebar,nav=nav,containers=containers,hero_unit={'name': 'test', 'type': 'sphere-projection', 'coords':json.dumps(coords)})

@app.route('/hero')
def hero():
    return render_template('hero.html')
