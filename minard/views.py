from minard import app
import datetime, random, json
from flask import render_template, jsonify, request, redirect, url_for 
from functools import wraps
from orca import cmos, base
from minard.database import init_db, db_session
from minard.models import *

init_db()

PROJECT_NAME = 'Minard'
DEBUG = True
SECRET_KEY = "=S\t3w>zKIVy0n]b1h,<%|@EHBgfRJQ;A\rLC'[\x0blPF!` ai}/4W"

app.config.from_object(__name__)

@app.route('/')
def index():
    return render_template('fluid.html')

@app.route('/hero')
def hero():
    return render_template('hero.html')

@app.route('/daq/<name>')
def channels(name):
    return render_template('channels.html',name=name)

@app.route('/stream')
def stream():
    return render_template('stream.html')

@app.route('/alarms')
def alarms():
    return render_template('alerts.html', edit=edit)

@app.route('/query')
def query():
    name = request.args.get('name','',type=str)

    if name == 'sphere':
    	latest = PMT.latest()
	id, charge_occupancy = zip(*db_session.query(PMT.id, PMT.chargeocc)\
            .filter(PMT.id == latest.id).all())
        return jsonify(id=id, values2=charge_occupancy)

    if name == 'l2_info':
        id = request.args.get('id',None,type=str)

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

    if name == 'delta_t':
        value = db_session.query(L2).order_by(L2.entry_time.desc())[:100]
        result = {'t': [x.entry_time.isoformat() for x in value],
                  'y': [(x.entry_time - x.get_clock()).total_seconds() for x in value]}
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
