from minard import app
from flask import (render_template, jsonify, request, redirect,
    url_for, flash)
from flask.ext.login import (LoginManager, UserMixin, login_user,
    login_required, logout_user, current_user)
    
import datetime, random, json
from functools import wraps
from database import get_charge_occupancy, PMT, get_number_of_events, get_number_of_passed_events, get_nhit, get_pos_hist, get_l2_info, get_alarms
from orca import cmos, base

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
        id, charge_occupancy = get_charge_occupancy()
        id, charge_occupancy = \
            zip(*[(i, x) for i, x in zip(id, charge_occupancy)])# if x > 0])
        return jsonify(id=id, values2=charge_occupancy)

    if name == 'l2_info':
        return jsonify(value=get_l2_info(id=id))

    if name == 'nhit':
        return jsonify(value=get_nhit(id=id))

    if name == 'pos':
        return jsonify(value=get_pos_hist(id=id))

    if name == 'events':
        return jsonify(value=get_number_of_events())

    if name == 'events_passed':
        return jsonify(value=get_number_of_passed_events())

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
        return jsonify(messages=get_alarms())

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
