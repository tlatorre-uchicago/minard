from minard import app
from flask import (render_template, jsonify, request, session, redirect,
    url_for, flash)
from flask.ext.login import (LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user)
import flask
import gevent
import gevent.monkey
gevent.monkey.patch_all()
from itertools import count
import datetime
from functools import wraps

PROJECT_NAME = 'Minard'

app.secret_key = 'secret'

@app.context_processor
def inject_user():
    return dict(userid=current_user.get_id())

class User(UserMixin):
    def __init__(self, username, password, edit=False):
	self.id = username
	self.password = password
        self.edit = edit

def edit_required(func):
    @wraps(func)
    @login_required
    def wrapped(*args, **kwargs):
        if current_user.edit:
            return func(*args, **kwargs)
        else:
            return login_manager.unauthorized()
    return wrapped

users = {'test': User('test','test')}

login_manager = LoginManager()

login_manager.init_app(app)

@login_manager.user_loader
def load_user(userid):
    return users[userid]

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/login', methods=['GET','POST'])
def login():
    error = None
    if request.method == 'POST':
	try:
	    user = load_user(request.form['username'])
	except KeyError:
	    error = 'Invalid username'
	else:
	    if request.form['password'] == user.password:
		login_user(user, remember=('remember' in request.form))
		flash('You were logged in.')
		return redirect(url_for('index'))
	    else:
		error = 'Invalid password'
    return render_template('login.html', error=error)

login_manager.login_view = 'login'

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
        data = jsonify(data=[random.gauss(0,1) for i in range(npoints)])
        #print data
        return data
    else:
        print 'returning latest'
        return jsonify(value=random.gauss(5,1))

@app.route('/get')
def get():
    name = request.args.get('name','',type=str)
    #print name
    if name == 'sphere':
        print 'returning id and values'
        id = []
        values = []
        for i in range(9000):
            id.append(i)#random.randint(0,9000))
            values.append(random.randint(0,10))
        return jsonify(id=id,values2=values)
    return jsonify(values=[random.gauss(5,1) for i in range(100)])

@app.route('/')
@login_required
def index():
    return render_template('fluid.html',sidebar=sidebar,nav=nav,containers=containers)

with open('/home/tlatorre/monitor/proj/pmt.js') as f:
    pmtinfo = json.load(f)

import math

# coords = []
# count = 0
# for x, y, z in zip(pmtinfo['x'],pmtinfo['y'],pmtinfo['z']):
#     r = math.sqrt(x**2 + y**2 + z**2)
#     if r <= 0:
#         count += 1
#         coords.append([0,0])
#         continue

#     t = math.acos(z/r)*180.0/math.pi - 90.0
#     p = math.atan2(y,x)*180.0/math.pi
#     coords.append([p,t]);

# print 'count = ', count

sidebar=[{'href': '/', 'name': 'test', 'group': 'Hello'}]
nav = [{'href': '/', 'name': 'test'}]
containers = [{'name': 'Histogram %i' % i, 'type': 'histogram', 'bins': random.choice([10,20,30])} for i in range(6)]

@app.route('/hero')
def hero():
    return render_template('hero.html')

@app.route('/time')
def time():
    return render_template('time.html')

@app.route('/alerts')
def alerts():
    try:
        edit = current_user.edit
    except AttributeError:
        edit = False
    return render_template('alerts.html', edit=edit)

alerts = []
for i in range(10):
    level = random.choice(['info','danger','warning','success'])
    alerts.append({'time':datetime.datetime.now().isoformat(),'level':level,'msg':'hello world %i ' % i})

@app.route('/dismiss', methods=['POST'])
@edit_required
def dismiss():
    dismiss = request.form['dismiss']

    print 'dismiss'
    for i in range(len(alerts)):
        if alerts[i]['time'] == dismiss:
            print 'deleting %i' % i
            del alerts[i]
            return jsonify(test='test')

@app.route('/stream')
def stream():
    last = request.args.get('last','',type=int)
    if last:
        npoints = request.args.get('npoints','',type=int)
        print 'returning %i points' % npoints
        data = jsonify(data=[random.gauss(0,1) for i in range(npoints)])
        #print data
        return data
    else:
        print 'returning alerts'
        level = random.choice(['info','danger','warning','success'])
        #alerts.append({'time':datetime.datetime.now().isoformat(),'level':level,'msg':'hello world 11'})
        #print alerts
        return jsonify(messages=alerts)

    #return flask.Response(event_stream(),mimetype='text/event-stream')
