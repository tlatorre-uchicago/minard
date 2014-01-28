from minard import app
from flask import (render_template, jsonify, request, redirect,
    url_for, flash)
from flask.ext.login import (LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user)
    
import datetime, random, json
from functools import wraps
#from database import get_charge_occupancy, PMT, get_number_of_events, get_number_of_passed_events, get_nhit, get_pos_hist, get_l2_info, get_alarms
from orca import cmos, base
from minard.database import init_db, db_session
from minard.models import *

init_db()

PROJECT_NAME = 'Minard'
DEBUG = True
SECRET_KEY = "=S\t3w>zKIVy0n]b1h,<%|@EHBgfRJQ;A\rLC'[\x0blPF!` ai}/4W"

app.config.from_object(__name__)

@app.context_processor
def inject_user():
    """Injects the current user into all templates"""
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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

users = {'snoplus': User('snoplus','snoplus',edit=True)}

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

@app.route('/query')
def query():
    name = request.args.get('name','',type=str)
    id = request.args.get('id',None,type=str)

    if name == 'sphere':
    	latest = PMT.latest()
	id, charge_occupancy = zip(*db_session.query(PMT.id, PMT.chargeocc)\
        .filter(PMT.id == latest.id).all())
        return jsonify(id=id, values2=charge_occupancy)

    if name == 'l2_info':
        if id is not None:
            info = db_session.query(L2).filter(L2.id == id).one()
        else:
            info = db_session.query(L2).order_by(L2.id.desc()).first()

        return jsonify(value=dict(info))

    if name == 'nhit':
        latest = Nhit.latest()
        hist = [getattr(latest,'nhit%i' % i) for i in range(30)]
        bins = range(5,300,10)
        result = dict(zip(bins,hist))
        return jsonify(value=result)

    if name == 'pos':
        latest = Position.latest()
        hist = [getattr(latest,'pos%i' % i) for i in range(13)]
        bins = range(25,650,50)
        result = dict(zip(bins,hist))
        return jsonify(value=result)

    if name == 'events':
        value = db_session.query(L2.entry_time, L2.events).order_by(L2.entry_time.desc())[:100]
        t, y = zip(*value)
        result = {'t': [x.isoformat() for x in t], 'y': y}
        return jsonify(value=result)

    if name == 'events_passed':
        value = db_session.query(L2.entry_time, L2.passed_events).order_by(L2.entry_time.desc())[:100]
        t, y = zip(*value)
        result = {'t': [x.isoformat() for x in t], 'y': y}
        return jsonify(value=result)

    if name == 'cmos':
        stats = request.args.get('stats','',type=str)

        if stats == 'avg':
            obj = cmos.avg
        elif stats == 'max':
            obj = cmos.max
        else:
            obj = cmos.now

        return jsonify(value=obj)

    if name == 'base':
        stats = request.args.get('stats','',type=str)

        if stats == 'avg':
            obj = base.avg
        elif stats == 'max':
            obj = base.max
        else:
            obj = base.now

        return jsonify(value=obj)

    if name == 'alerts':
        alarms = db_session.query(Alarms)
        return jsonify(messages=[dict(x) for x in alarms])

    return jsonify(value=[random.gauss(5,1) for i in range(100)])

@app.route('/')
def index():
    return render_template('fluid.html')

@app.route('/hero')
def hero():
    return render_template('hero.html')

@app.route('/daq/<name>')
def channels(name):
    print 'name = ', name
    return render_template('channels.html',name=name)

@app.route('/stream')
def stream():
    return render_template('stream.html')

@app.route('/alarms')
def alarms():
    try:
        edit = current_user.edit
    except AttributeError:
        edit = False
    return render_template('alerts.html', edit=edit)
