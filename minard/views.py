from __future__ import division
from minard import app
from flask import render_template, jsonify, request, redirect, url_for
from minard.orca import total_seconds, redis
from sqlalchemy.sql import select
from minard.database import init_db, db_session
from minard.models import *
from datetime import datetime, timedelta
from itertools import product
import time
import calendar

def parse(timestr):
    dt = datetime.strptime(timestr,'%Y-%m-%dT%H:%M:%S.%fZ')
    return calendar.timegm(dt.timetuple())

init_db()

PROJECT_NAME = 'Minard'
DEBUG = True
SECRET_KEY = "=S\t3w>zKIVy0n]b1h,<%|@EHBgfRJQ;A\rLC'[\x0blPF!` ai}/4W"

app.config.from_object(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detector')
def hero():
    return render_template('detector.html')

@app.route('/daq/<name>')
def channels(name):
    if name == 'cmos':
        return render_template('channels.html',name=name, threshold=5000)
    elif name == 'base':
        return render_template('channels.html',name=name, threshold=80)

@app.route('/stream')
def stream():
    return render_template('stream.html')

@app.route('/alarms')
def alarms():
    return render_template('alarms.html')

@app.route('/builder')
def builder():
    return render_template('builder.html')

CHANNELS = [crate << 16 | card << 8 | channel \
            for crate, card, channel in product(range(19),range(16),range(32))]

@app.route('/query')
def query():
    name = request.args.get('name','',type=str)

    if name == 'tail_log':
        start = request.args.get('id',0,type=int)
        stop = int(redis.get('builder/global:next'))
        if start > stop:
            # server restart
            start = 0
        p = redis.pipeline()
        for i in range(start,stop):
            p.get('builder/uid:%i:msg' % i)
        value = map(lambda x: x if x is not None else '',p.execute())
        return jsonify(value=value,id=stop)

    if name == 'sphere':
    	latest = PMT.latest()
	id, charge_occupancy = zip(*db_session.query(PMT.pmtid, PMT.chargeocc)\
            .filter(PMT.id == latest.id).filter(PMT.chargeocc != 0).all())
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
        value = db_session.query(L2.entry_time, L2.events).order_by(L2.entry_time.desc())[:600]
        t, y = zip(*value)
        result = {'t': [x.isoformat() for x in t], 'y': y}
        return jsonify(value=result)

    if name == 'events_passed':
        value = db_session.query(L2.entry_time, L2.passed_events).order_by(L2.entry_time.desc())[:600]
        t, y = zip(*value)
        result = {'t': [x.isoformat() for x in t], 'y': y}
        return jsonify(value=result)

    if name == 'delta_t':
        value = db_session.query(L2).order_by(L2.entry_time.desc())[:600]
        result = {'t': [x.entry_time.isoformat() for x in value],
                  'y': [total_seconds(x.entry_time - x.get_clock()) for x in value]}
        return jsonify(value=result)

    if name == 'cmos' or name == 'base':
        p = redis.pipeline()
        for index in CHANNELS:
            p.get('%s/index:%i:value' % (name,index))
        values = p.execute()

        result = dict((i,int(v)) for i, v in zip(CHANNELS,values) if v is not None)

        return jsonify(value=result)

    if name == 'alarms':
        alarms = db_session.query(Alarms)
        return jsonify(messages=[dict(x) for x in alarms])

import sys

@app.route('/metric/')
def metric():
    expr = request.args.get('expr','',type=str)
    start = request.args.get('start','',type=str)
    stop = request.args.get('stop','',type=str)
    # convert ms -> sec
    step = request.args.get('step',None,type=int)//1000

    start = int(parse(start))
    stop = int(parse(stop))

    now = int(time.time())

    dt = stop - now
    start -= dt
    stop -= dt

    if step > 3600:
        t = 3600
    elif step > 60:
        t = 60
    else:
        t = 1

    if expr in ('gtid', 'run', 'subrun'):
        p = redis.pipeline()
        for i in range(start,stop,step):
            p.get('time/{0:d}/{1:d}/{2}'.format(t,i//t,expr))
        values = p.execute()
        return jsonify(values=values)

    try:
        trig, type = expr.split('-')
    except ValueError:
        trig = expr
        type = 'count'

    p = redis.pipeline()
    for i in range(start,stop,step):
        p.get('time/{0:d}/{1:d}/trigger:{2}:{3}'.format(t,i//t,trig,type))
    values = p.execute()

    if type != 'count':
        p = redis.pipeline()
        for i in range(start,stop,step):
            p.get('time/{0:d}/{1:d}/trigger:{2}:{3}'.format(t,i//t,trig,'count'))
        counts = p.execute()
        values = [float(a)/int(b) if a or b else 0 for a, b in zip(values,counts)]
    else:
        values = map(lambda x: int(x)/t if x else 0, values)

    return jsonify(values=values)

@app.route('/snostream')
def snostream():
    if not request.args.get('step'):
        return redirect(url_for('snostream',step=1,height=40,extent=400,_external=True))
    step = request.args.get('step',1,type=int)*1000
    height = request.args.get('height',40,type=int)
    extent = request.args.get('extent',400,type=int)
    return render_template('demo-stocks.html',step=step,height=height,extent=extent)
